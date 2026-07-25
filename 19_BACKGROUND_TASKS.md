# Global Network Anomaly Tracker (GNAT)

# Background Tasks Design

Version: 1.0

Status:
Approved

Module:
Background Processing

Framework:
Celery

Message Broker:
Redis

Task Scheduler:
Celery Beat

---

# 1. Purpose

The Background Tasks module executes long-running operations asynchronously.

It improves application responsiveness by moving resource-intensive operations outside the HTTP request lifecycle.

---

# 2. Objectives

The background processing system shall

✔ Execute long-running tasks

✔ Queue jobs

✔ Retry failed tasks

✔ Schedule recurring jobs

✔ Track task status

✔ Log task execution

✔ Support task cancellation

---

# 3. Architecture

User Request

↓

Django View

↓

Service Layer

↓

Celery Task

↓

Redis Queue

↓

Celery Worker

↓

Database

↓

Notify User

---

# 4. Task Categories

Dataset Processing

Graph Generation

Model Training

AI Inference

Report Generation

Notification Delivery

Cleanup Jobs

Scheduled Maintenance

---

# 5. Dataset Processing Task

Responsibilities

Validate uploaded files

Clean dataset

Store metadata

Create processing logs

Update dataset status

---

# 6. Graph Generation Task

Responsibilities

Load transactions

Generate graph

Compute metrics

Generate node features

Generate edge features

Store graph

---

# 7. Model Training Task

Responsibilities

Load dataset

Initialize model

Train model

Validate model

Save checkpoints

Export trained model

Store metrics

---

# 8. Prediction Task

Responsibilities

Load trained model

Run inference

Calculate risk scores

Store predictions

Update dashboard statistics

---

# 9. Report Generation Task

Responsibilities

Collect data

Generate charts

Generate report

Export PDF

Store report

Notify user

---

# 10. Notification Task

Responsibilities

Create notification

Store notification

Deliver notification

Mark delivery status

Support future email integration

---

# 11. Scheduled Tasks

Run using Celery Beat

Daily Cleanup

Old Log Cleanup

Temporary File Cleanup

Database Health Check

Prediction Statistics Update

Dashboard Cache Refresh

---

# 12. Task Status

Possible states

Pending

Queued

Running

Completed

Failed

Cancelled

Retrying

---

# 13. Retry Policy

Retry

Temporary Database Errors

Redis Connection Errors

File Access Errors

Maximum Retries

3

Retry Delay

60 Seconds

Permanent failures must not retry indefinitely.

---

# 14. Task Priority

High

Prediction

Notifications

Medium

Graph Generation

Dataset Processing

Low

Cleanup

Report Generation

Priority must be configurable.

---

# 15. Monitoring

Track

Task ID

Task Name

Start Time

End Time

Execution Time

Status

Retries

Error Message

Worker Name

---

# 16. Logging

Log

Task Started

Task Completed

Task Failed

Retry Attempt

Execution Time

Warnings

Errors

---

# 17. Error Handling

Handle

Redis Unavailable

Worker Offline

Database Failure

File Not Found

Model Missing

Unexpected Exceptions

Log all failures and update task status.

---

# 18. Configuration

Store configuration in

.env

Celery Settings

Redis Settings

Task Timeouts

Retry Count

Queue Names

Worker Concurrency

Beat Schedule

---

# 19. Security

Validate task inputs

Restrict privileged tasks

Protect Redis access

Avoid executing arbitrary user input

Log administrative task execution

---

# 20. Performance

Use

Multiple Workers

Dedicated Queues

Batch Processing

Database Transactions

Connection Pooling

Efficient Memory Usage

---

# 21. Testing

Unit Tests

Task Execution

Retry Logic

Task Status Updates

Configuration

Integration Tests

Celery Worker

Redis Queue

Database Updates

Performance Tests

Large Dataset Processing

Concurrent Task Execution

---

# 22. Success Criteria

The background processing module is complete when

✔ Tasks execute asynchronously

✔ Queue processing works

✔ Retries function correctly

✔ Scheduled tasks execute

✔ Task status updates correctly

✔ Logging is complete

✔ Performance is acceptable

✔ Tests pass

✔ Documentation complete

---

# Future Improvements

Distributed Workers

RabbitMQ Support

Priority Queue Optimization

Auto Scaling Workers

Task Chaining

Task Groups

Task Monitoring Dashboard

Email Notifications

Slack Notifications

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Configure Celery

2.

Configure Redis

3.

Create Task Base Class

4.

Implement Dataset Processing Task

5.

Implement Graph Generation Task

6.

Implement Model Training Task

7.

Implement Prediction Task

8.

Implement Report Generation Task

9.

Implement Notification Task

10.

Configure Celery Beat

11.

Unit Tests

12.

Documentation

Generate production-ready code only.

Use shared tasks where appropriate.

Keep business logic inside service classes.

Implement retries with exponential backoff where suitable.

Include structured logging, type hints, and docstrings.

Wait for approval after completing each component.

End of Background Tasks Design