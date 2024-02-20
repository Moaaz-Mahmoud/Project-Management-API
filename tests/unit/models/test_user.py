from collections import defaultdict
from datetime import datetime
from unittest import TestCase

from passlib.hash import pbkdf2_sha256 as hashing_algo

from models import UserModel
from models.user import UserStatus


class TestTask(TestCase):
    def test_create_user(self):
        now = datetime.now()
        user = UserModel(
            name='Example User',
            username='example_user',
            email='example.user@example.com',
            password='123',
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )

        self.assertEqual(user.name, "Example User")
        self.assertEqual(user.username, "example_user")
        self.assertEqual(user.email, "example.user@example.com")
        self.assertEqual(user.password, "123")
        self.assertEqual(user.status, UserStatus.ACTIVE)
        self.assertEqual(user.created_at, now)
        self.assertEqual(user.updated_at, now)

    def test_as_dict(self):
        now = datetime.now()
        user = UserModel(
            name='Example User',
            username='example_user',
            email='example.user@example.com',
            password='123',
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )

        expected_dict = defaultdict()
        expected_dict['id'] = None
        expected_dict['name'] = 'Example User'
        expected_dict['username'] = 'example_user'
        expected_dict['email'] = 'example.user@example.com'
        expected_dict['password'] = '123'
        expected_dict['status'] = 'active'
        expected_dict['created_at'] = now.isoformat()
        expected_dict['updated_at'] = now.isoformat()

        user_dict = user.as_dict()

        print(user_dict)
        print(expected_dict)

        self.assertDictEqual(user_dict, expected_dict)
