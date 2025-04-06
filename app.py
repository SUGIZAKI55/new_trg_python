# app.py
from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
from datetime import timedelta
from auth import auth_bp
from quiz import quiz_bp
from createquiz import createquiz_bp
from admin import admin_bp
import logging
import os

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here') # 環境変数から取得推奨
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(createquiz_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login_form'))

if __name__ == "__main__":
    app.run(debug=True, port=8888)