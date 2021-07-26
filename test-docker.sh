#!/bin/bash

set -e

# remove caches
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

VERSIONS=('2.7' '3.4' '3.5' '3.6' '3.7' '3.8')
# VERSIONS=('2.7')

for i in "${VERSIONS[@]}"
do

    if [[ "$(docker images -q stackify-python-api-test-${i}:latest 2> /dev/null)" != "" ]]; then
        echo "Delete stackify-python-api-test-${i}..."
        docker rm stackify-python-api-test-${i} &>/dev/null
        docker rmi stackify-python-api-test-${i}:latest &>/dev/null
    fi

    echo "Building stackify-python-api-test-${i}..."
    docker build --no-cache --build-arg from_version=${i} --build-arg version=${i} --build-arg test=${TEST} --build-arg test_repo=${TEST_REPO} --file docker/stackify-python-api-test . -t stackify-python-api-test-${i}:latest

    echo "Running stackify-python-api-test-${i}..."
    docker run --network="host" --name "stackify-python-api-test-${i}"  stackify-python-api-test-${i}:latest

    echo "Delete stackify-python-api-test-${i}..."
    docker rm stackify-python-api-test-${i} &>/dev/null
    docker rmi stackify-python-api-test-${i}:latest &>/dev/null

done

echo "Done"
