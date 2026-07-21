import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth.utils import get_current_user_api as get_current_user_dep
from app.models.user import User
from app.auth.utils import get_password_hash


TEST_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        # create a test user
        pw = get_password_hash("testpass")
        user = User(email="test@example.com", full_name="Test User", password_hash=pw)
        db.add(user)
        db.commit()
        db.refresh(user)
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    # override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # override current user dependency to return our test user
    def override_current_user():
        return db_session.query(User).filter(User.email == "test@example.com").first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_dep] = override_current_user
    with TestClient(app) as c:
        yield c
