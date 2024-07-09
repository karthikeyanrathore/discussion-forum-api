import pytest
import datetime
import requests 

JWT_SECRET_KEY = "secret1415@!kalm"
HOST_ADDRESS = "http://0.0.0.0:80"

@pytest.fixture
def jwt_client_token():
    payload = {
        "username": "eric singer",
        "password": "kalm4@178jo12k!0%%%",
        "email_id": "eric1987_singer@pytest.co.in",
        "mobile_number": 1167866013
    }
    ret = (requests.post(f"{HOST_ADDRESS}/backend/api/users/signup",json=payload))
    payload = {
        "username": "eric singer",
        "password": "kalm4@178jo12k!0%%%",
    }
    ret = (requests.post(f"{HOST_ADDRESS}/backend/api/users/login",json=payload))
    assert ret.status_code == 200
    return ret.json()["data"]["access_token"]