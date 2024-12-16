#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  celery -A online_shop worker --loglevel=info
elif [[ "${1}" == "flower" ]]; then
  celery -A online_shop flower
 fi

## скрипт для заруска по параметрам celery или flower