#!/bin/bash

##
# Ensure you have set up the piswarm docker context:
#     docker context create piswarm --docker "host=ssh://piswarmdeploy"
#


cd `dirname $0`

set -x

docker --context piswarm build -t piswarm-gateway -f ../containers/piswarm-gateway/dockerfile ../../services/gateway
docker --context piswarm build -t piswarm-authenticator -f ../containers/piswarm-authenticator/dockerfile ../../services/authenticator
docker --context piswarm build -t piswarm-authenticator-proxy ../containers/piswarm-authenticator-proxy
docker --context piswarm build -t piswarm-secure-mysql ../containers/piswarm-secure-mysql
docker --context piswarm build -t piswarm-socat ../containers/piswarm-socat