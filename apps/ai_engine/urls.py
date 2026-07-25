"""
URL Configuration for AI Engine Application.

This module defines URL patterns for:
- Model training
- Inference
- Model management
- Evaluation

Status: Placeholder URLs, will be implemented in Phases 5, 6, 7, 11
"""
from django.urls import path
from . import views

app_name = "ai_engine"

urlpatterns: list = [
    # Training
    # path("train/", views.TrainModelView.as_view(), name="train"),
    # path("train/status/<uuid:run_id>/", views.TrainingStatusView.as_view(), name="training_status"),
    
    # Inference
    # path("predict/", views.PredictView.as_view(), name="predict"),
    
    # Models
    # path("models/", views.ModelListView.as_view(), name="models"),
    # path("models/<uuid:model_id>/", views.ModelDetailView.as_view(), name="model_detail"),
]