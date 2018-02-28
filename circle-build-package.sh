#!/usr/bin/env bash

if [ -z "$CI" ]; then
    echo "Will only continue on CI"
    exit
fi

if [[ $CIRCLE_BRANCH != "master" ]]; then
    echo "Will build on master branch"
    exit
fi

# build package and upload to private pypi index
echo "[distutils]" >> ~/.pypirc
echo "index-servers = pypi" >> ~/.pypirc
echo "[pypi]" >> ~/.pypirc
echo "username=$PYPI_USERNAME" >> ~/.pypirc
echo "password=$PYPI_PASSWORD" >> ~/.pypirc

python setup.py bdist_wheel
twine upload dist/*
