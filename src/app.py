import os

from flask import Flask, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-insecure")


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


@app.route("/")
def home():
    return jsonify({"message": "Bienvenue sur mon API", "status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/hello/<name>")
def hello(name):
    return jsonify({"message": f"Bonjour {name} !"})


if __name__ == "__main__":
    app.run()


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    return jsonify({"result": a + b})


@app.route("/about")
def about():
    return jsonify({"app": "Mon projet Flask", "version": "1.0"})
