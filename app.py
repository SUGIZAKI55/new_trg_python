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
import sqlite3  # 追加
import bcrypt # 追加 (password_hash を扱うため)

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

def init_db():  # 追加
    conn = sqlite3.connect('sugizaki.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            Q_no TEXT,
            genre TEXT,
            title TEXT NOT NULL,
            choices TEXT,
            answer TEXT,
            explanation TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.before_request  # 修正: before_first_request -> before_request
def initialize_database():
    initialize_database.initialized = getattr(initialize_database, 'initialized', False)
    if not initialize_database.initialized:
        init_db()
        initialize_database.initialized = True

@app.route('/')
def index():
    return redirect(url_for('auth.login_form'))

if __name__ == "__main__":
    init_db()  # 念のためここにも記述
    app.run(debug=True, port=8888)