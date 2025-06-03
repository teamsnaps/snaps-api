import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def verified_user1():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username='verified_user1',
        email='verified_user1@gmail.com',
        password='mysecretpassword1'
    )

    user.save()