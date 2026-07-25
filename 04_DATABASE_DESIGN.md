# Global Network Anomaly Tracker (GNAT)

# Database Design Document

Version: 1.0

Status: Approved

Database Engine:
PostgreSQL 16+

ORM:
Django ORM

Migration Tool:
Django Migrations

---

# 1. Purpose

This document defines the complete database architecture for GNAT.

The database must support

• Authentication

• Synthetic Dataset Management

• Graph Metadata

• AI Models

• Training Runs

• Prediction History

• User Activity

• System Logs

• Reports

The design follows Third Normal Form (3NF).

---

# 2. Database Principles

The database shall

• Avoid duplicate data

• Support indexing

• Support auditing

• Store historical records

• Support future scaling

• Use UUID primary keys where appropriate

• Maintain referential integrity

---

# 3. Database Overview

Database Name

gnat_db

Schema

public

Character Encoding

UTF-8

Timezone

UTC

---

# 4. Core Tables

Authentication

accounts_user

accounts_profile

----------------------------

Synthetic Data

country

city

dataset

transaction

----------------------------

Graph

graph

graph_node

graph_edge

graph_metric

----------------------------

Artificial Intelligence

ml_model

training_run

model_checkpoint

prediction

prediction_node

----------------------------

Analytics

analysis

report

dashboard_snapshot

----------------------------

System

audit_log

system_log

notification

---

# 5. Entity Relationship Overview

User

↓

Dataset

↓

Transactions

↓

Graph

↓

Nodes

↓

Edges

↓

Features

↓

Model

↓

Prediction

↓

Dashboard

---

# 6. Table Specifications

--------------------------------

accounts_user

--------------------------------

Purpose

Application users

Columns

id

UUID

Primary Key

username

Unique

email

Unique

password

Hashed

first_name

last_name

is_active

is_staff

date_joined

last_login

Indexes

email

username

---

accounts_profile

Purpose

Additional user information

Columns

id

user_id

Role

Avatar

Organization

Country

Created At

Updated At

---

country

Purpose

Store countries

Columns

id

ISO Code

Country Name

Continent

Latitude

Longitude

Indexes

Country Name

---

city

Purpose

Store world cities

Columns

id

country_id

City Name

Latitude

Longitude

Population

Timezone

Indexes

country_id

city_name

---

dataset

Purpose

Synthetic dataset metadata

Columns

id

Dataset Name

Description

Source

Version

Created By

Created At

Status

Record Count

Indexes

Version

Status

---

transaction

Purpose

Synthetic network traffic

Columns

id

dataset_id

source_city

destination_city

packet_count

latency

bandwidth

protocol

timestamp

is_anomaly

Indexes

dataset_id

timestamp

source_city

destination_city

---

graph

Purpose

Graph metadata

Columns

id

dataset_id

total_nodes

total_edges

density

created_at

---

graph_node

Purpose

Nodes inside graph

Columns

id

graph_id

city_id

degree

pagerank

betweenness

closeness

eigenvector

risk_score

Indexes

graph_id

risk_score

---

graph_edge

Purpose

Graph edges

Columns

id

graph_id

source_node

destination_node

weight

traffic_volume

is_anomaly

Indexes

graph_id

source_node

destination_node

---

graph_metric

Purpose

Store graph statistics

Columns

id

graph_id

metric_name

metric_value

created_at

---

ml_model

Purpose

Registered AI models

Columns

id

Model Name

Architecture

Framework

Version

Accuracy

Precision

Recall

F1 Score

Created At

Is Active

---

training_run

Purpose

Training history

Columns

id

model_id

epochs

learning_rate

batch_size

optimizer

loss

accuracy

training_time

gpu_used

completed_at

---

model_checkpoint

Purpose

Saved model files

Columns

id

training_run

checkpoint_path

best_accuracy

created_at

---

prediction

Purpose

Prediction session

Columns

id

dataset

model

executed_by

prediction_time

average_risk

total_anomalies

execution_time

---

prediction_node

Purpose

Individual node prediction

Columns

id

prediction

graph_node

risk_score

classification

confidence

---

analysis

Purpose

Historical analysis

Columns

id

prediction

summary

recommendation

status

generated_at

---

report

Purpose

Generated reports

Columns

id

analysis

report_name

file_path

format

generated_at

---

dashboard_snapshot

Purpose

Historical dashboard statistics

Columns

id

total_nodes

total_edges

average_risk

highest_risk_city

generated_at

---

audit_log

Purpose

Track every user action

Columns

id

user

action

ip_address

browser

timestamp

---

system_log

Purpose

Application logs

Columns

id

level

message

module

created_at

---

notification

Purpose

System notifications

Columns

id

title

message

priority

is_read

created_at

---

# 7. Relationships

User

1:N

Datasets

Dataset

1:N

Transactions

Dataset

1:1

Graph

Graph

1:N

Nodes

Graph

1:N

Edges

Model

1:N

Training Runs

Training Run

1:N

Checkpoints

Prediction

1:N

Prediction Nodes

Prediction

1:1

Analysis

Analysis

1:N

Reports

---

# 8. Indexing Strategy

Create indexes on

Email

Username

Dataset Version

Timestamp

Risk Score

Prediction Time

Country

City

Graph ID

Foreign Keys

Composite Indexes

(graph_id, risk_score)

(dataset_id, timestamp)

(source_city, destination_city)

(model_id, created_at)

---

# 9. Constraints

Email must be unique

Username must be unique

Risk score between

0.0

and

1.0

Packet count > 0

Bandwidth > 0

Latency >= 0

---

# 10. Soft Delete Strategy

Never permanently delete

Datasets

Predictions

Reports

Models

Use

is_deleted

deleted_at

deleted_by

---

# 11. Audit Strategy

Log

Login

Logout

Dataset Upload

Training

Prediction

Export

Admin Actions

API Calls

---

# 12. Backup Strategy

Daily Backup

Weekly Full Backup

Monthly Archive

Point-in-Time Recovery Enabled

---

# 13. Performance Strategy

Use

Database Indexes

Pagination

select_related()

prefetch_related()

Bulk Inserts

Bulk Updates

Connection Pooling

Caching

---

# 14. Security

Encrypt passwords

Never store plaintext passwords

Validate every input

Prevent SQL Injection

Use ORM only

Environment Variables

Least Privilege Access

---

# 15. Future Database Enhancements

Neo4j Integration

TimescaleDB

Graph Database Synchronization

Vector Database

Redis Cache

Multi-region Replication

Partitioning

---

# Database Success Criteria

The database must

✔ Handle millions of synthetic transactions

✔ Support historical AI analysis

✔ Enable dashboard analytics

✔ Support secure authentication

✔ Scale without redesign

✔ Remain fully normalized

✔ Support future Graph Database integration

End of Database Design Document.