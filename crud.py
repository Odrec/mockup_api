from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas

GLOBAL_SCOPES = [
    schemas.QuotaScope.user,
    schemas.QuotaScope.course,
    schemas.QuotaScope.total
]

COURSE_SCOPES = [
    schemas.QuotaScope.course,
    schemas.QuotaScope.course_user,
]


# CRUD für QuotaDefinition
def get_quota_definitions(db: Session) -> list[models.QuotaDefinition]:
    return db.query(models.QuotaDefinition).all()


# CRUD für Quota
def get_global_quotas(db: Session) -> list[models.Quota]:
    return db.query(models.Quota).filter(
        models.Quota.scope.in_(GLOBAL_SCOPES),
        models.Quota.user_id == None,
        models.Quota.course_id == None
    ).all()


def check_quota_defintion(db: Session, quota: schemas.QuotaUpdate) -> models.QuotaDefinition:
    quota_definition = db.query(models.QuotaDefinition).filter(
        models.QuotaDefinition.scope == quota.scope,
        models.QuotaDefinition.feature == quota.feature
    ).first()

    if not quota_definition:
        raise HTTPException(
            status_code=404,
            detail=f"QuotaDefinition with scope={quota.scope} and feature={quota.feature} not found"
        )

    return quota_definition


def update_or_create_global_quota(db: Session, global_quota: schemas.QuotaUpdate) -> models.Quota:
    if global_quota.scope not in GLOBAL_SCOPES:
        print(global_quota.scope)
        raise HTTPException(status_code=400, detail="Supported global scopes: " + ', '.join([s.value for s in GLOBAL_SCOPES]))

    # Check if the quota definition exists
    quota_definition = check_quota_defintion(db, global_quota)

    db_quota = db.query(models.Quota).filter(
        models.Quota.scope == global_quota.scope,
        models.Quota.feature == global_quota.feature,
        models.Quota.user_id == None,
        models.Quota.course_id == None
    ).first()

    if db_quota:
        # Update
        db_quota.limit = global_quota.limit
    else:
        # Create
        db_quota = models.Quota(
            limit=global_quota.limit,
            scope=global_quota.scope,
            feature=global_quota.feature,
            type=quota_definition.type,  # TODO: Do we need to store the type in each quota
            quota_definition_id=quota_definition.id  # use the ID of the quota definition
        )
        db.add(db_quota)

    db.commit()
    db.refresh(db_quota)
    return db_quota


def get_course_quotas(db: Session, course_id: str) -> list[models.Quota]:
    return db.query(models.Quota).filter(
        models.Quota.scope.in_(COURSE_SCOPES),
        models.Quota.course_id == course_id,
        models.Quota.user_id == None
    ).all()


def update_or_create_course_quota(db: Session, course_id: str, course_quota: schemas.QuotaUpdate) -> models.Quota:
    if course_quota.scope not in COURSE_SCOPES:
        raise HTTPException(status_code=400, detail="Supported course scopes: " + ', '.join([s.value for s in COURSE_SCOPES]))

    # Check if the quota definition exists
    quota_definition = check_quota_defintion(db, course_quota)

    db_quota = db.query(models.Quota).filter(
        models.Quota.scope == course_quota.scope,
        models.Quota.feature == course_quota.feature,
        models.Quota.course_id == course_id,
        models.Quota.user_id == None
    ).first()

    if db_quota:
        # Update
        db_quota.limit = course_quota.limit
    else:
        # Create
        db_quota = models.Quota(
            limit=course_quota.limit,
            scope=course_quota.scope,
            feature=course_quota.feature,
            course_id=course_id,
            type=quota_definition.type,  # TODO: Do we need to store the type in each quota
            quota_definition_id=quota_definition.id  # use the ID of the quota definition
        )
        db.add(db_quota)

    db.commit()
    db.refresh(db_quota)
    return db_quota


def get_course_member_quotas(db: Session, course_id: str) -> list[models.Quota]:
    return db.query(models.Quota).filter(
        models.Quota.scope == schemas.QuotaScope.course_user,
        models.Quota.course_id == course_id,
        models.Quota.user_id != None
    ).all()


def get_course_member_quota(db: Session, course_id: str, user_id: str) -> models.Quota:
    quota = db.query(models.Quota).filter(
        models.Quota.scope == schemas.QuotaScope.course_user,
        models.Quota.course_id == course_id,
        models.Quota.user_id == user_id
    ).first()

    if not quota:
        raise HTTPException(
            status_code=404,
            detail=f"User quota with scope=course-user not found"
        )

    return quota
