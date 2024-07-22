# Running the service

```uvicorn main:app --reload```

# Simulate tool authentication

1. Generate JWT token

```python test_jwt.py```

2. Authenticate

```curl -X POST "http://127.0.0.1:8000/" -H "Content-Type: application/x-www-form-urlencoded" -d "token=YOUR_JWT_TOKEN"```

# Testing with curl
1. Get Metadata

```curl -X GET "http://127.0.0.1:8000/metadata" -H "Authorization: Bearer mysecureapikey"```

2. Get Quotas

```curl -X GET "http://127.0.0.1:8000/quota" -H "Authorization: Bearer mysecureapikey"```

3. Update Quotas

```
curl -X PUT "http://127.0.0.1:8000/quota" -H "Authorization: Bearer mysecureapikey" -H "Content-Type: application/json" -d '
[
    {
        "limit": 100,
        "scope": "total"
    },
    {
        "limit": 100,
        "scope": "user"
    },
    {
        "limit": 500,
        "scope": "user",
        "feature": "gpt-3"
    }
]'
```

4. Get Course Quota

```curl -X GET "http://127.0.0.1:8000/quota/course/course-123" -H "Authorization: Bearer mysecureapikey"```

5. Update Course Quota

```
curl -X PUT "http://127.0.0.1:8000/quota/course/course-123" -H "Authorization: Bearer mysecureapikey" -H "Content-Type: application/json" -d '
[
    {
        "limit": 100,
        "scope": "course"
    },
    {
        "limit": 10,
        "scope": "course-user"
    }
]'
```

6. Get Quota for All Course Members

```curl -X GET "http://127.0.0.1:8000/quota/course/course-123/user" -H "Authorization: Bearer mysecureapikey"```

7. Get Quota for a Specific Course Member

```curl -X GET "http://127.0.0.1:8000/quota/course/course-123/user/user-456" -H "Authorization: Bearer mysecureapikey"```