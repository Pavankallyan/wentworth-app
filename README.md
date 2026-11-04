
## Tests and CI
GitHub Actions runs `python -m py_compile app.py` and `pytest tests/` on
every push and pull request to `main` (see `.github/workflows/ci.yml`).
