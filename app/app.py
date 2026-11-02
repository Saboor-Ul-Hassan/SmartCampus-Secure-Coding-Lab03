
import os
import hmac
import hashlib
import sqlite3
import json
import re
from pathlib import Path
from functools import wraps

import requests
from flask import (
    Flask, request, session, abort,
    send_file, jsonify, render_template
)

app = Flask(__name__)

# Secure environment-based configuration
app.secret_key = os.environ["FLASK_SECRET_KEY"]
GATEWAY_TOKEN = os.environ["GATEWAY_TOKEN"]
RECEIPT_HMAC_KEY = os.environ["RECEIPT_HMAC_KEY"]

DB = "fees.db"
RECEIPT_DIR = Path("receipts").resolve()


def db():
    return sqlite3.connect(DB)


# Role-based access control
def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Student invoice ownership check
@app.route("/invoice")
@require_role("student", "bursar")
def invoice():
    sid = request.args.get("student_id")

    if not sid or not sid.isdigit():
        abort(400)

    if session.get("role") == "student":
        if str(session.get("student_id")) != sid:
            abort(403)

    connection = db()
    try:
        rows = connection.execute(
            "SELECT term, amount, status FROM invoices WHERE student_id = ?",
            (sid,)
        ).fetchall()
    finally:
        connection.close()

    return jsonify(rows)


# Secure payment processing
@app.route("/pay", methods=["POST"])
@require_role("student")
def pay():
    student_id = request.form.get("student_id", "")
    amount = request.form.get("amount", "")

    if not student_id.isdigit():
        abort(400)

    if str(session.get("student_id")) != student_id:
        abort(403)

    try:
        amount_value = float(amount)
        if not 0 < amount_value <= 1000000:
            abort(400)
    except (ValueError, TypeError):
        abort(400)

    receipt = hmac.new(
        RECEIPT_HMAC_KEY.encode(),
        f"{student_id}:{amount_value:.2f}".encode(),
        hashlib.sha256
    ).hexdigest()

    response = requests.post(
        "https://pay.example.com/charge",
        data={
            "token": GATEWAY_TOKEN,
            "amount": f"{amount_value:.2f}"
        },
        timeout=10
    )

    response.raise_for_status()
    return jsonify({
        "receipt": receipt,
        "payment_status": "submitted"
    })


# Secure receipt file access
@app.route("/receipt")
@require_role("student", "bursar")
def receipt():
    filename = request.args.get("file", "")

    if not filename or Path(filename).name != filename:
        abort(400)

    file_path = (RECEIPT_DIR / filename).resolve()

    if not file_path.is_relative_to(RECEIPT_DIR):
        abort(400)

    if not file_path.is_file():
        abort(404)

    if session.get("role") == "student":
        student_id = str(session.get("student_id", ""))
        if not filename.startswith(student_id + "_"):
            abort(403)

    return send_file(file_path)


# Safe discount calculation without eval()
@app.route("/discount")
@require_role("student", "bursar")
def discount():
    percent = request.args.get("percent", "")

    try:
        value = float(percent)
    except (ValueError, TypeError):
        abort(400)

    if not 0 <= value <= 100:
        abort(400)

    return jsonify({"discount_percent": value})


# Safe JSON import instead of pickle
@app.route("/import", methods=["POST"])
@require_role("bursar")
def import_batch():
    try:
        data = json.loads(request.data)
    except (ValueError, UnicodeDecodeError):
        abort(400)

    if not isinstance(data, list):
        abort(400)

    for item in data:
        if not isinstance(item, dict):
            abort(400)

        if not {"student_id", "amount"}.issubset(item):
            abort(400)

        if not str(item["student_id"]).isdigit():
            abort(400)

        try:
            amount = float(item["amount"])
        except (ValueError, TypeError):
            abort(400)

        if not 0 < amount <= 1000000:
            abort(400)

    return jsonify({
        "message": "Batch data validated",
        "records": len(data)
    })


# Safe HTML template rendering
@app.route("/notice")
@require_role("student", "bursar")
def notice():
    name = request.args.get("name", "")

    return render_template(
        "notice.html",
        name=name
    )


# Bursar-only refund operation
@app.route("/refund", methods=["POST"])
@require_role("bursar")
def refund():
    invoice_id = request.form.get("id", "")

    if not invoice_id.isdigit():
        abort(400)

    connection = db()
    try:
        cursor = connection.execute(
            "UPDATE invoices SET status = ? WHERE id = ?",
            ("refunded", invoice_id)
        )
        if cursor.rowcount == 0:
            abort(404)
        connection.commit()
    finally:
        connection.close()

    return "Refund processed successfully"


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
