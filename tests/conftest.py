import pytest
from django.contrib.auth.models import User
from accounts.models import UserProfile


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username='adminuser',
        email='admin@test.com',
        password='admin123!',
    )
    UserProfile.objects.create(user=user, role='admin')
    return user


@pytest.fixture
def regular_user(db):
    user = User.objects.create_user(
        username='regularuser',
        email='user@test.com',
        password='user123!',
    )
    UserProfile.objects.create(user=user, role='user')
    return user
