import unittest
from unittest import TestCase

from database.db_handler import DatabaseHandler, Users


class DatabaseTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database_handler = DatabaseHandler()
        cls.database_handler.create_db()
        cls.database_handler.clear_db()

    def tearDown(self):
        self.database_handler.clear_db()

    def test_create_user_1(self):
        created = self.database_handler.create(
            table=Users,

            id="UserID1",
            name="Andrew"
        )
        self.assertTrue(created)

    def test_create_user_2(self):
        created_1 = self.database_handler.create(
            table=Users,

            id="UserID1",
            name="Andrew"
        )

        created_2 = self.database_handler.create(
            table=Users,

            id="UserID1",
            name="Bob"
        )
        self.assertTrue(created_1 and not created_2)

    def test_read_user_1(self):
        user = self.database_handler.read(Users, 'UNKNOWN USERID')
        self.assertIsNone(user)

    def test_read_user_2(self):
        self.database_handler.create(
            table=Users,

            id="UserID1",
            name="Andrew"
        )
        user = self.database_handler.read(Users, 'UserID1')
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Andrew")

    def test_update_user_1(self):
        self.database_handler.create(
            table=Users,

            id="UserID1",
            name="Andrew"
        )
        updated = self.database_handler.update(
            table=Users,

            id="UserID1",
            name="NewAndrew"
        )
        updated_user = self.database_handler.read(Users, 'UserID1')
        self.assertTrue(updated)
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, "NewAndrew")

    def test_update_user_2(self):
        updated = self.database_handler.update(
            table=Users,

            id="UserID1",
            name="NewAndrew",
        )
        updated_user = self.database_handler.read(Users, 'UserID1')
        self.assertFalse(updated)
        self.assertIsNone(updated_user)

    def test_delete_user_1(self):
        pass


if __name__ == '__main__':
    unittest.main()
