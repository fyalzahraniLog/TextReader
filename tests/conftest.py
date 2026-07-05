import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)
# `import app` in test_api.py resolves server/app.py the same way the Docker
# image does (app.py at /app, the shared `pipeline` package alongside it).
sys.path.insert(0, os.path.join(_REPO_ROOT, "server"))
