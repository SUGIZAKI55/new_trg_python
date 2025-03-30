# app.py
from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
from datetime import timedelta
from auth import auth_bp, auth ,logout
from quiz import quiz_bp, quiz_questions, genre_to_ids
from log_manager import log_w
from admin import admin_bp
import random

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def login_form():
    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    return auth(request,session,redirect,url_for,render_template)

@app.route('/loginok')
def loginok():
    session["Q_no"] = 0
    if 'username' in session:
        username = session['username']
        return render_template('admin.html', username=username)
    else:
        return redirect(url_for('login_form'))

@app.route('/admin')
def admin():
    if 'username' in session:
        username = session['username']
        return render_template('admin.html', username=username)
    else:
        return redirect(url_for('login_form'))

@app.route('/logout')
def logout():
    return logout(session,redirect,url_for)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
