import os
import json
import time
import datetime
import tempfile
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing backend services
from company_profiler import profile_company, build_compliance_profile
from fetch_agent import fetch_latest_circulars, fetch_circular_text, LATEST_RBI_CIRCULARS
from parser_agent import parse_rbi_circular, extract_text_from_pdf_bytes, extract_text_from_pdf_file
from mapper_agent import index_company_profile, compare_regulation_with_profile
from action_agent import generate_compliance_alert, generate_quick_scan, generate_action_plan

from services.db_service import (
    save_company_profile, get_company_profile, save_compliance_report,
    save_global_matrix, get_global_matrix, save_diff_result, get_diff_history,
    save_agent_run, save_full_compliance_profile, get_saved_profiles,
    get_saved_profile_by_id, get_company_scan_history, delete_saved_profile,
    get_local_data, save_local_data
)
from services.diff_engine import compare_regulatory_documents
from services.report_generator import generate_pdf_report
from agents_pipeline import (
    run_multi_agent_pipeline, run_single_agent_by_id,
    normalize_company_type, ALLOWED_COMPANY_TYPES,
    run_company_research_agent, run_regulatory_discovery_agent,
    run_applicability_agent, run_compliance_analyst_agent,
    run_risk_agent, run_action_agent, run_report_agent
)

app = FastAPI(
    title="RegWatch API",
    description="Backend API powering RegWatch Regulatory Intelligence Platform",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class ScanRequest(BaseModel):
    company_name: str
    primary_country: str = "India"
    operating_countries: List[str] = ["India"]
    company_type: str = "Fintech"
    industry: str = "Payments"
    rbi_license: Optional[str] = ""

class AgentRerunRequest(BaseModel):
    profile_id: str
    agent_id: int

class DiffRequest(BaseModel):
    doc1_title: str
    doc1_text: str
    doc2_title: str
    doc2_text: str
    company_profile: Optional[Dict[str, Any]] = None

class ProfileUpdateRequest(BaseModel):
    profile_id: str
    company_name: str
    company_type: str
    industry: str
    primary_country: str
    operating_countries: List[str]
    rbi_license: Optional[str] = ""

# API Endpoints

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/api/saved_profiles")
def list_saved_profiles():
    """Retrieve all saved scan profiles sorted by date descending."""
    profiles = get_saved_profiles()
    return {"profiles": profiles}

@app.get("/api/saved_profiles/{profile_id}")
def get_profile(profile_id: str):
    """Retrieve details for a single saved scan profile."""
    profile = get_saved_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Saved profile not found")
    return profile

@app.delete("/api/saved_profiles/{profile_id}")
def delete_profile(profile_id: str):
    """Delete a saved scan profile by ID."""
    success = delete_saved_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found or already deleted")
    return {"success": True, "profile_id": profile_id}

@app.get("/api/circulars")
def list_circulars():
    """Get list of available RBI circulars for diff comparison."""
    circulars = fetch_latest_circulars(limit=12)
    return {"circulars": circulars}

@app.post("/api/scan")
def create_full_scan(req: ScanRequest):
    """Run full 7-agent pipeline synchronously and save results."""
    if not req.company_name or not req.company_name.strip():
        raise HTTPException(status_code=400, detail="Company name is required")
        
    company_name = req.company_name.strip()
    primary_country = req.primary_country or "India"
    operating_countries = list(set([primary_country] + [c for c in req.operating_countries if c]))
    
    existing_profile = {
        "company_name": company_name,
        "primary_country": primary_country,
        "operating_countries": operating_countries,
        "company_type": req.company_type,
        "industry": req.industry
    }
    
    agent_outputs = {}
    agent_states = []
    
    pipeline_gen = run_multi_agent_pipeline(
        company_name=company_name,
        primary_country=primary_country,
        operating_countries=operating_countries,
        existing_profile=existing_profile
    )
    
    for step in pipeline_gen:
        agent_id, status, stats, dur, sources, data = step
        agent_states.append({
            "agent_id": agent_id,
            "status": status,
            "stats": stats,
            "duration": dur,
            "sources": sources
        })
        if status == "COMPLETED" and data:
            if agent_id == 1: agent_outputs["profile"] = data
            elif agent_id == 2: agent_outputs["discovery"] = data
            elif agent_id == 3: agent_outputs["applicability"] = data
            elif agent_id == 4: agent_outputs["compliance"] = data
            elif agent_id == 5: agent_outputs["risk"] = data
            elif agent_id == 6: agent_outputs["action"] = data
            elif agent_id == 7: agent_outputs["report"] = data
        elif status == "FAILED":
            raise HTTPException(status_code=500, detail=f"Agent {agent_id} failed: {data}")
            
    profile_id = save_full_compliance_profile(
        company_profile=agent_outputs.get("profile", existing_profile),
        discovery_results=agent_outputs.get("discovery", {}),
        applicability_results=agent_outputs.get("applicability", {}),
        compliance_results=agent_outputs.get("compliance", {}),
        risk_results=agent_outputs.get("risk", {}),
        action_results=agent_outputs.get("action", {}),
        report_results=agent_outputs.get("report", {})
    )
    
    saved_record = get_saved_profile_by_id(profile_id)
    return {"success": True, "profile_id": profile_id, "data": saved_record}


@app.get("/api/scan/stream")
def stream_scan(company_name: str, primary_country: str = "India", operating_countries: str = "India", company_type: str = "Fintech", industry: str = "Payments"):
    """SSE Endpoint for live streaming the 7-agent pipeline execution."""
    countries_list = list(set([c.strip() for c in operating_countries.split(",") if c.strip()]))
    if primary_country not in countries_list:
        countries_list.insert(0, primary_country)
        
    existing_profile = {
        "company_name": company_name,
        "primary_country": primary_country,
        "operating_countries": countries_list,
        "company_type": company_type,
        "industry": industry
    }

    def event_generator():
        pipeline_gen = run_multi_agent_pipeline(
            company_name=company_name,
            primary_country=primary_country,
            operating_countries=countries_list,
            existing_profile=existing_profile
        )
        
        agent_outputs = {}
        for step in pipeline_gen:
            agent_id, status, stats, dur, sources, data = step
            
            if status == "COMPLETED" and data:
                if agent_id == 1: agent_outputs["profile"] = data
                elif agent_id == 2: agent_outputs["discovery"] = data
                elif agent_id == 3: agent_outputs["applicability"] = data
                elif agent_id == 4: agent_outputs["compliance"] = data
                elif agent_id == 5: agent_outputs["risk"] = data
                elif agent_id == 6: agent_outputs["action"] = data
                elif agent_id == 7: agent_outputs["report"] = data

            event_payload = {
                "agent_id": agent_id,
                "status": status,
                "stats": stats,
                "duration": dur,
                "sources": sources,
                "data_preview": data if status == "COMPLETED" and isinstance(data, dict) else None
            }
            yield f"data: {json.dumps(event_payload)}\n\n"

        # Finalize & Save
        profile_id = save_full_compliance_profile(
            company_profile=agent_outputs.get("profile", existing_profile),
            discovery_results=agent_outputs.get("discovery", {}),
            applicability_results=agent_outputs.get("applicability", {}),
            compliance_results=agent_outputs.get("compliance", {}),
            risk_results=agent_outputs.get("risk", {}),
            action_results=agent_outputs.get("action", {}),
            report_results=agent_outputs.get("report", {})
        )
        saved_record = get_saved_profile_by_id(profile_id)
        yield f"data: {json.dumps({'event': 'DONE', 'profile_id': profile_id, 'saved_record': saved_record})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/agent/rerun")
def rerun_agent(req: AgentRerunRequest):
    """Re-run a single agent for an existing profile and update saved DB record."""
    record = get_saved_profile_by_id(req.profile_id)
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    pipeline_state = {
        "profile": record.get("company_profile", {}),
        "discovery": record.get("discovery_results", {}),
        "applicability": record.get("applicability_results", {}),
        "compliance": record.get("compliance_results", {}),
        "risks": record.get("risk_results", {}),
        "actions": record.get("action_results", {}),
        "report": record.get("report_results", {})
    }
    
    try:
        stats, dur, sources, result_data = run_single_agent_by_id(req.agent_id, pipeline_state)
        
        # Update state
        if req.agent_id == 1: record["company_profile"] = result_data
        elif req.agent_id == 2: record["discovery_results"] = result_data
        elif req.agent_id == 3: record["applicability_results"] = result_data
        elif req.agent_id == 4: record["compliance_results"] = result_data
        elif req.agent_id == 5: record["risk_results"] = result_data
        elif req.agent_id == 6: record["action_results"] = result_data
        elif req.agent_id == 7: record["report_results"] = result_data
        
        # Update DB file
        local_db = get_local_data()
        for idx, p in enumerate(local_db.get("saved_profiles", [])):
            if p.get("profile_id") == req.profile_id:
                local_db["saved_profiles"][idx] = record
                break
        save_local_data(local_db)
        
        return {
            "success": True,
            "agent_id": req.agent_id,
            "stats": stats,
            "duration": dur,
            "result_data": result_data,
            "updated_record": record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent rerun failed: {str(e)}")


class PDFParseRequest(BaseModel):
    filename: Optional[str] = "Uploaded Document.pdf"
    pdf_base64: str

@app.post("/api/parse_pdf")
def parse_pdf_endpoint(req: PDFParseRequest):
    """Extract plain text from base64 encoded PDF payload using pypdf."""
    import base64
    try:
        pdf_bytes = base64.b64decode(req.pdf_base64)
        extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
        if not extracted_text:
            return {"success": False, "error": "Unable to extract readable text from PDF."}
        return {"success": True, "text": extracted_text, "filename": req.filename}
    except Exception as e:
        return {"success": False, "error": f"PDF extraction failed: {str(e)}"}

@app.post("/api/diff")
def run_diff(req: DiffRequest):
    """Execute regulatory diff between two document texts."""
    doc1_title = req.doc1_title or "Document A"
    doc2_title = req.doc2_title or "Document B"
    
    doc1_text = req.doc1_text or ""
    doc2_text = req.doc2_text or ""

    print(f"[DIFF DIAGNOSTIC] Doc A: '{doc1_title}' | Chars: {len(doc1_text)} | Status: {'SUCCESS' if len(doc1_text) >= 20 else 'FAILED'}")
    print(f"[DIFF DIAGNOSTIC] Doc B: '{doc2_title}' | Chars: {len(doc2_text)} | Status: {'SUCCESS' if len(doc2_text) >= 20 else 'FAILED'}")
    
    diff_res = compare_regulatory_documents(
        old_text=doc1_text,
        new_text=doc2_text,
        company_profile=req.company_profile,
        doc1_title=doc1_title,
        doc2_title=doc2_title
    )
    save_diff_result(doc1_title, doc2_title, diff_res)
    return {"success": True, "diff": diff_res}


@app.post("/api/profile/update")
def update_profile(req: ProfileUpdateRequest):
    """Update company metadata for a saved scan profile."""
    record = get_saved_profile_by_id(req.profile_id)
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    c_prof = record.get("company_profile", {})
    c_prof["company_name"] = req.company_name
    c_prof["company_type"] = req.company_type
    c_prof["industry"] = req.industry
    c_prof["primary_country"] = req.primary_country
    c_prof["operating_countries"] = req.operating_countries
    if req.rbi_license:
        c_prof["rbi_license"] = req.rbi_license

    record["company_name"] = req.company_name
    record["company_type"] = req.company_type
    record["industry"] = req.industry
    record["primary_country"] = req.primary_country
    record["operating_countries"] = req.operating_countries

    local_db = get_local_data()
    for idx, p in enumerate(local_db.get("saved_profiles", [])):
        if p.get("profile_id") == req.profile_id:
            local_db["saved_profiles"][idx] = record
            break
    save_local_data(local_db)
    return {"success": True, "updated_record": record}


@app.get("/api/pdf/{profile_id}")
def download_pdf(profile_id: str):
    """Generate and return PDF compliance report for a saved profile."""
    record = get_saved_profile_by_id(profile_id)
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"RegWatch_Compliance_Report_{profile_id}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    generate_pdf_report(
        company_profile=record.get("company_profile", {}),
        discovery_results=record.get("discovery_results", {}),
        compliance_results=record.get("compliance_results", {}),
        risk_results=record.get("risk_results", {}),
        action_results=record.get("action_results", {}),
        output_path=pdf_path
    )
    
    return FileResponse(
        path=pdf_path,
        filename=pdf_filename,
        media_type="application/pdf"
    )

# Serve static web frontend
if os.path.exists("index.html"):
    @app.get("/", response_class=HTMLResponse)
    def read_root():
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
