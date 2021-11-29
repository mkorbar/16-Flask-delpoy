import os
import pytest

# important: this line needs to be set BEFORE the "app" import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app, db


@pytest.fixture
def client():
    client = app.test_client()

    cleanup()  # clean up before every test

    db.create_all()

    yield client


def cleanup():
    # clean up/delete the DB (drop all tables in the database)
    db.drop_all()


def test_home_page(client):
    response = client.get('/')
    assert 'Dobrodošli na mojo stran'.encode() in response.data


def test_game_for_unauthenticated_user(client):
    response = client.get('/game', follow_redirects=True)
    assert 'Vpiši se na mojo stran'.encode() in response.data
    assert 'Play the guessing game'.encode() not in response.data


def test_logged_in_user(client):
    uname = 'TestUser'
    response = client.post('/login', data={
        'name': uname,
        'email': 'test@test.si',
        'password': 'asdf123'
    })
    assert ('Created a new user ' + uname).encode() in response.data
    response = client.get('/game')
    assert 'Play the guessing game'.encode() in response.data
    assert f"You're playing as {uname}".encode() in response.data

