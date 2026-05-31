import pytest
from movie import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_index_loads(client):
    response = client.get('/')
    assert response.status_code == 200


def test_add_movie(client):
    response = client.post('/', data={'title': 'The Matrix', 'year': 1999, 'rating': 8.7})
    assert response.status_code == 200
    assert b'The Matrix' in response.data


def test_add_movie_title_only(client):
    response = client.post('/', data={'title': 'Inception'})
    assert response.status_code == 200
    assert b'Inception' in response.data


def test_delete_movie(client):
    client.post('/', data={'title': 'ToDelete'})
    response = client.post('/delete', data={'title': 'ToDelete'})
    assert response.status_code == 302


def test_update_movie(client):
    client.post('/', data={'title': 'OldTitle', 'year': 2000})
    response = client.post('/update', data={
        'oldtitle': 'OldTitle',
        'newtitle': 'NewTitle',
        'year': 2001
    })
    assert response.status_code == 302


def test_metrics_endpoint(client):
    response = client.get('/metrics')
    assert response.status_code == 200