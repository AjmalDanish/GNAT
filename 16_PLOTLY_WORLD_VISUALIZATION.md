# Global Network Anomaly Tracker (GNAT)

# Plotly World Visualization Design

Version: 1.0

Status:
Approved

Module:
World Visualization

Visualization Library:
Plotly

Framework Integration:
Django Templates

---

# 1. Purpose

The World Visualization module provides an interactive global map that displays network communication between cities and highlights anomalous activity detected by the AI model.

It serves as the primary visualization component of the GNAT dashboard.

---

# 2. Objectives

The visualization shall

✔ Display worldwide communication

✔ Highlight anomalous nodes

✔ Display network connections

✔ Support zoom and pan

✔ Show interactive tooltips

✔ Filter displayed data

✔ Update dynamically after predictions

---

# 3. Visualization Workflow

Load Prediction

↓

Load Graph

↓

Prepare Geographic Data

↓

Generate Plotly Figure

↓

Render in Dashboard

↓

User Interaction

---

# 4. Data Requirements

Node Data

Node ID

City

Country

Latitude

Longitude

Risk Score

Community

Traffic Volume

Edge Data

Source

Destination

Bandwidth

Latency

Protocol

Weight

Prediction

---

# 5. Map Projection

Default

Natural Earth

Future Options

Mercator

Orthographic

Equirectangular

Projection must be configurable.

---

# 6. Node Representation

Each node represents a city.

Node Size

Based on Traffic Volume

Node Color

Green

Low Risk

Yellow

Medium Risk

Orange

High Risk

Red

Critical Risk

---

# 7. Edge Representation

Each edge represents communication.

Edge Width

Based on Traffic Volume

Edge Color

Normal

Gray

Anomalous

Red

Opacity

Configurable

---

# 8. Interactive Features

Support

Zoom

Pan

Hover

Click

Double Click Reset

Legend Toggle

Export Image

---

# 9. Tooltips

Display

City

Country

Risk Score

Traffic Volume

Community

Incoming Connections

Outgoing Connections

Prediction

---

# 10. Filters

Country

Continent

Risk Level

Protocol

Community

Prediction Status

Date Range

Search by City

---

# 11. Search

Allow users to search

City

Country

Node ID

Highlight matching nodes.

---

# 12. Legends

Display

Risk Levels

Traffic Levels

Node Size

Edge Meaning

Community Colors (Future)

---

# 13. Dashboard Integration

Embed inside

Dashboard

Prediction Details

Graph Details

Reports (Static Snapshot)

---

# 14. Performance

Support

Lazy Loading

Efficient Data Preparation

Limit Maximum Visible Edges

Server-side Filtering

Client-side Interaction

---

# 15. Error Handling

Handle

Missing Coordinates

Missing Predictions

Empty Dataset

Rendering Failure

Invalid Graph

Display user-friendly messages.

---

# 16. Configuration

Map Projection

Default Zoom

Node Size Range

Edge Width Range

Color Scheme

Maximum Visible Nodes

Maximum Visible Edges

Animation Enabled

---

# 17. Export

Allow users to export

PNG

SVG

HTML

Future

PDF

---

# 18. Logging

Log

Visualization Generated

Render Time

Filter Usage

Export Actions

Errors

Warnings

---

# 19. Testing

Unit Tests

Data Preparation

Configuration

Visualization Generation

Integration Tests

Dashboard Rendering

Prediction Integration

Performance Tests

Large Graph Rendering

---

# 20. Success Criteria

The visualization is complete when

✔ World map renders successfully

✔ Nodes display correctly

✔ Edges display correctly

✔ Risk colors applied

✔ Filters function

✔ Search works

✔ Tooltips display correctly

✔ Export works

✔ Tests pass

✔ Documentation complete

---

# Future Improvements

Animated Traffic Flow

Real-Time Streaming

Time Slider

3D Globe

Cluster Visualization

Heatmap Overlay

Threat Timeline

Satellite View

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Data Preparation Module

2.

Plotly Figure Generator

3.

Node Rendering

4.

Edge Rendering

5.

Interactive Controls

6.

Filtering & Search

7.

Export Features

8.

Dashboard Integration

9.

Unit Tests

10.

Documentation

Generate production-ready code only.

Keep visualization logic separate from business logic.

Use reusable plotting utilities.

Include configuration support.

Include logging and type hints.

Wait for approval after each component.

End of Plotly World Visualization Design