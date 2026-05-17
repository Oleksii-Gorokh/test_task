import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_loads(client):
    response = client.get(reverse('register'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_with_valid_credentials(client, regular_user):
    response = client.post(reverse('login'), {
        'email': 'user@test.com',
        'password': 'user123!',
    })
    assert response.status_code == 302
    assert response.url == reverse('dashboard')


@pytest.mark.django_db
def test_login_with_wrong_password(client, regular_user):
    response = client.post(reverse('login'), {
        'email': 'user@test.com',
        'password': 'wrongpassword',
    })
    assert response.status_code == 200
    assert 'Невірний пароль' in response.content.decode()


@pytest.mark.django_db
def test_login_with_unknown_email(client):
    response = client.post(reverse('login'), {
        'email': 'nobody@test.com',
        'password': 'anything',
    })
    assert response.status_code == 200
    assert 'не знайдено' in response.content.decode()


@pytest.mark.django_db
def test_dashboard_redirects_unauthenticated(client):
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_dashboard_accessible_after_login(client, regular_user):
    client.login(username='regularuser', password='user123!')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_creates_user_with_role(client):
    response = client.post(reverse('register'), {
        'email': 'newuser@test.com',
        'password': 'newpass123!',
        'password_confirm': 'newpass123!',
    })
    assert response.status_code == 302
    user = User.objects.get(email='newuser@test.com')
    assert hasattr(user, 'profile')
    assert user.profile.role == 'user'


@pytest.mark.django_db
def test_register_password_mismatch(client):
    response = client.post(reverse('register'), {
        'email': 'bad@test.com',
        'password': 'pass1',
        'password_confirm': 'pass2',
    })
    assert response.status_code == 200
    assert not User.objects.filter(email='bad@test.com').exists()


@pytest.mark.django_db
def test_logout_redirects(client, regular_user):
    client.login(username='regularuser', password='user123!')
    response = client.get(reverse('logout'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_admin_panel_blocked_for_regular_user(client, regular_user):
    client.login(username='regularuser', password='user123!')
    response = client.get(reverse('admin_panel'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_admin_panel_accessible_for_admin(client, admin_user):
    client.login(username='adminuser', password='admin123!')
    response = client.get(reverse('admin_panel'))
    assert response.status_code == 200
