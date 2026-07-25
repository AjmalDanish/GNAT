# Global Network Anomaly Tracker (GNAT)

# AI Inference Engine

Version: 1.0

Status:
Approved

Module:
AI Inference Engine

Primary Framework:
PyTorch Geometric

Dependencies

PyTorch

PyTorch Geometric

NetworkX

NumPy

Pandas

Django

---

# 1. Purpose

The AI Inference Engine is responsible for loading trained Graph Neural Network models and generating anomaly predictions on graph datasets.

It acts as the bridge between the trained AI model and the Django application.

---

# 2. Objectives

The inference engine shall

✔ Load trained models

✔ Validate input graphs

✔ Perform inference

✔ Calculate node risk scores

✔ Classify anomalies

✔ Store prediction history

✔ Return results to APIs

✔ Support batch inference

---

# 3. Inference Workflow

Load Model

↓

Load Graph Dataset

↓

Validate Features

↓

Move Model to Device

↓

Forward Pass

↓

Generate Risk Scores

↓

Classify Nodes

↓

Store Predictions

↓

Return Results

---

# 4. Inputs

Required

Graph Dataset

Node Features

Edge Index

Optional

Edge Attributes

Metadata

Model Version

---

# 5. Outputs

For Every Node

Node ID

City

Risk Score

Prediction

Confidence

Community

Timestamp

Summary

Total Nodes

Normal Nodes

Anomalous Nodes

Average Risk

Highest Risk Node

Execution Time

---

# 6. Risk Score

Output Range

0.0 → 1.0

Categories

0.00 – 0.30

Low Risk

0.31 – 0.60

Medium Risk

0.61 – 0.80

High Risk

0.81 – 1.00

Critical Risk

These thresholds must be configurable.

---

# 7. Model Loading

Support

Latest Model

Specific Version

Best Checkpoint

Validate

Model Exists

Version Exists

Compatible Architecture

---

# 8. Prediction Modes

Single Graph

Batch Graphs

Historical Dataset

Future

Streaming Inference

---

# 9. Prediction Storage

Store

Prediction ID

Dataset ID

Model Version

Execution Time

Average Risk

Maximum Risk

Created By

Created At

Node Predictions

---

# 10. Performance

Support

CPU Inference

GPU Inference

Batch Prediction

Memory Efficient Loading

Lazy Loading

---

# 11. Error Handling

Handle

Model Not Found

Dataset Missing

Invalid Features

Version Mismatch

Prediction Failure

GPU Failure

Every error must be logged.

---

# 12. Logging

Log

Model Loaded

Inference Started

Inference Completed

Prediction Count

Execution Time

Errors

Warnings

---

# 13. Configuration

Configuration File

Inference Device

Batch Size

Thresholds

Model Directory

Prediction Directory

Logging Level

Maximum Concurrent Predictions

---

# 14. API Integration

Expose Service Methods

load_model()

predict()

predict_batch()

calculate_risk()

save_predictions()

get_prediction_history()

These methods will be consumed by

Django Views

REST APIs

Dashboard

---

# 15. Response Format

Prediction Response

Prediction ID

Model Version

Dataset Version

Execution Time

Summary

Node Predictions

Statistics

Return JSON-compatible objects.

---

# 16. Visualization Support

Provide data for

World Map

Risk Heatmap

Node Colors

Edge Colors

Statistics

Charts

No visualization logic belongs inside this module.

---

# 17. Unit Tests

Test

Model Loading

Prediction

Batch Prediction

Risk Calculation

Storage

History Retrieval

Configuration

---

# 18. Output Files

predictions.csv

prediction_summary.json

risk_scores.csv

execution_log.txt

prediction_history.json

---

# 19. Success Criteria

The module is complete when

✔ Model loads correctly

✔ Predictions execute successfully

✔ Risk scores generated

✔ Prediction history stored

✔ Dashboard receives data

✔ APIs return valid responses

✔ Tests pass

✔ Documentation complete

---

# Future Improvements

Real-time Streaming

Multiple Model Selection

Model Ensemble

Explainable AI

Confidence Calibration

Auto Retry

Prediction Caching

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Inference Service

2.

Model Loader

3.

Prediction Engine

4.

Risk Score Calculator

5.

Prediction Repository

6.

Prediction History Service

7.

Unit Tests

8.

Documentation

Generate production-ready code.

Include logging.

Use type hints.

Use configuration files.

Separate business logic from Django views.

Wait for approval after completing each component.

End of AI Inference Engine