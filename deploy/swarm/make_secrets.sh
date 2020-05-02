#!/bin/bash

cd `dirname $0`

set -x

ln -s ~/Private/piswarm/secrets secrets

openssl rand -hex 64 | tr -d '\n' \
    > secrets/mysql_authenticator_password

openssl rand -hex 32  | sed -e 's:^:1;:' \
    > secrets/mysql_authenticator_encryption_key

openssl rand -hex 64 | tr -d '\n' \
    > secrets/mysql_authenticator_password

openssl rand -hex 64 | tr -d '\n' \
    > secrets/authenticator_secret_key

vim secrets/authenticator_email_user

vim secrets/authenticator_email_password

vim secrets/authenticator_superuser_password
