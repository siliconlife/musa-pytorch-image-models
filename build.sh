#!/bin/bash

pip install build

rm -rf dist .pdm-build

python -m build