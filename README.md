# Wentworth App

Flask web application — Wentworth coursework project.

## Overview
Simple Flask web app with templated pages and static assets.

## How to run
```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## Running tests
The test suite uses pytest and mocks the MySQL connection, so no database
server is needed to run it:

```bash
pip install -r requirements.txt
pytest tests/ -v
```
