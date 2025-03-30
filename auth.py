# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# データベース接続設定
def create_db_connection():
    connection = sqlite3.connect('sugizaki.db')
    return connection

# ユーザーの認証を行う関数
def authenticate_user(username, password):
    connection = create_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            query = "SELECT password_hash FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            selected_choices = cursor.fetchone()
            if selected_choices:
                hashed_password = selected_choices[0]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()
    return False

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = create_db_connection()
        if connection is not None:
            try:
                cursor = connection.cursor()
                query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                cursor.execute(query, (username, hashed_password))
                connection.commit()
                cursor.close()
                connection.close()
                return redirect(url_for('login_form'))
            except sqlite3.Error as e:
                print(f"The error '{e}' occurred")
                return render_template('error.html')
    return render_template("signup.html")

# 認証用関数
def auth(request,session,redirect,url_for,render_template):
  username = request.form['username']
  password = request.form['password']

  if authenticate_user(username, password):
      session['username'] = username
      return redirect(url_for('loginok'))
  else:
      return render_template('error.html')

def logout(session,redirect,url_for):
  session.pop('username', None)
  session.clear()
  return redirect(url_for('login_form'))
