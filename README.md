# Contents
* [Host Configuration](piswarm/hosts/raspberrypi/README.md)
* [Authentication Microservice](piswarm/services/authenticator/README.md)
* [Project Deployment](piswarm/deploy/README.md)

# TODO
* sort out all the storage volumes and update the docker files.
* docker secret security (password on master startup)
* switch to ansible for Host Configuration.

# Gateway configuration
Place a conf.d file into the shared-gateway docker volume and it will be injected into the nginx configuration.
