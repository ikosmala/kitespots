from .. import schemas
import pytest


def test_get_all_users(client, create_test_users):
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    for i, created_user in enumerate(create_test_users):
        assert created_user["email"] == users[i]["email"]
        assert created_user["name"] == users[i]["name"]
        assert created_user["active"] == users[i]["active"]
        assert created_user["id"] == users[i]["id"]


def test_create_user(client):
    user_data = {
        "email": "valid@email.com",
        "name": "ValidName",
        "password": "ValidPassword",
    }
    response = client.post("/users/", json=user_data)
    new_user = schemas.UserOut(**response.json())
    assert new_user.email == user_data["email"]
    assert new_user.name == user_data["name"]


@pytest.mark.parametrize(
    "email, name, password, result",
    [
        ("valid@email.com", "", "validpassword", 422),
        ("invalid-email.com", "ValidName", "validpassword", 422),
        ("valid@email.com", "ValidName", "", 422),
        ("", "ValidName", "validpassword", 422),
    ],
)
def test_invalid_create_user(client, email, name, password, result):
    response = client.post(
        "/users/", json={"email": email, "name": name, "password": password}
    )
    assert response.status_code == result
