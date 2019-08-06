#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

TARGET="/home/jovyan/work/DS1EDP"
REPO_URL="https://github.com/BigDaMa/DS1EDP"

if [[ -d ${TARGET} ]]; then
	echo "${TARGET} already exists"
else
	git clone ${REPO_URL} ${TARGET}
	chown jovyan:1024 -R ${TARGET}
fi

set -e

if [[ ! -z "${JUPYTERHUB_API_TOKEN}" ]]; then
  # launched by JupyterHub, use single-user entrypoint
  exec /usr/local/bin/start-singleuser.sh "$@"
elif [[ ! -z "${JUPYTER_ENABLE_LAB}" ]]; then
  . /usr/local/bin/start.sh jupyter lab "$@"
else
  . /usr/local/bin/start.sh jupyter notebook "$@"
fi
