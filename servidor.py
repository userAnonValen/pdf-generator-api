from flask import Flask, request, send_file
import tempfile
from generar_catalogo import generar_pdf  # tu función que genera el PDF

app = Flask(__name__)
TOKEN = "MI_TOKEN_SEGURO"  # cambialo por algo tuyo

@app.route("/generar-pdf", methods=["POST"])
def generar():
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {TOKEN}":
        return {"error": "Unauthorized"}, 401

    data = request.json
    output_path = tempfile.mktemp(suffix=".pdf")
    generar_pdf(data, output_path)
    return send_file(output_path, as_attachment=True, download_name="catalogo.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
