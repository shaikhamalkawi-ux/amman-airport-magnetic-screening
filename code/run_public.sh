#!/usr/bin/env bash
set -euo pipefail
python code/analyse_public.py
python code/verify_public.py
