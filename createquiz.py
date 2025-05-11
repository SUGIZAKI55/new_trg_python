# createquiz.py
from flask import Blueprint, render_template, request, redirect, url_for, g, abort
import sqlite3
import logging

logger = logging.getLogger(__name__)
createquiz_bp = Blueprint('createquiz', __name__, url_prefix='/createquiz')

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('sugizaki.db')
        conn.row_factory = sqlite3.Row
    return conn

@createquiz_bp.teardown_request
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

@createquiz_bp.route('/q_list')
def q_list():
    questions = query_db("SELECT rowid, Q_no, genre, title, choices, answer, explanation FROM quiz_questions")
    return render_template('q_list.html', questions=questions)

@createquiz_bp.route('/editQuiz')
def editQuiz():
    return redirect(url_for('createquiz.q_list'))

@createquiz_bp.route('/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    error = None
    question = query_db("SELECT Q_no, genre, title, choices, answer, explanation FROM quiz_questions WHERE rowid = ?", [question_id], one=True)
    if question is None:
        abort(404, description="問題が見つかりませんでした。")

    if request.method == 'POST':
        q_no = request.form['Q_no']
        genre = request.form['genre']
        title = request.form['title']
        choices = request.form['choices']
        answer = request.form['answer']
        explanation = request.form['explanation']
        if not title:
            error = 'Title is required.'
        else:
            execute_db("UPDATE quiz_questions SET Q_no=?, genre=?, title=?, choices=?, answer=?, explanation=? WHERE rowid=?",
                       [q_no, genre, title, choices, answer, explanation, question_id])
            return redirect(url_for('createquiz.q_list'))

    return render_template('edit.html', question=question, question_id=question_id, error=error)

@createquiz_bp.route('/createQuiz')
def index2():
    return render_template('q_index.html')

@createquiz_bp.route('/createQuiz2', methods=['POST'])
def createQuiz2():
    error = None
    if request.method == 'POST':
        title = request.form.get('title')
        genre = request.form.get('genre')
        choices = request.form.get('choices')
        answer = request.form.get('answer')
        explanation = request.form.get('explanation') or "なし"

        if not title:
            error = 'Title is required.'
        else:
            execute_db("INSERT INTO quiz_questions (genre, title, choices, answer, explanation) VALUES (?, ?, ?, ?, ?)",
                       [genre, title, choices, answer, explanation])
            return redirect(url_for('createquiz.q_list'))



    return render_template('q_index.html', error=error)