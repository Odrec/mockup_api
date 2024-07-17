from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = "1234"
ALGORITHM = "HS256"


def create_jwt_token(username: str, name: str, course_id: str, role: str):
    to_encode = {
        "sub": username,
        "name": name,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),  # Token valid for 30 seconds
        "context": course_id,
        "context-role": role
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


token = create_jwt_token("jdoe", "John Doe", "course-123", "learner")
print(token)
