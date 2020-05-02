
import json
import os
import re
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client
from django.test import TestCase


class TestEmailSignup(TestCase):


    def test_email_signup_full_flow(self):
        web = Client()

        # Sign up with email
        response = web.post(
            '/auth/accounts/signup/',
            {'email': 'test1@convex.cc',
             'password1':'69BillAndTed',
             'password2':'69BillAndTed'})
        self.assertRedirects(response, '/auth/accounts/confirm-email/')
        current_site = Site.objects.get_current()
        self.assertEqual(
            mail.outbox[-1].subject,
            "[Battle Chat Rising!] Please Confirm Your E-mail Address")
        self.assertTrue('example.com' not in mail.outbox[-1].body)
        self.assertTrue(current_site.domain in mail.outbox[-1].body)
        self.assertTrue(current_site.name in mail.outbox[-1].body)
        self.assertEqual(
            mail.outbox[-1].to,
            ["test1@convex.cc"])
        self.assertEqual(
            mail.outbox[-1].from_email,
            "support@convex.cc")

        # Retrieve the verify url from the body.
        body_words = mail.outbox[-1].body.split()
        body_urls = [word for word in body_words
                     if word.startswith(
                         "http://testserver/auth/accounts/confirm-email/")]
        verify_link = body_urls[-1].replace('http://testserver/', '/')

        # Verify email
        response = web.post(verify_link)
        self.assertRedirects(response, '/auth/accounts/login/')

        # Login
        response = web.post(
            '/auth/accounts/login/',
            {'login': 'test1@convex.cc',
             'password':'69BillAndTed'})
        self.assertRedirects(response, '/auth/user/')

        # Get the username now we are logged in
        response = web.get('/auth/user/')
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)['user']
        self.assertEqual(
            username,
            User.objects.get(email='test1@convex.cc').username)

        # Check it looks like a UUID4 id
        UUID4 = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.assertTrue(re.match(UUID4, username))

        # Collect API token
        response = web.post('/auth/token/login/')
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)['token']

        # Make new connection with API token
        headers = {'HTTP_AUTHORIZATION': 'Token %s' % token}
        api = Client(**headers)

        # Check we can get the username from this token
        response = api.get('/auth/user/')
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)['user']
        self.assertEqual(
            username,
            User.objects.get(email='test1@convex.cc').username)

        # Logout from the API token
        response = api.post('/auth/token/logout/')
        self.assertEqual(response.status_code, 200)

        # Check we can't get the username
        response = api.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content),
                         {"detail":"Invalid token."})

        # Logout from the session
        response = web.post('/auth/accounts/logout/')
        self.assertRedirects(response, '/auth/accounts/login/')

        # Check we can't get the username
        response = web.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content),
            {"detail":"Authentication credentials were not provided."})


    def test_email_signup_needs_verification(self):
        web = Client()

        # Sign up with email
        response = web.post(
            '/auth/accounts/signup/',
            {'email': 'test1@convex.cc',
             'password1':'69BillAndTed',
             'password2':'69BillAndTed'})

        # Login
        response = web.post(
            '/auth/accounts/login/',
            {'login': 'test1@convex.cc',
             'password':'69BillAndTed'})
        self.assertRedirects(response, '/auth/accounts/confirm-email/')

        # Check we can't get the username
        response = web.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content),
            {"detail":"Authentication credentials were not provided."})


class TestSessionSignedUp(TestCase):

    def setUp(self):
        web = Client()

        # Sign up with email
        response = web.post(
            '/auth/accounts/signup/',
            {'email': 'test1@convex.cc',
             'password1':'69BillAndTed',
             'password2':'69BillAndTed'})
        # Retrieve the verify url from the body.
        body_words = mail.outbox[-1].body.split()
        body_urls = [word for word in body_words
                     if word.startswith(
                         "http://testserver/auth/accounts/confirm-email/")]
        verify_link = body_urls[-1].replace('http://testserver/', '/')
        # Verify email
        response = web.post(verify_link)

        self.web = web


    def test_email_signup_full_flow(self):
        web = self.web

        # Login attempt with the wrong password
        response = web.post(
            '/auth/accounts/login/',
            {'login': 'test1@convex.cc',
             'password':'----    bad    password    ----'})

        # Check we can't get the username
        response = web.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content),
            {"detail":"Authentication credentials were not provided."})


    def test_token_login_fails_without_sign_in(self):
        web = self.web
        response = web.post('/auth/token/login/')
        self.assertRedirects(
            response,
            '/auth/accounts/login/?next=/auth/token/login/')


    def test_token_logout_fails_without_sign_in(self):
        web = self.web
        response = web.post('/auth/token/logout/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content),
            {"detail":"Authentication credentials were not provided."})


    def test_user_fails_without_sign_in(self):
        web = self.web
        response = web.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content),
            {"detail":"Authentication credentials were not provided."})


    def test_password_reset_email_customisations(self):
        web = self.web
        response = web.post(
            '/auth/accounts/password/reset/',
            {'email': 'test1@convex.cc'})
        self.assertRedirects(
            response,
            '/auth/accounts/password/reset/done/')
        current_site = Site.objects.get_current()
        self.assertEqual(
            mail.outbox[-1].subject,
            "[Battle Chat Rising!] Password Reset E-mail")
        self.assertTrue('example.com' not in mail.outbox[-1].body)
        self.assertTrue(current_site.domain in mail.outbox[-1].body)
        self.assertTrue(current_site.name in mail.outbox[-1].body)
        self.assertEqual(
            mail.outbox[-1].to,
            ["test1@convex.cc"])
        self.assertEqual(
            mail.outbox[-1].from_email,
            "support@convex.cc")


class TestSessionLoggedIn(TestCase):

    def setUp(self):
        web = Client()

        # Sign up with email
        response = web.post(
            '/auth/accounts/signup/',
            {'email': 'test1@convex.cc',
             'password1':'69BillAndTed',
             'password2':'69BillAndTed'})
        # Retrieve the verify url from the body.
        body_words = mail.outbox[0].body.split()
        body_urls = [word for word in body_words
                     if word.startswith(
                         "http://testserver/auth/accounts/confirm-email/")]
        verify_link = body_urls[0].replace('http://testserver/', '/')
        # Verify email
        response = web.post(verify_link)
        # Login
        response = web.post(
            '/auth/accounts/login/',
            {'login': 'test1@convex.cc',
             'password':'69BillAndTed'})
        # Collect API token
        response = web.post('/auth/token/login/')
        token = json.loads(response.content)['token']
        # Make new connection with API token
        headers = {'HTTP_AUTHORIZATION': 'Token %s' % token}
        api = Client(**headers)

        self.web = web
        self.api = api


    def test_token_login_fail_with_token_login(self):
        api = self.api
        response = api.post('/auth/token/login/')
        self.assertRedirects(
            response,
            '/auth/accounts/login/?next=/auth/token/login/')


    def test_login_when_already_logged_in(self):
        web = self.web
        response = web.get('/auth/accounts/login/')
        self.assertRedirects(response, '/auth/user/')


    def test_token_logout_with_session_login(self):
        web = self.web
        api = self.api

        # Logout from the API token
        response = web.post('/auth/token/logout/')
        self.assertEqual(response.status_code, 200)

        # Check we can't get the username
        response = api.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content),
                         {"detail":"Invalid token."})


    def test_session_logout_also_logs_out_from_token(self):
        web = self.web
        api = self.api

        # Logout from Session
        response = web.post('/auth/accounts/logout/')
        self.assertRedirects(response, '/auth/accounts/login/')

        # Check we can't get the username
        response = api.get('/auth/user/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content),
                         {"detail":"Invalid token."})


    def test_session_logout_but_keep_token(self):
        web = self.web
        api = self.api

        # Logout from Session but keep tokens.
        response = web.post('/auth/accounts/logout/', {'keeptokens': True})
        self.assertRedirects(response, '/auth/accounts/login/')

        # Check we can get the username from this token
        response = api.get('/auth/user/')
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)['user']
        self.assertEqual(
            username,
            User.objects.get(email='test1@convex.cc').username)


    def test_token_login_denied_account_management_pages(self):
        api = self.api

        for url_path in ['/auth/accounts/email/',
                         '/auth/accounts/password/change/',
                         '/auth/accounts/password/set/',
                         '/auth/accounts/social/connections/',]:
            response = api.get(url_path)
            self.assertRedirects(response,
                '/auth/accounts/login/?next=%s' % url_path)


class TestSiteCustomisations(TestCase):


    def test_domain_and_site_name_are_correct(self):
        # We only want to have this service one site.
        # If we need mutliple sites, mircorservices this baby.
        current_site = Site.objects.get_current()
        self.assertEqual(current_site.domain, os.environ['DOMAIN'])
        self.assertEqual(current_site.name, os.environ['SITE_NAME'])
