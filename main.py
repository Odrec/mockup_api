import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from typing import List
from schemas import QuotaGet, QuotaUpdate, Metadata
from database import get_all_quotas, update_quotas
from utils import verify_token, verify_api_key

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()


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
async def get_metadata():
    base_url = os.getenv("HOST_URL")  # Read the environment variable for host URL
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
        "supported_quotas": [
            {
                "type": "token",
                "description": {
                    "de-DE": "Token Beispiel",
                    "en-GB": "Token example"
                },
                "reset_interval": "daily",
                "scope": "total"
            }
        ]
    }


# Helper function to ensure quotas have all fields
def validate_quota(quota):
    valid_scopes = {"user", "course", "course-user", "total"}
    scope = quota.get("scope")
    if scope not in valid_scopes:
        raise ValueError(f"Invalid scope value: {scope}. Expected one of {valid_scopes}")

    return {
        "limit": quota.get("limit"),
        "used": quota.get("used", None),
        "type": quota.get("type", "token"),  # Default type to "token" if missing
        "scope": scope,
        "feature": quota.get("feature", None),
        "user_id": quota.get("user_id", None)
    }


# Endpoint to get quotas (API Key protected)
@app.get("/quota", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_quotas():
    try:
        quotas = get_all_quotas()
        validated_quotas = [validate_quota(q) for q in quotas]
        return validated_quotas
    except ValueError as e:
        logging.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))


# Endpoint to update quotas (API Key protected)
@app.put("/quota", dependencies=[Depends(verify_api_key)])
async def put_quotas(quotas: List[QuotaUpdate]):
    all_quotas = get_all_quotas()
    for quota in quotas:
        quota_dict = quota.dict()
        quota_dict["used"] = 0  # Initialize used to 0 for new quotas
        quota_dict["type"] = quota_dict.get("type", "token")  # Default type
        all_quotas.append(quota_dict)
    update_quotas(all_quotas)
    return {"message": "Quotas updated successfully"}


# Endpoint to get quota for a specific course with user quotas option (API Key protected)
@app.get("/quota/course/{course_id}", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_quota(course_id: str, with_user_quotas: bool = Query(default=False)):
    quotas = get_all_quotas()
    course_quotas = [validate_quota(q) for q in quotas if
                     q['scope'] in ['course', 'course-user'] and q.get('course_id') == course_id]
    if not course_quotas:
        raise HTTPException(status_code=404, detail="Course quota not found")
    if with_user_quotas:
        user_quotas = [validate_quota(q) for q in quotas if
                       q['scope'] == 'course-user' and q.get('course_id') == course_id]
        course_quotas.extend(user_quotas)
    return course_quotas


# Endpoint to update quota for a course and course members (API Key protected)
@app.put("/quota/course/{course_id}", dependencies=[Depends(verify_api_key)])
async def put_course_quota(course_id: str, quotas: List[QuotaUpdate]):
    all_quotas = get_all_quotas()
    for quota in quotas:
        quota_dict = quota.dict()
        quota_dict['course_id'] = course_id
        updated = False
        for idx, q in enumerate(all_quotas):
            if q['scope'] == quota_dict['scope'] and q.get('course_id') == course_id:
                all_quotas[idx] = quota_dict
                updated = True
                break
        if not updated:
            all_quotas.append(quota_dict)
    update_quotas(all_quotas)
    return {"message": "Course quotas updated successfully"}


# Endpoint to get quota for all course members (API Key protected)
@app.get("/quota/course/{course_id}/user", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_users_quota(course_id: str):
    quotas = get_all_quotas()
    user_quotas = [validate_quota(q) for q in quotas if q['scope'] == 'course-user' and q.get('course_id') == course_id]
    return user_quotas


# Endpoint to get quota for a specific course member (API Key protected)
@app.get("/quota/course/{course_id}/user/{user_id}", response_model=QuotaGet, dependencies=[Depends(verify_api_key)])
async def get_course_user_quota(course_id: str, user_id: str):
    quotas = get_all_quotas()
    for quota in quotas:
        if quota['scope'] == 'course-user' and quota.get('course_id') == course_id and quota.get('user_id') == user_id:
            return validate_quota(quota)
    raise HTTPException(status_code=404, detail="Course user quota not found")
