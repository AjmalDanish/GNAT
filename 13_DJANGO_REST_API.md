# Global Network Anomaly Tracker (GNAT)

# Django REST API Design

Version: 1.0

Status:
Approved

Module:
REST API

Framework:
Django REST Framework (DRF)

API Version:
v1

Response Format:
JSON

---

# 1. Purpose

The REST API provides a secure and standardized interface between the frontend, AI engine, and backend services.

All client applications must communicate through these APIs.

---

# 2. Objectives

The API shall

✔ Support CRUD operations

✔ Authenticate users

✔ Upload datasets

✔ Trigger graph generation

✔ Trigger AI inference

✔ Retrieve dashboard statistics

✔ Generate reports

✔ Return standardized responses

---

# 3. Base URL

/api/v1/

Example

/api/v1/auth/login/

/api/v1/datasets/

/api/v1/predictions/

---

# 4. Authentication APIs

POST

/auth/login/

Authenticate user

POST

/auth/logout/

Logout user

POST

/auth/password/change/

Change password

GET

/auth/profile/

Current user profile

PUT

/auth/profile/

Update profile

---

# 5. Dataset APIs

GET

/datasets/

List datasets

POST

/datasets/

Upload dataset

GET

/datasets/{id}/

Dataset details

PUT

/datasets/{id}/

Update dataset

DELETE

/datasets/{id}/

Delete dataset

POST

/datasets/{id}/process/

Generate graph

---

# 6. Graph APIs

GET

/graphs/

List graphs

GET

/graphs/{id}/

Graph details

GET

/graphs/{id}/metrics/

Graph metrics

GET

/graphs/{id}/nodes/

Node list

GET

/graphs/{id}/edges/

Edge list

---

# 7. AI Training APIs

POST

/training/start/

Start model training

GET

/training/status/

Training status

GET

/training/history/

Training history

GET

/training/models/

Available models

---

# 8. Prediction APIs

POST

/predictions/run/

Run inference

GET

/predictions/

Prediction history

GET

/predictions/{id}/

Prediction details

DELETE

/predictions/{id}/

Delete prediction

---

# 9. Dashboard APIs

GET

/dashboard/summary/

Dashboard overview

GET

/dashboard/charts/

Chart data

GET

/dashboard/activity/

Recent activity

GET

/dashboard/statistics/

System statistics

---

# 10. Reports APIs

GET

/reports/

List reports

POST

/reports/generate/

Generate report

GET

/reports/{id}/download/

Download report

DELETE

/reports/{id}/

Delete report

---

# 11. Notification APIs

GET

/notifications/

List notifications

PUT

/notifications/{id}/read/

Mark as read

DELETE

/notifications/{id}/

Delete notification

---

# 12. Standard Success Response

{
    "success": true,
    "message": "Operation completed successfully.",
    "data": {}
}

---

# 13. Standard Error Response

{
    "success": false,
    "message": "Validation failed.",
    "errors": {}
}

---

# 14. HTTP Status Codes

200 OK

201 Created

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

500 Internal Server Error

---

# 15. Pagination

Default Page Size

20

Maximum

100

Parameters

page

page_size

---

# 16. Filtering

Support

Search

Ordering

Date Range

Risk Level

Country

Prediction Status

Dataset

---

# 17. Sorting

Ascending

Descending

Supported Fields

Created Date

Updated Date

Risk Score

Training Date

Prediction Date

---

# 18. Permissions

Administrator

Full Access

Analyst

Upload datasets

Generate graphs

Run predictions

Generate reports

Viewer

Read-only access

---

# 19. Validation Rules

Validate

Required fields

File type

Maximum upload size

Duplicate datasets

Invalid IDs

Authentication

Authorization

---

# 20. Rate Limiting

Authentication APIs

10 requests/minute

Prediction APIs

30 requests/minute

Dataset Upload

10 requests/hour

Configurable through DRF settings.

---

# 21. Security

HTTPS

CSRF Protection

Input Validation

SQL Injection Protection

XSS Protection

Permission Classes

Authentication Middleware

---

# 22. API Documentation

Generate documentation using

OpenAPI

Swagger UI

ReDoc

Include

Endpoint description

Parameters

Example requests

Example responses

Error responses

Authentication requirements

---

# 23. Logging

Log

API request

API response

Execution time

Authenticated user

Errors

Warnings

---

# 24. Testing

Unit Tests

Serializer Tests

Permission Tests

View Tests

Integration Tests

Authentication

Dataset APIs

Prediction APIs

Dashboard APIs

Performance Tests

---

# 25. Success Criteria

The API module is complete when

✔ Authentication APIs work

✔ Dataset APIs work

✔ Graph APIs work

✔ Training APIs work

✔ Prediction APIs work

✔ Dashboard APIs work

✔ Reports APIs work

✔ Notifications APIs work

✔ Documentation generated

✔ Tests pass

---

# Future Improvements

JWT Authentication

OAuth2

API Versioning (v2)

GraphQL Support

WebSocket APIs

Bulk Operations

API Analytics

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Configure Django REST Framework

2.

Create Serializers

3.

Create ViewSets

4.

Configure URL Routing

5.

Implement Permissions

6.

Implement Filtering & Pagination

7.

Generate OpenAPI Documentation

8.

Write Unit Tests

9.

Generate API Documentation

Generate production-ready code only.

Use ViewSets where appropriate.

Keep business logic inside services.

Use serializers for validation.

Include logging, type hints, and docstrings.

Wait for approval after each component.

End of Django REST API Design