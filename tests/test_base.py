import os
from unittest import TestCase

from dotenv import load_dotenv

from app import create_app
from db import db


load_dotenv()


class TestBase(TestCase):
    """
    TestBase

    This class should be the parent class to each non-unit test.
    It allows for instantiation of the database dynamically
    and makes sure that it is a new, blank database each time.
    """
    def setUp(self):
        # Make sure database exists
        self.app = create_app(db_url=os.getenv('TEST_DATABASE_URL'))
        app = self.app

        # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL')
        with app.app_context():
            db.init_app(app)
            db.create_all()
        # Get a test client
        self.test_client = app.test_client()
        self.app_context = app.app_context

    def tearDown(self):
        # Database is blank
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            pass

    def test_haha(self):
        print(self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertTrue(True)
