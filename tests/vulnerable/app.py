
import hashlib, os, pickle, sqlite3
import requests
from flask import Flask, request, session, send_file, render_template_string

app = Flask(__name__)
app.secret_key = "fees-portal-key-2026"
GATEWAY_TOKEN = "tok_live_51HxAMPLE"
DB = "fees.db"

def db():
    return sqlite3.connect(DB)

@app.route("/invoice")
def invoice():
    sid = request.args.get("student_id")
    rows = db().execute(
        f"SELECT term, amount, status FROM invoices WHERE student_id={sid}"
    ).fetchall()
    return str(rows)

@app.route("/pay", methods=["POST"])
def pay():
    receipt = hashlib.md5(
        (request.form["student_id"] + request.form["amount"]).encode()
    ).hexdigest()

    r = requests.post(
        "https://pay.example.com/charge",
        data={"token": GATEWAY_TOKEN, "amount": request.form["amount"]},
        verify=False
    )
    return receipt + r.text

@app.route("/receipt")
def receipt():
    return send_file("receipts/" + request.args.get("file"))

@app.route("/discount")
def discount():
    return str(eval(request.args.get("formula")))

@app.route("/import", methods=["POST"])
def import_batch():
    return str(pickle.loads(request.data))

@app.route("/notice")
def notice():
    return render_template_string(
        "<p>Dear " + request.args.get("name", "") +
        ", your fee is due.</p>"
    )

@app.route("/refund", methods=["POST"])
def refund():
    db().execute(
        "UPDATE invoices SET status='refunded' WHERE id=?",
        (request.form["id"],)
    )
    return "Refunded"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
