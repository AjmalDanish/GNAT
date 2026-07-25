# Global Network Anomaly Tracker (GNAT)

# Synthetic Data Engine Design

Version: 1.0

Status:
Approved

Module:
Graph Data Generation

Primary Owner:
Data Engineering Layer

Dependencies

Python

Pandas

NumPy

NetworkX

Faker

GeoPy

PostgreSQL

---

# 1. Purpose

The Synthetic Data Engine is responsible for creating realistic global network communication data that simulates internet traffic between cities around the world.

This data becomes the training dataset for the Graph Neural Network.

The generated data should mimic realistic communication behavior while also allowing controlled anomaly injection.

---

# 2. Objectives

The engine shall

✔ Load real world cities

✔ Generate realistic communication

✔ Support multiple protocols

✔ Generate graph-ready datasets

✔ Inject anomalies

✔ Validate data

✔ Store metadata

✔ Export multiple formats

---

# 3. Data Sources

Primary Dataset

SimpleMaps World Cities

Alternative

GeoNames

Natural Earth

OpenStreetMap

Required Fields

City

Country

Latitude

Longitude

Population

Timezone

ISO Code

Continent

---

# 4. Dataset Pipeline

World Cities CSV

↓

Validation

↓

Cleaning

↓

Normalization

↓

City Repository

↓

Traffic Generator

↓

Anomaly Injector

↓

Graph Builder

↓

Feature Generator

↓

Dataset Export

↓

Database

---

# 5. Pipeline Modules

city_loader

Responsibilities

Load CSV

Validate columns

Remove duplicates

Normalize names

Return DataFrame

---

city_validator

Responsibilities

Validate

Latitude

Longitude

Country

Population

Timezone

---

city_repository

Responsibilities

Cache city data

Query by country

Query by continent

Random city selection

Population weighted sampling

---

traffic_generator

Responsibilities

Generate synthetic communication

Support

Random traffic

Business traffic

Regional traffic

International traffic

High-volume hubs

Night traffic

Peak traffic

---

anomaly_generator

Responsibilities

Inject

Botnets

DDoS

Spam

Closed communication loops

Traffic spikes

Bandwidth abuse

Impossible latency

Compromised nodes

---

dataset_exporter

Responsibilities

CSV

JSON

Parquet

PostgreSQL

---

dataset_metadata

Responsibilities

Dataset Version

Creation Date

Configuration

Random Seed

Statistics

Checksum

---

# 6. Communication Model

Each transaction includes

Transaction ID

Timestamp

Source City

Destination City

Protocol

Packet Count

Packet Size

Bandwidth

Latency

Duration

Connection Type

Encryption

Risk Label

---

# 7. Supported Protocols

HTTP

HTTPS

SSH

FTP

SMTP

DNS

TCP

UDP

ICMP

MQTT

WebSocket

Each protocol has configurable probability.

---

# 8. Traffic Types

Normal

Business

Cloud

Government

Financial

Academic

Streaming

Gaming

IoT

VPN

Dark Web (Synthetic)

---

# 9. Node Features

Each city stores

Population

Connections

Incoming Traffic

Outgoing Traffic

Average Latency

Average Bandwidth

Degree

Pagerank

Betweenness

Closeness

Eigenvector

Risk Score

Country

Continent

---

# 10. Edge Features

Bandwidth

Latency

Traffic Volume

Protocol

Frequency

Connection Duration

Packet Count

Encryption

Weight

Timestamp

---

# 11. Graph Properties

Directed Graph

Weighted Graph

Connected Components

Strongly Connected Components

Average Degree

Density

Diameter

Average Path Length

Clustering Coefficient

---

# 12. Synthetic Traffic Rules

Large cities communicate more frequently.

Nearby cities communicate more frequently.

Countries share regional traffic.

Financial hubs produce larger traffic.

Internet hubs produce many connections.

Weekdays produce more business traffic.

Night hours reduce activity.

---

# 13. Anomaly Injection

Supported anomaly classes

Class 1

Traffic Spike

Sudden increase

Class 2

Botnet

Many infected nodes

Class 3

Closed Loop

Nodes communicate only internally

Class 4

Impossible Latency

Unrealistic communication delay

Class 5

Bandwidth Abuse

Extremely high bandwidth

Class 6

Beaconing

Regular suspicious intervals

Class 7

Data Exfiltration

Large outbound transfers

Class 8

Distributed Attack

Many nodes attack one target

---

# 14. Dataset Configuration

Configurable Parameters

Number of Cities

Number of Transactions

Anomaly Percentage

Random Seed

Time Window

Protocols

Countries

Traffic Pattern

Maximum Connections

Minimum Connections

Output Format

---

# 15. Dataset Validation

Verify

No missing coordinates

Unique IDs

Valid timestamps

Positive packet counts

Positive bandwidth

Positive latency

Valid countries

Connected graph

Duplicate detection

---

# 16. Feature Engineering

Generate

Node Degree

Weighted Degree

Pagerank

Betweenness

Closeness

Eigenvector

Community ID

Average Bandwidth

Average Latency

Risk Features

Temporal Features

Normalize numerical features before training.

---

# 17. Performance Strategy

Use

Vectorized Pandas operations

NumPy random generators

Batch inserts

Memory-efficient processing

Chunked exports

Parallel feature computation where applicable

---

# 18. Output Files

cities.csv

transactions.csv

nodes.csv

edges.csv

graph_metrics.csv

dataset_metadata.json

training_dataset.pt

---

# 19. Database Storage

Persist

Dataset

Transactions

Graph

Nodes

Edges

Metadata

Statistics

Generation Logs

---

# 20. Logging

Log

Dataset loading

Cleaning

Generation progress

Validation

Anomaly injection

Export

Execution time

Errors

---

# 21. Testing

Unit Tests

CSV Loading

Validation

Traffic Generation

Anomaly Injection

Export

Integration Tests

Complete pipeline

Performance Tests

100k transactions

500k transactions

1M transactions

---

# 22. Success Criteria

The engine is complete when

✔ World city data loads successfully

✔ Synthetic traffic is realistic

✔ Anomalies are injected correctly

✔ Graph is fully connected where expected

✔ Features are generated

✔ Dataset exports successfully

✔ Database stores all records

✔ Performance is acceptable

✔ Unit tests pass

✔ Documentation is complete

---

# Future Enhancements

Real ISP topology

ASN simulation

BGP routing

Satellite links

Temporal graph generation

Live data ingestion

Streaming pipeline

Kafka integration

Cloud-scale generation

Synthetic malware families

---

# GLM-4.7 Instructions

When implementing this module:

1. Build each component independently.
2. Use configuration files instead of hardcoded values.
3. Include logging and validation.
4. Write comprehensive unit tests.
5. Generate production-ready code only.
6. Explain every design decision before generating code.
7. Wait for approval after each component.

End of Synthetic Data Engine Design