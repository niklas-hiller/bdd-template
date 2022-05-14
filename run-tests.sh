#!/bin/bash

echo "Running pytest in ${ENVIRONMENT}."
pytest --env=${ENVIRONMENT} \
--cucumberjson=cucumber.json \
--junitxml=report.xml