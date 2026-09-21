from app import create_app
import os

app = create_app(os.environ.get("FLASK_ENV", "dev"))

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
