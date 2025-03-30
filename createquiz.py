from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

createquiz_bp = Blueprint('createquiz', __name__)

# データベース接続設定
def create_db_connection():
    connection = sqlite3.connect('sugizaki.db')
    return connection

# 問題をデータベースから読み込む関数
def load_questions():
    connection = create_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            query = "SELECT rowid, Q_no, genre, title, choices, answer, explanation FROM quiz_questions"
            cursor.execute(query)
            questions = cursor.fetchall()
            return questions
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# 問題をデータベースに保存する関数
def save_questions(questions):
    connection = create_db_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM quiz_questions")
            for q in questions:
                query = "INSERT INTO quiz_questions (Q_no, genre, title, choices, answer, explanation) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(query, q[1:])
            connection.commit()
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()

@createquiz_bp.route('/q_list')
def q_list():
    questions = load_questions()
    return render_template('q_list.html', questions=questions)

@createquiz_bp.route('/editQuiz')
def editQuiz():
    questions = load_questions()
    return render_template('q_list.html', questions=questions)

@createquiz_bp.route('/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    questions = load_questions()
    question = None
    for q in questions:
      if q[0]==question_id:
        question =q
        break;

    if request.method == 'POST':
        # フォームからデータを取得して更新
        updated_question = (
            request.form['Q_no'],
            request.form['genre'],
            request.form['title'],
            request.form['choices'],
            request.form['answer'],
            request.form['explanation']
        )
        updated_questions = []
        for q in questions:
          if q[0] == question_id:
            updated_questions.append((question_id,*updated_question))
          else:
            updated_questions.append(q)

        save_questions(updated_questions)
        return redirect(url_for('createquiz.editQuiz'))

    return render_template('edit.html', question=question, question_id=question_id)

@createquiz_bp.route('/createQuiz')
def index2():
    return render_template('q_index.html')

@createquiz_bp.route('/createQuiz2', methods=['POST'])
def createQuiz2():
    title = request.form.get('title')
    genre = request.form.get('genre')
    choices = request.form.get('choices')
    answer = request.form.get('answer')
    explanation = request.form.get('explanation') or "なし"  # 空の場合はデフォルト値

    # 新しい問題を作成
    questions = load_questions()
    new_question = (
        len(questions),
        str(len(questions)),
        genre,
        title,
        choices,
        answer,
        explanation
    )

    # 問題をリストに追加し保存
    questions.append(new_question)
    save_questions(questions)
    return "登録が完了しました"