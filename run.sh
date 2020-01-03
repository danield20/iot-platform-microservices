#!/bin/bash
if [ "$1" = "-s" ]; then
    docker stack rm sprc3
    docker service rm registry
else
    if [ "$1" = "-v" ]; then
        docker volume rm sprc3_db_data
    fi
    docker service create --name registry --publish published=5000,target=5000 registry:2
    docker-compose -f stack.yml build
    docker-compose -f stack.yml down -v
    docker-compose -f stack.yml push
    docker stack deploy -c stack.yml sprc3
fi