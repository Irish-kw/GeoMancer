#!/usr/bin/env bash
# GeoMancer-only environment setup (does not modify other conda envs or project folders).
set -euo pipefail

ENV_NAME="geomancer"
REQ_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/requirements.txt"

if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "Removing existing conda env: ${ENV_NAME}"
  conda env remove -n "${ENV_NAME}" -y
fi

echo "Creating ${ENV_NAME} with Python 3.9"
conda create -n "${ENV_NAME}" python=3.9 pip -y

echo "Installing system-linked deps via conda-forge (geomancer env only)"
conda install -n "${ENV_NAME}" -c conda-forge pycairo=1.21.0 -y

echo "Upgrading pip in ${ENV_NAME}"
conda run -n "${ENV_NAME}" python -m pip install -U pip wheel
conda run -n "${ENV_NAME}" python -m pip install 'setuptools>=69,<82'

echo "Installing GeoMancer requirements"
conda run -n "${ENV_NAME}" python -m pip install -r "${REQ_FILE}"

echo "Done. Activate with: conda activate ${ENV_NAME}"
