def test_gzip_compressible_response(client):
    response = client.get("/health", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"


def test_gzip_no_accept_encoding(client):
    response = client.get("/health")
    assert response.status_code == 200
