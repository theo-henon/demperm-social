"""
Tests for admin report management endpoints.
"""
import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from db.entities.message_entity import Report
from db.entities.user_entity import User, UserProfile, UserSettings


def _create_user(email_prefix: str = "user", is_admin: bool = False) -> User:
    """Helper to create a user with profile/settings."""
    suffix = uuid.uuid4()
    user = User.objects.create(
        google_id=f"{email_prefix}-google-{suffix}",
        email=f"{email_prefix}-{suffix}@example.com",
        username=f"{email_prefix}_{suffix}",
        is_admin=is_admin,
    )
    UserProfile.objects.create(user=user, display_name=f"{email_prefix} display")
    UserSettings.objects.create(user=user)
    return user


@pytest.mark.django_db
def test_list_reports_filters_by_status(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")

    # Two pending reports and one resolved
    pending_1 = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="spam"
    )
    pending_2 = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="harassment"
    )
    Report.objects.create(
        reporter=reporter,
        target_type="user",
        target_id=target.user_id,
        reason="inappropriate",
        status="resolved",
    )

    url = reverse("admin_panel:reports-list")
    response = admin_client.get(f"{url}?status=pending&page=1&page_size=10")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    returned_ids = {item["report_id"] for item in data}
    assert returned_ids == {str(pending_1.report_id), str(pending_2.report_id)}
    assert all(item["status"] == "pending" for item in data)


@pytest.mark.django_db
def test_update_report_status_sets_resolved(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")
    report = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="spam"
    )

    url = reverse("admin_panel:update-report", args=[report.report_id])
    response = admin_client.post(url, {"status": "resolved"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    report.refresh_from_db()

    assert payload["report_id"] == str(report.report_id)
    assert payload["status"] == "resolved"
    assert report.status == "resolved"
    assert report.resolved_at is not None


@pytest.mark.django_db
def test_update_report_status_rejected_sets_resolved_at(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")
    report = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="spam"
    )

    url = reverse("admin_panel:update-report", args=[report.report_id])
    response = admin_client.post(url, {"status": "rejected"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    report.refresh_from_db()
    assert report.status == "rejected"
    assert report.resolved_at is not None


@pytest.mark.django_db
def test_update_report_status_under_review_keeps_resolved_at_null(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")
    report = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="harassment"
    )

    url = reverse("admin_panel:update-report", args=[report.report_id])
    response = admin_client.post(url, {"status": "under_review"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    report.refresh_from_db()
    assert report.status == "under_review"
    assert report.resolved_at is None


@pytest.mark.django_db
def test_update_report_status_invalid_choice_returns_400(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")
    report = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="spam"
    )

    url = reverse("admin_panel:update-report", args=[report.report_id])
    response = admin_client.post(url, {"status": "not_a_status"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert "status" in body


@pytest.mark.django_db
def test_update_report_status_unknown_report_returns_404(admin_client):
    url = reverse("admin_panel:update-report", args=[uuid.uuid4()])
    response = admin_client.post(url, {"status": "resolved"}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


@pytest.mark.django_db
def test_reports_list_requires_admin(non_admin_client):
    url = reverse("admin_panel:reports-list")
    resp = non_admin_client.get(url)

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_report_requires_admin(another_non_admin, reporter_client=None):
    reporter = _create_user("reporter")
    target = _create_user("target")
    report = Report.objects.create(
        reporter=reporter, target_type="user", target_id=target.user_id, reason="spam"
    )

    url = reverse("admin_panel:update-report", args=[report.report_id])
    resp = another_non_admin.post(url, {"status": "resolved"}, format="json")

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_reports_list_pagination(admin_client):
    reporter = _create_user("reporter")
    target = _create_user("target")
    created_ids = []
    for idx in range(3):
        rpt = Report.objects.create(
            reporter=reporter,
            target_type="user",
            target_id=target.user_id,
            reason="spam" if idx % 2 == 0 else "harassment",
        )
        created_ids.append(str(rpt.report_id))

    url = reverse("admin_panel:reports-list")
    resp = admin_client.get(f"{url}?page=1&page_size=2")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
