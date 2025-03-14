from fastapi.testclient import TestClient
from main import app

client = TestClient(app)  # Creation of the test client


# Test of the read_root function ("/") endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# Test of the get_options function ("/get-options") endpoint
def test_get_options():
    response = client.get("/get-options", params={"term": "Harry Potter", "limit": 5})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5


# Test of the get_options function ("/get-options") endpoint with empty response
def test_get_options_empty():
    response = client.get("/get-options")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test of the test_receive_data function ("/sent-data") endpoint
def test_receive_data():
    test_data = {"ISBN": "0345402871"}
    response = client.post("/sent-data", json=test_data)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert isinstance(json_data["rec_books"], list)

