"""
Admin Configuration for Graph Engine.

This module configures Django admin interface for graph_engine models.

Architecture:
- Clean Architecture: Infrastructure Layer
- Follows Django admin best practices
- Custom admin actions and filters

Status: Phase 2 - Issue #1
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import City, Country, Dataset, Transaction


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin configuration for Country model."""

    list_display = [
        "iso_code",
        "country_name",
        "continent",
        "latitude",
        "longitude",
        "created_at",
    ]
    list_filter = ["continent", "created_at"]
    search_fields = ["iso_code", "iso_code_3", "country_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["country_name"]
    fieldsets = (
        (
            "Identification",
            {"fields": ("iso_code", "iso_code_3", "country_name")},
        ),
        (
            "Geographic Information",
            {"fields": ("continent", "latitude", "longitude")},
        ),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at"), "classes": ["collapse"]},
        ),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin configuration for City model."""

    list_display = ["city_name", "country", "latitude", "longitude", "population", "created_at"]
    list_filter = ["country", "created_at"]
    search_fields = ["city_name", "country__country_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["city_name"]
    autocomplete_fields = ["country"]
    fieldsets = (
        (
            "Identification",
            {"fields": ("country", "city_name")},
        ),
        (
            "Geographic Information",
            {"fields": ("latitude", "longitude")},
        ),
        (
            "Demographics",
            {"fields": ("population", "timezone")},
        ),
        (
            "Metadata",
            {"fields": ("id", "created_at", "updated_at"), "classes": ["collapse"]},
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("country")


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Admin configuration for Dataset model."""

    list_display = [
        "dataset_name",
        "version",
        "status",
        "record_count",
        "created_by",
        "created_at",
    ]
    list_filter = ["status", "version", "created_at"]
    search_fields = ["dataset_name", "description"]
    readonly_fields = ["id", "created_at", "checksum"]
    ordering = ["-created_at"]
    # autocomplete_fields = ["created_by"]  # User model not available yet (Phase 11)
    fieldsets = (
        (
            "Identification",
            {"fields": ("dataset_name", "version", "description", "source")},
        ),
        (
            "Status & Configuration",
            {"fields": ("status", "created_by", "random_seed")},
        ),
        (
            "Statistics",
            {"fields": ("record_count", "configuration", "statistics")},
        ),
        (
            "Integrity",
            {"fields": ("checksum",), "classes": ["collapse"]},
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    "created_at",
                ),
                "classes": ["collapse"],
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("created_by")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction model."""

    list_display = [
        "id",
        "source_city",
        "destination_city",
        "protocol",
        "bandwidth",
        "latency",
        "is_anomaly",
        "risk_label",
        "timestamp",
    ]
    list_filter = [
        "protocol",
        "is_anomaly",
        "risk_label",
        "connection_type",
        "timestamp",
    ]
    search_fields = [
        "source_city__city_name",
        "destination_city__city_name",
        "dataset__dataset_name",
    ]
    readonly_fields = ["id", "timestamp"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"
    autocomplete_fields = ["dataset", "source_city", "destination_city"]
    fieldsets = (
        (
            "Identification",
            {"fields": ("dataset", "timestamp")},
        ),
        (
            "Network Flow",
            {"fields": ("source_city", "destination_city", "protocol")},
        ),
        (
            "Metrics",
            {
                "fields": (
                    "packet_count",
                    "packet_size",
                    "bandwidth",
                    "latency",
                    "duration",
                )
            },
        ),
        (
            "Classification",
            {"fields": ("is_anomaly", "risk_label", "connection_type", "encryption")},
        ),
        (
            "Metadata",
            {"fields": ("id",), "classes": ["collapse"]},
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("source_city", "destination_city", "dataset")
        )

    def is_anomaly_colored(self, obj: Transaction) -> str:
        """Return colored HTML for anomaly status."""
        if obj.is_anomaly:
            return format_html('<span style="color: red;">⚠️</span>')
        return format_html('<span style="color: green;">✓</span>')

    is_anomaly_colored.short_description = "Anomaly"
    is_anomaly_colored.admin_order_field = "is_anomaly"

    list_display.insert(6, "is_anomaly_colored")
