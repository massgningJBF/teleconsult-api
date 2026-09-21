import time
from flask import g, request


def register_security(app):
    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def apply_security(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        duration = (time.time() - g.get("start", time.time())) * 1000
        app.logger.info(
            "%s %s -> %s (%.1fms)", request.method, request.path, response.status_code, duration
        )
        return response
