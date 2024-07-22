import os
import logging
from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from sqlalchemy.orm import Session

import crud
import models
from schemas import QuotaGet, QuotaUpdate, Metadata
from database import engine, SessionLocal, get_db
from seed import seed_data
from utils import verify_token, verify_api_key

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

models.Base.metadata.create_all(bind=engine)

with SessionLocal() as session:
    # Create mock data
    seed_data(session)

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint to access the tool (simulates JWT token validation and session creation)
@app.post("/", response_class=HTMLResponse)
async def access_tool(token: str = Form()):
    logging.debug(f"Token received for tool access: {token}")
    user = verify_token(token)
    return f"""
    <html>
        <head>
            <title>KIWI-Tool</title>
        </head>
        <body>
            <h1>Welcome to the tool, {user['name']}!</h1>
        </body>
    </html>
    """


# Endpoint to get metadata (API Key protected)
@app.get("/metadata", response_model=Metadata, dependencies=[Depends(verify_api_key)])
async def get_metadata(db: Session = Depends(get_db)):
    base_url = os.getenv("HOST_URL")  # Read the environment variable for host URL
    quota_definitions_objects = crud.get_quota_definitions(db)

    quota_definitions = []
    for quota_definition in quota_definitions_objects:
        quota_definitions.append({
            "type": quota_definition.type,
            "description": quota_definition.description,
            "reset_interval": quota_definition.reset_interval,
            "scope": quota_definition.scope,
            "feature": quota_definition.feature,
        })

    return {
        "tool_url": f"{base_url}",
        "quota_url": f"{base_url}/api/quota",
        "image_url": f"{base_url}/static/tool.png",
        "description": {
            "de-DE": "Beschreibung für ein Test-Tool",
            "en-GB": "Description for a test tool"
        },
        "title": {
            "de-DE": "Titel des Test-Tools",
            "en-GB": "Test Tool Title"
        },
        "supported_quotas": quota_definitions
    }


# Helper function to ensure quotas have all fields
def validate_quota(quota: models.Quota):
    return {
        "limit": quota.limit,
        "used": quota.used,
        "type": quota.type,
        "scope": quota.scope,
        "feature": quota.feature,
        "user_id": quota.user_id
    }


# Endpoint to get quotas (API Key protected)
@app.get("/quota", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_quotas(db: Session = Depends(get_db)):
    quotas = crud.get_global_quotas(db)
    validated_quotas = [validate_quota(q) for q in quotas]
    return validated_quotas


# Endpoint to update quotas (API Key protected)
@app.put("/quota", dependencies=[Depends(verify_api_key)])
async def put_quotas(quotas: List[QuotaUpdate], db: Session = Depends(get_db)):
    # Update passed quotas
    for quota in quotas:
        crud.update_or_create_global_quota(db, quota)

    global_quotas = crud.get_global_quotas(db)
    validated_quotas = [validate_quota(q) for q in global_quotas]
    return validated_quotas


# Endpoint to get quota for a specific course with user quotas option (API Key protected)
@app.get("/quota/course/{course_id}", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_quota(course_id: str, db: Session = Depends(get_db)):
    quotas = crud.get_course_quotas(db, course_id)
    validated_quotas = [validate_quota(q) for q in quotas]
    return validated_quotas


# Endpoint to update quota for a course and course members (API Key protected)
@app.put("/quota/course/{course_id}", dependencies=[Depends(verify_api_key)])
async def put_course_quota(course_id: str, quotas: List[QuotaUpdate], db: Session = Depends(get_db)):
    for quota in quotas:
        crud.update_or_create_course_quota(db, course_id, quota)

    course_quotas = crud.get_course_quotas(db, course_id)
    validated_quotas = [validate_quota(q) for q in course_quotas]
    return validated_quotas


# Endpoint to get quota for all course members (API Key protected)
@app.get("/quota/course/{course_id}/user", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_member_quotas(course_id: str, db: Session = Depends(get_db)):
    quotas = crud.get_course_quotas(db, course_id)
    validated_quotas = [validate_quota(q) for q in quotas]
    return validated_quotas


# Endpoint to get quota for a specific course member (API Key protected)
@app.get("/quota/course/{course_id}/user/{user_id}", response_model=QuotaGet, dependencies=[Depends(verify_api_key)])
async def get_course_member_quota(course_id: str, user_id: str, db: Session = Depends(get_db)):
    quota = crud.get_course_member_quota(db, course_id, user_id)
    return validate_quota(quota)
