from sqlalchemy.orm import Session

from models import QuotaDefinition, Quota
from schemas import ResetIntervalDefinition, QuotaScope


def seed_data(db: Session):
    # Check whether data already exists to avoid duplicate entries
    if db.query(QuotaDefinition).first() or db.query(Quota).first():
        return

    # Creating mock data for QuotaDefinition
    quota_definitions = [
        QuotaDefinition(
            type='token',
            description={
                "en": "Token limit for users",
                "de": "Tokenlimit für Nutzende"
            },
            reset_interval=ResetIntervalDefinition.daily,
            scope=QuotaScope.user,
        ),
        QuotaDefinition(
            type='token',
            description={
                "en": "Token limit for gpt-3 users",
                "de": "Tokenlimit für gpt-3 Nutzende"
            },
            reset_interval=ResetIntervalDefinition.monthly,
            scope=QuotaScope.user,
            feature='gpt-3',
        ),
        QuotaDefinition(
            type='number',
            description={
                "en": "Number of total images to generate",
                "de": "Gesamtzahl zu generierender Bilder"
            },
            reset_interval=ResetIntervalDefinition.daily,
            scope=QuotaScope.total,
        ),
        QuotaDefinition(
            type='token',
            description={
                "en": "Token limit for course user",
                "de": "Tokenlimit für Kursmitglieder"
            },
            reset_interval=ResetIntervalDefinition.semester,
            scope=QuotaScope.course_user,
        ),

        QuotaDefinition(
            type='token',
            description={
                "en": "Token limit for courses",
                "de": "Tokenlimit für Kurse"
            },
            reset_interval=ResetIntervalDefinition.semester,
            scope=QuotaScope.course,
        ),
    ]

    # Adding QuotaDefinition mock data to the session
    db.add_all(quota_definitions)
    db.flush()  # ensures that IDs are generated for foreign key assignments

    # Create mock data for quota
    quotas = [
        Quota(
            limit=1000,
            type='token',
            scope=QuotaScope.user,
            quota_definition_id=quota_definitions[0].id  # refers to the actual ID of the QuotaDefinition entry
        ),
        Quota(
            limit=1000,
            used=200,
            type='token',
            scope=QuotaScope.user,
            user_id='user-456',
            quota_definition_id=quota_definitions[0].id  # refers to the actual ID of the QuotaDefinition entry
        ),

        Quota(
            limit=1000,
            type='token',
            scope=QuotaScope.user,
            feature='gpt-3',
            quota_definition_id=quota_definitions[1].id  # refers to the actual ID of the QuotaDefinition entry
        ),
        Quota(
            limit=1000,
            used=100,
            type='token',
            scope=QuotaScope.user,
            feature='gpt-3',
            user_id='user-456',
            quota_definition_id=quota_definitions[1].id  # refers to the actual ID of the QuotaDefinition entry
        ),

        Quota(
            limit=500,
            used=50,
            type='number',
            scope=QuotaScope.total,
            quota_definition_id=quota_definitions[2].id  # refers to the actual ID of the QuotaDefinition entry
        ),

        Quota(
            limit=500,
            type='token',
            scope=QuotaScope.course_user,
            quota_definition_id=quota_definitions[3].id  # refers to the actual ID of the QuotaDefinition entry
        ),
        Quota(
            limit=100,
            type='token',
            scope=QuotaScope.course_user,
            course_id="course-123",
            quota_definition_id=quota_definitions[3].id  # refers to the actual ID of the QuotaDefinition entry
        ),
        Quota(
            limit=100,
            used=200,
            type='token',
            scope=QuotaScope.course_user,
            course_id="course-123",
            user_id="user-456",
            quota_definition_id=quota_definitions[3].id  # refers to the actual ID of the QuotaDefinition entry
        ),

        Quota(
            limit=200,
            type='token',
            scope=QuotaScope.course,
            quota_definition_id=quota_definitions[4].id  # refers to the actual ID of the QuotaDefinition entry
        ),
    ]

    # Adding quota mock data to the session
    db.add_all(quotas)
    db.commit()
