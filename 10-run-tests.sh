#!/bin/bash

echo "Running pytest in ${ENVIRONMENT}."
pytest --env=${ENVIRONMENT} \
--cucumberjson=${CUCUMBER_PATH} \
--junitxml=${JUNIT_PATH}