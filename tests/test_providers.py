from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import database
import crypto
import main
from models import Base, Provider


def make_test_client():
    test_engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    database.engine = test_engine
    database.SessionLocal = TestingSessionLocal
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[database.get_db] = override_get_db
    return TestClient(main.app), TestingSessionLocal


def test_provider_crud():
    client, TestingSessionLocal = make_test_client()

    create_resp = client.post(
        "/api/providers",
        json={
            "name": "OpenAI",
            "website": "https://openai.com",
            "signup_url": "https://platform.openai.com/signup",
            "api_docs": "https://platform.openai.com/docs",
            "api_key": "secret",
            "enabled": True,
        },
    )
    assert create_resp.status_code == 201
    provider = create_resp.json()
    assert provider["id"] == 1
    assert provider["name"] == "OpenAI"
    assert provider["enabled"] is True
    assert provider["api_key"] == "secret"
    assert "created_at" in provider

    with TestingSessionLocal() as db:
        stored = db.get(Provider, provider["id"])
        assert stored is not None
        assert stored.api_key is not None
        assert stored.api_key != "secret"
        assert crypto.decrypt(stored.api_key) == "secret"

    get_resp = client.get(f"/api/providers/{provider['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "OpenAI"
    assert get_resp.json()["api_key"] == "secret"

    update_resp = client.put(
        f"/api/providers/{provider['id']}",
        json={
            "website": "https://openai.com/updated",
            "enabled": False,
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["website"] == "https://openai.com/updated"
    assert updated["enabled"] is False

    delete_resp = client.delete(f"/api/providers/{provider['id']}")
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/api/providers/{provider['id']}")
    assert missing_resp.status_code == 404


def test_duplicate_name_returns_error():
    client, _ = make_test_client()

    first = client.post("/api/providers", json={"name": "Anthropic"})
    assert first.status_code == 201

    second = client.post("/api/providers", json={"name": "Anthropic"})
    assert second.status_code == 400
    assert second.json()["detail"] == "Provider name already exists"
