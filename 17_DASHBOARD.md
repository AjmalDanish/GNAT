# Global Network Anomaly Tracker (GNAT)

# Dashboard Design

Version: 1.0

Status:
Approved

Module:
Dashboard

Framework:
Django Templates

Visualization:
Plotly

---

# 1. Purpose

The Dashboard is the primary landing page of GNAT.

It provides users with an overview of datasets, graph analytics, AI predictions, system status, and recent activities in a single interface.

---

# 2. Objectives

The dashboard shall

✔ Display system overview

✔ Show AI prediction summary

✔ Display graph statistics

✔ Monitor datasets

✔ Provide quick actions

✔ Display interactive charts

✔ Show recent activity

✔ Refresh dynamically

---

# 3. Dashboard Layout

Top Navigation

↓

Sidebar

↓

KPI Cards

↓

Interactive Charts

↓

World Visualization

↓

Recent Activity

↓

System Status

↓

Footer

---

# 4. KPI Cards

Display

Total Datasets

Total Graphs

Total Nodes

Total Edges

Total Predictions

Average Risk Score

Active Users

Latest Model Version

Each card should include

Title

Value

Small icon

Last updated timestamp

---

# 5. Quick Actions

Provide buttons for

Upload Dataset

Generate Graph

Train Model

Run Prediction

Generate Report

Refresh Dashboard

---

# 6. Dataset Overview

Display

Dataset Name

Version

Upload Date

Status

Node Count

Edge Count

Prediction Status

Actions

View

Delete

Process

---

# 7. Graph Statistics

Display

Number of Nodes

Number of Edges

Average Degree

Graph Density

Connected Components

Communities

Average Latency

Average Bandwidth

---

# 8. AI Prediction Summary

Display

Total Predictions

Normal Nodes

Anomalous Nodes

Average Risk

Highest Risk City

Prediction Time

Current Model

---

# 9. Interactive Charts

Charts

Risk Distribution

Traffic Volume by Country

Prediction Trend

Top Risk Cities

Protocol Distribution

Community Distribution

Daily Activity

Use Plotly for all visualizations.

---

# 10. World Map Section

Embed

Interactive Plotly World Map

Display

Cities

Connections

Risk Levels

Hover Details

Filters

Zoom Controls

---

# 11. Recent Activity

Display

Dataset Uploaded

Graph Generated

Training Completed

Prediction Completed

Report Generated

User Login

Each entry should include

Timestamp

User

Action

Status

---

# 12. Notifications Panel

Display

Unread Notifications

System Alerts

Training Alerts

Prediction Alerts

Actions

View

Mark as Read

Dismiss

---

# 13. System Status

Display

Database Status

AI Engine Status

Graph Engine Status

API Status

Celery Status

Redis Status

Status Indicators

Healthy

Warning

Offline

---

# 14. Dashboard Refresh

Support

Manual Refresh

Automatic Refresh (Configurable)

Refresh Interval

30 Seconds (Default)

Do not refresh while a long-running operation is in progress.

---

# 15. Filters

Provide filters for

Dataset

Country

Risk Level

Date Range

Protocol

Prediction Status

Model Version

---

# 16. Search

Allow search by

Dataset Name

City

Country

Prediction ID

Graph ID

Highlight matching results.

---

# 17. Role-Based Visibility

Administrator

View all dashboard components

Analyst

View operational and AI components

Viewer

View read-only dashboard and reports

Hide unauthorized widgets automatically.

---

# 18. Error Handling

Handle

Missing Data

Failed API Calls

Visualization Errors

Timeouts

Display informative messages and retry options.

---

# 19. Performance

Optimize using

Database Query Optimization

Caching

Pagination

Lazy Loading

Background Data Refresh

Compressed Static Assets

---

# 20. Logging

Log

Dashboard Access

Widget Load Time

Refresh Events

Chart Generation

Errors

Warnings

---

# 21. Testing

Unit Tests

Widget Tests

Chart Tests

Filter Tests

Integration Tests

Dashboard Rendering

API Integration

Responsive Tests

Performance Tests

---

# 22. Success Criteria

The dashboard is complete when

✔ KPI cards display correctly

✔ Charts render successfully

✔ World map loads

✔ Recent activity updates

✔ Notifications work

✔ Filters function correctly

✔ Search works

✔ System status is visible

✔ Responsive design verified

✔ Tests pass

✔ Documentation complete

---

# Future Improvements

Real-Time Dashboard

Custom Dashboard Widgets

Drag-and-Drop Layout

Dark Mode

Live Threat Feed

User-Customizable KPIs

Dashboard Export (PDF)

Mobile Dashboard App

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Dashboard Layout

2.

KPI Cards

3.

Interactive Charts

4.

World Map Integration

5.

Recent Activity Panel

6.

Notifications Panel

7.

System Status Widgets

8.

Filters and Search

9.

Responsive Design

10.

Unit Tests

11.

Documentation

Generate production-ready code only.

Use reusable dashboard components.

Separate presentation logic from business logic.

Use Plotly for visualizations.

Include logging, type hints, and documentation.

Wait for approval after completing each component.

End of Dashboard Design