# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, g
import sqlite3
import bcrypt
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('sugizaki.db')
        conn.row_factory = sqlite3.Row
    return conn

@auth_bp.teardown_request
def close_db(error):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    cur.close()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif query_db('SELECT user_id FROM users WHERE username = ?', [username], one=True) is not None:
            error = f'User {username} is already registered.'
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            execute_db('INSERT INTO users (username, password_hash) VALUES (?, ?)', [username, hashed_password])
            return redirect(url_for('auth.login_form'))
    return render_template("signup.html", error=error)

@auth_bp.route('/login_form')
def login_form():
    error = request.args.get('error')
    return render_template('login.html', error=error)

@auth_bp.route('/login', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    if authenticate_user(username, password):
        session['username'] = username
        return redirect(url_for('admin.view')) # ログイン成功で admin へ
    else:
        return render_template('error.html', error='ログインに失敗しました')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('auth.login_form'))