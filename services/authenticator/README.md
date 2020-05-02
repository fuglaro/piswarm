# Authenticator Microservice

This service is responsible for authenticating users.

This should be fronted by a reverse proxy which checks that each request is associated with a valid login by asking this service to provide the user id for the provided credentials associated with the request.

This service should either provide the user id or deny the request if invalid credentials are provided.

There are two types of credentials that can be provided. Either a web session id or an API token.

These are obtained by logging in to this service and then requesting an API token.

## User IDs and Other Info

The provided user ids are in the form of UUIDs. Personal details such as username/alias/nicknames or First Names etc, are not in the scope of this service.

This service deliberately tries to limit the amount of personal information retained and ensures that what is stored can be administered by the user.

## Login Features

This uses the django-allauth app to provide the following login features:

* Login via email.
* Login via social accounts such as Facebook, Google and Apple.
* Login via multiple accounts.
* Removal of accounts.
* Email verification.
* Password reset.

## API Token Features

This uses the djangorestframework app provide API access tokens for authentication to things like Rest APIs. Once logged in with a session, you can retrieve an API token. Note that API tokens must be logged out from separately to the session ID login.

## Other Features

This also provides:

* An administrator webpage.

## Endpoints

/auth/admin/login/ - Web endpoint for a Server administration page.
/auth/accounts/login/ - Web endpoint for login screens.
/auth/accounts/logout - Web/API endpoint to sign out of
/auth/accounts/email - Web endpoint for a User account management page.
/auth/token/login/ - API endpoint to obtain login token from an authenticated session id.
/auth/token/logout/ - API endpoint to sign out.
/auth/user/ - API endpoint to verify the user is authenticated and retrieve their user id.
/auth/static/ - Frontend files.

XXX TODO
XXX TODO - add account deletion.
XXX TODO - document the keeptokens functionality of logout.

## Authentication Parameters

(Header) Cookie: csrftoken=...; sessionid=...

or

(Header) Authorization: Token ...

## Setup

* Make .env file (from .env.example)
* pipenv update
* Deploy behind a hardened webserver.

## TESTING

Regression tests:

    pipenv run authenticator/manage.py test

Run test server:

    pipenv run authenticator/manage.py runserver

## UNTESTED FUNCTIONALITY

These need regression tests:

* XXX test social login (make a test provider)
* XXX test UUID4 based usernames with social login
* XXX test social providers listed in views doesn't include ones not configured in admin.