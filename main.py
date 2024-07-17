from fastapi import FastAPI, Depends, HTTPException
from typing import List
from schemas import QuotaGet, QuotaUpdate, Metadata
from database import get_all_quotas, update_quotas
from utils import verify_api_key

app = FastAPI()


# Endpoint to get metadata
@app.get("/metadata", response_model=Metadata, dependencies=[Depends(verify_api_key)])
async def get_metadata():
    return {
        "tool_url": "https://tool.example.com",
        "quota_url": "https://tool.example.com/api/quota",
        "image_url": "https://tool.example.com/image.png",
        "description": {"en": "This is an AI tool"},
        "title": {"en": "AI Toolbox"},
        "supported_quotas": [
            {
                "type": "token",
                "description": {"en": "Token quota"},
                "reset_interval": "monthly",
                "scope": "total",
                "feature": None
            },
            {
                "type": "time",
                "description": {"en": "Time quota"},
                "reset_interval": "monthly",
                "scope": "user",
                "feature": None
            }
        ]
    }


# Helper function to ensure quotas have all fields
def validate_quota(quota):
    return {
        "limit": quota.get("limit"),
        "used": quota.get("used", 0),
        "type": quota.get("type", "token"),  # Default type to "token" if missing
        "scope": quota.get("scope"),
        "feature": quota.get("feature", None),
        "user_id": quota.get("user_id", None)
    }


# Endpoint to get quotas
@app.get("/quota", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_quotas():
    quotas = get_all_quotas()
    validated_quotas = [validate_quota(q) for q in quotas]
    return validated_quotas


# Endpoint to update quotas
@app.put("/quota", dependencies=[Depends(verify_api_key)])
async def put_quotas(quotas: List[QuotaUpdate]):
    all_quotas = get_all_quotas()
    updated_quotas = [
        {"limit": q.limit, "used": 0, "type": "token", "scope": q.scope, "feature": q.feature, "user_id": q.user_id} for
        q in quotas]
    all_quotas.extend(updated_quotas)
    update_quotas(all_quotas)
    return {"message": "Quotas updated successfully"}


# Endpoint to get quota for a specific course with user quotas option
@app.get("/quota/course/{course_id}", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_quota(course_id: str, with_user_quotas: bool = False):
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


# Endpoint to update quota for a course and course members
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


# Endpoint to get quota for all course members
@app.get("/quota/course/{course_id}/user", response_model=List[QuotaGet], dependencies=[Depends(verify_api_key)])
async def get_course_users_quota(course_id: str):
    quotas = get_all_quotas()
    user_quotas = [validate_quota(q) for q in quotas if q['scope'] == 'course-user' and q.get('course_id') == course_id]
    if not user_quotas:
        raise HTTPException(status_code=404, detail="Course user quotas not found")
    return user_quotas


# Endpoint to get quota for a specific course member
@app.get("/quota/course/{course_id}/user/{user_id}", response_model=QuotaGet, dependencies=[Depends(verify_api_key)])
async def get_course_user_quota(course_id: str, user_id: str):
    quotas = get_all_quotas()
    for quota in quotas:
        if quota['scope'] == 'course-user' and quota.get('course_id') == course_id and quota.get('user_id') == user_id:
            return validate_quota(quota)
    raise HTTPException(status_code=404, detail="Course user quota not found")


# Endpoint to update quota for a specific course member
@app.put("/quota/course/{course_id}/user/{user_id}", dependencies=[Depends(verify_api_key)])
async def put_course_user_quota(course_id: str, user_id: str, quota: QuotaUpdate):
    quotas = get_all_quotas()
    quota_dict = quota.dict()
    quota_dict['course_id'] = course_id
    quota_dict['user_id'] = user_id
    quota_dict['used'] = 0
    quota_dict['type'] = "token"
    quota_updated = False
    for idx, q in enumerate(quotas):
        if q['scope'] == 'course-user' and q.get('course_id') == course_id and q.get('user_id') == user_id:
            quotas[idx] = quota_dict
            quota_updated = True
            break
    if not quota_updated:
        quotas.append(quota_dict)
    update_quotas(quotas)
    return {"message": "Course user quota updated successfully"}
