from __future__ import annotations


def test_mark_eaten_creates_history_event(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    first = generated["planned_meals"][0]
    response = client.post(f"/api/v1/planned-meals/{first['id']}/mark-eaten")
    assert response.status_code == 200
    event = response.json()
    assert event["meal_id"] == first["meal_id"]
    assert event["variation_selections"] == first["variation_selections"]
    history = client.get("/api/v1/history").json()
    assert history[0]["id"] == event["id"]


def test_skip_does_not_create_history_event(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    first = generated["planned_meals"][0]
    response = client.post(f"/api/v1/planned-meals/{first['id']}/skip")
    assert response.status_code == 200
    assert response.json()["state"] == "skipped"
    assert client.get("/api/v1/history").json() == []
