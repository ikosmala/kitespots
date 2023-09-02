from fastapi.testclient import TestClient
from ..main import app
from ..database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from .. import schemas

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


Base.metadata.create_all(bind=test_engine)


@pytest.fixture
def session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# create test users in database
@pytest.fixture()
def create_test_users(client):
    users_data = [
        {"email": "test1@email.com", "name": "Tester", "password": "testpassword"},
        {"email": "test2@email.com", "name": "Tester2 ", "password": "testpass"},
    ]
    created_users = []
    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201
        created_user = response.json()
        created_user["password"] = user["password"]
        created_users.append(created_user)
    return created_users
