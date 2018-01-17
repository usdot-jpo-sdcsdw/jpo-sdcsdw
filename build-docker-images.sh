#!/bin/bash

source build-docker-images.env

set -x

docker build -t $FEDGOV_CV_SSO_WEBAPP_IMAGE_NAME:$FEDGOV_CV_SSO_WEBAPP_IMAGE_VERSION fedgov-cv-sso-webapp
docker build -t $FEDGOV_CV_WHTOOLS_WEBAPP_IMAGE_NAME:$FEDGOV_CV_WHTOOLS_WEBAPP_IMAGE_VERSION fedgov-cv-whtools-webapp
docker build -t $FEDGOV_CV_MESSAGE_VALIDATOR_WEBAPP_IMAGE_NAME:$FEDGOV_CV_MESSAGE_VALIDATOR_WEBAPP_IMAGE_VERSION fedgov-cv-message-validator-webapp
docker build -t $CREDENTIALS_DB_IMAGE_NAME:$CREDENTIALS_DB_IMAGE_VERSION credentials-db
docker build -t $TIM_DB_IMAGE_NAME:$TIM_DB_IMAGE_VERSION tim-db