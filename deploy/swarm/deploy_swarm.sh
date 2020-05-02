#!/bin/bash

##
# Ensure you have set up the piswarm docker context:
#     docker context create piswarm --docker "host=ssh://piswarmdeploy"
#


cd `dirname $0`

set -x


# Hook up the docker registry to be connectable
[ -z "$(docker --context piswarm ps --filter name=docker-registry-hook -q)" ] \
&& docker --context piswarm run --restart=always -it --net=piswarm_admin -d \
    --name docker-registry-hook --publish 127.0.0.1:5000:5000 \
    piswarm-socat \
    tcp-listen:5000,fork,reuseaddr \
    tcp-connect:docker-registry:5000

# Start the base services so we can deploy from it
[ -z "$(docker --context piswarm stack ps --filter name=piswarm_docker-registry -q piswarm)" ] \
&& docker --context piswarm stack deploy -c ./docker-compose.base.yaml piswarm

# Push all local images in case there has been updates
docker --context piswarm tag piswarm-gateway 127.0.0.1:5000/piswarm-gateway
docker --context piswarm tag piswarm-authenticator 127.0.0.1:5000/piswarm-authenticator
docker --context piswarm tag piswarm-authenticator-proxy 127.0.0.1:5000/piswarm-authenticator-proxy
docker --context piswarm tag piswarm-secure-mysql 127.0.0.1:5000/piswarm-secure-mysql
docker --context piswarm push 127.0.0.1:5000/piswarm-gateway
docker --context piswarm push 127.0.0.1:5000/piswarm-authenticator
docker --context piswarm push 127.0.0.1:5000/piswarm-authenticator-proxy
docker --context piswarm push 127.0.0.1:5000/piswarm-secure-mysql

# Check what will need to be initialised
[ -z "$(docker --context piswarm stack ps --filter name=piswarm_authenticator-mysql -q piswarm)" ] && authenticator_mysql_init=1

# Deploy all the services to the swarm
docker --context piswarm stack deploy -c ./docker-compose.base.yaml -c ./docker-compose.yaml --prune piswarm

# Initialize databases
if [ "$authenticator_mysql_init" = "1" ]; then
  # Ensure logs land on encrypted storage
  cat `pwd`/secrets/mysql_authenticator_password | \
    docker --context piswarm run --net piswarm_authenticator-mysql -i --rm --name authenticator-mysql-init linuxserver/mariadb \
      bash -c 'printf "[client]\nuser=root\npassword=" > /tmp/client.config \
          && cat - >> /tmp/client.config \
          && echo "\
              SET GLOBAL log_output = '\''TABLE'\''; \
              SET GLOBAL general_log = OFF; \
              ALTER TABLE mysql.general_log ENGINE=Aria; \
              SET GLOBAL general_log = ON; \
              SET GLOBAL slow_query_log = OFF; \
              ALTER TABLE mysql.slow_log ENGINE=Aria; \
              SET GLOBAL slow_query_log = ON;\
              " | mysql --defaults-extra-file=/tmp/client.config -hauthenticator-mysql'
fi
