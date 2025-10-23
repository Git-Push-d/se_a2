#!/usr/bin/env python3
"""
Run script for the Community Service Tracker application.
This starts the Flask web server.
"""
from wsgi import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
