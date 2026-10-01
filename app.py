import os
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=None)
DIST_DIR = Path(__file__).resolve().parent / "dist"
AWS_API_URL = os.environ.get(
    "AWS_API_URL", "https://zu3g6t4634.execute-api.us-east-1.amazonaws.com/v1/datos"
)


@app.get("/")
@app.get("/login")
def frontend():
    if not (DIST_DIR / "index.html").is_file():
        return "Primero ejecuta npm install y npm run build, o usa npm run dev para desarrollar.", 503
    return send_from_directory(DIST_DIR, "index.html")


@app.get("/assets/<path:filename>")
def frontend_assets(filename):
    return send_from_directory(DIST_DIR / "assets", filename)


@app.route("/api/registros", methods=["GET", "POST", "PUT", "DELETE"])
def registros():
    """Adaptador para AWS. El login visual no proporciona autenticación."""
    payload = None
    if request.method != "GET":
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify(error="Los datos enviados no son válidos."), 400
        fields = ("id",) if request.method == "DELETE" else ("id", "titulo", "autor")
        if not all(isinstance(payload.get(key), str) and payload[key].strip() for key in fields):
            return jsonify(error="Completa todos los campos requeridos."), 400
        payload = {key: payload[key].strip() for key in fields}
    try:
        response = requests.request(request.method, AWS_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        if request.method == "GET":
            data = response.json()
            if not isinstance(data, list):
                return jsonify(error="El servicio devolvió una respuesta inesperada."), 502
            return jsonify(data)
        return jsonify(ok=True)
    except (requests.RequestException, ValueError):
        app.logger.exception("No se pudo completar la operación con AWS")
        return jsonify(error="No pudimos conectar con el servicio. Intenta de nuevo."), 502


if __name__ == "__main__":
    app.run(debug=True)
