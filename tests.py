"""Test Suite for testing Hackbright project."""

import server
import unittest
import doctest


def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests.

    This function name, ``load_tests``, is required.
    """

    tests.addTests(doctest.DocTestSuite(server))
    tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class MyAppUnitTestCase(unittest.TestCase):
    """Examples of unit tests: discrete code testing."""

    def testAdder(self):
        assert server.adder(1, 1) == 99

    def test_should_add_two_nums(self):
        self.assertEqual(server.adder(4, 5), 9)

    def test_things(self):
        self.assertEqual(len(server.things_from_db()), 3)


class MyAppIntegrationTestCase(unittest.TestCase):
    """Examples of integration tests: testing Flask server."""

    def setUp(self):
        print "(setUp ran)"
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def tearDown(self):
        # We don't need to do anything here; we could just
        # not define this method at all, but we have a stub
        # here as an example.
        print "(tearDown ran)"

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("walking app", result.data)

    def test_login(self):
        result = self.client.get("/login")
        self.assertIn("Log In", result.data)

    def test_bad_login(self):
        result = self.client.post("/login",
                                  data={'name': "Boomer", 'email': "boomer@gmail.com"},
                                  follow_redirects=True)
        self.assertIn("Verify email and password entered is correct.", result.data)
        self.assertNotIn("logged in", result.data)

    def test_registration(self):
        result = self.client.post("/registration",
                                  data={'name': "Jimmy", 'email': "jimmy@jimmy.com"},
                                  follow_redirects=True)
        self.assertIn("Your account has been created.", result.data)

    def test_duplicate_registration(self):
        result = self.client.post("/registration",
                                  data={'name': "Jane", 'email': "jane@jane.com"},
                                  follow_redirects=True)
        self.assertIn("An account has already been created for this email.", result.data)
    # add check for redirect to login page


    def test_logout(self):
        result = self.client.get('/logout')
        self.assertIn('Logged out', result.data)
        # self.assertNotIn('user_id', session)
    # add check for redirect to home page


if __name__ == '__main__':
    # If called like a script, run our tests

    unittest.main()