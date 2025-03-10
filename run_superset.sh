!bin/bash
export SUPERSET_CONFIG_PATH=~/HiringChallengeDataEngineer/superset_config.py
. ~/HiringChallengeDataEngineer/.venv/bin/activate
gunicorn \
  -w 10 \
      -k gevent \
      --worker-connections 1000 \
      --timeout 120 \
      -b  0.0.0.0:8088 \
      --limit-request-line 0 \
      --limit-request-field_size 0 \
      "superset.app:create_app()"