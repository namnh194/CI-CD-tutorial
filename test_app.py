import app

def test_hello():
    # Sử dụng test client của Flask để gọi API
    with app.app.test_client() as client:
        response = client.get("/")
        assert response.data == b"Hello, CI/CD with Python!"
        