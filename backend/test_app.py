"""
Tests for the Coffee Rating API.

Run with:
    cd backend
    python -m pytest test_app.py -v
"""

import json
import os
import sys
import tempfile
import pytest

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))

# Override the DB path BEFORE importing the app so tests use a temp file
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["TEST_DB"] = _tmp_db.name

import database as _db

_original_db_path = _db.DB_PATH
_db.DB_PATH = _tmp_db.name

from app import app as flask_app


@pytest.fixture(autouse=True)
def reset_db():
    """Re-initialize a clean database before every test."""
    # Drop existing table so we start fresh
    conn = _db.get_connection()
    conn.execute("DROP TABLE IF EXISTS coffees")
    conn.commit()
    conn.close()
    _db.init_db()
    yield


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestGetCoffees:
    def test_returns_success(self, client):
        resp = client.get("/api/coffees")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_returns_six_coffees(self, client):
        data = client.get("/api/coffees").get_json()
        assert len(data["coffees"]) == 6

    def test_all_required_fields(self, client):
        data = client.get("/api/coffees").get_json()
        for coffee in data["coffees"]:
            for field in ("id", "name", "description", "image_url", "vote_count"):
                assert field in coffee, f"Missing field '{field}' in coffee: {coffee}"

    def test_initial_vote_count_zero(self, client):
        data = client.get("/api/coffees").get_json()
        for coffee in data["coffees"]:
            assert coffee["vote_count"] == 0


class TestVote:
    def test_vote_increments_by_one(self, client):
        # Get the first coffee id
        coffees = client.get("/api/coffees").get_json()["coffees"]
        first_id = coffees[0]["id"]

        resp = client.post(f"/api/coffees/{first_id}/vote")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["vote_count"] == 1

    def test_vote_nonexistent_coffee_returns_404(self, client):
        resp = client.post("/api/coffees/9999/vote")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["success"] is False

    def test_multiple_votes_accumulate(self, client):
        coffees = client.get("/api/coffees").get_json()["coffees"]
        cid = coffees[0]["id"]

        for _ in range(5):
            client.post(f"/api/coffees/{cid}/vote")

        resp = client.post(f"/api/coffees/{cid}/vote")
        assert resp.get_json()["vote_count"] == 6

    def test_votes_persist_across_requests(self, client):
        coffees = client.get("/api/coffees").get_json()["coffees"]
        cid = coffees[0]["id"]

        client.post(f"/api/coffees/{cid}/vote")
        client.post(f"/api/coffees/{cid}/vote")

        all_coffees = client.get("/api/coffees").get_json()["coffees"]
        match = next(c for c in all_coffees if c["id"] == cid)
        assert match["vote_count"] == 2

    def test_votes_for_different_coffees_independent(self, client):
        coffees = client.get("/api/coffees").get_json()["coffees"]
        id_a = coffees[0]["id"]
        id_b = coffees[1]["id"]

        client.post(f"/api/coffees/{id_a}/vote")
        client.post(f"/api/coffees/{id_a}/vote")
        client.post(f"/api/coffees/{id_b}/vote")

        all_coffees = {c["id"]: c for c in client.get("/api/coffees").get_json()["coffees"]}
        assert all_coffees[id_a]["vote_count"] == 2
        assert all_coffees[id_b]["vote_count"] == 1


class TestHealth:
    def test_health_endpoint(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"
