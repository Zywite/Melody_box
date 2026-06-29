def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_spa_fallback_returns_json_for_excluded_path(client):
    response = client.get("/music/somefile.mp3")
    assert response.status_code == 404


def test_spa_fallback_returns_json_for_unknown_route(client):
    response = client.get("/api/nonexistent")
    assert response.status_code == 200
