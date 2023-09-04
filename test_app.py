from website import create_app, db
from website.models import Users
import pytest
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

@pytest.fixture
def app():
    app = create_app(env='testing') 
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth(client):
    with client.application.app_context():
        # Create a test user and simulate their authentication
        test_user = Users(email=TEST_EMAIL, password=TEST_PASSWORD)
        db.session.add(test_user)
        db.session.commit()

        # Simulate user login
        with client.session_transaction() as session:
            session['user_id'] = test_user.id

    return client


def test_new_user(client):
    response = client.post(
        "/sign-up",
        data={
            "email": TEST_EMAIL,
            "password1": TEST_PASSWORD,
            "password2": TEST_PASSWORD,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    user = Users.query.filter_by(email=TEST_EMAIL).first()
    assert user is not None

def test_home_route(client, auth):
    with auth.application.app_context():
        response = client.get('/', follow_redirects=True)

        # Ensure that the user is authenticated
        with client.session_transaction() as session:
            user_id = session.get('user_id')
            authenticated_user = Users.query.get(user_id)

        # Debugging: Print user_id and authenticated_user
        print("user_id:", user_id)
        print("authenticated_user:", authenticated_user)

        # Print response headers and URL
        print("Response headers:", response.headers)
        print("Redirect URL:", response.location)

        assert authenticated_user is not None
        assert authenticated_user.email == TEST_EMAIL
        
        # Assert that the response is a redirect to the login page
        assert response.status_code == 200

      
