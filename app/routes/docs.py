from flask import Blueprint, jsonify, render_template_string
from app.docs import build_spec

docs_bp = Blueprint("docs", __name__)

SWAGGER_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Teleconsultation API - Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({ url: '/openapi.json', dom_id: '#swagger-ui' });
    };
  </script>
</body>
</html>
"""


@docs_bp.get("/openapi.json")
def openapi_json():
    return jsonify(build_spec())


@docs_bp.get("/docs")
def swagger_ui():
    return render_template_string(SWAGGER_HTML)
