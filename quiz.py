# quiz.py
from flask import Blueprint, render_template, session, request, redirect, url_for
import random
from datetime import datetime
from log_manager import log_w
import logging

logger = logging.getLogger(__name__)
quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

with open('quiz_questions.txt', 'r', encoding='utf-8') as file:
    content = file.read().strip()
questions = content.split('\n\n')
quiz_questions = []
for question in questions:
    parts = question.split('\n')
    if len(parts) == 6:
        quiz_questions.append(parts)

genre_to_ids = {}
for topic in quiz_questions:
    topic_id = topic[0]
    genre_list = topic[1].split(":")
    for genre in genre_list:
        if genre in genre_to_ids:
            genre_to_ids[genre].append(topic_id)
        else:
            genre_to_ids[genre] = [topic_id]

@quiz_bp.route('/question', methods=['GET'])
def question():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    else:
        Q_no = session["Q_no"]
        qmap = session["qmap"]
        qmaped_Q_no = qmap[Q_no]
        qmaped_Q_no = int(qmaped_Q_no)
        quiz_item = quiz_questions[qmaped_Q_no]
        question_id = quiz_item[0]
        session["current_question_id"] = question_id
        answer_choices = quiz_item[3].split(":")
        session["kaisetu"]=quiz_item[5]
        max_choices = min(len(answer_choices), 4)
        session["selected_choices"] = random.sample(answer_choices, max_choices)
        correct_answers_temp = set(quiz_item[4].split(":"))
        session["correct_ans"] = set(session["selected_choices"]) & correct_answers_temp
        session["start_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session["genre_name"] = session["genre_name"]
        return render_template('question.html', question=quiz_item[2], choices=session["selected_choices"], genre_name=session["genre_name"])

@quiz_bp.route('/answer', methods=['GET'])
def check_answer():
    selected_choices = session["selected_choices"]
    correct_ans = session.get("correct_ans", set())
    user_choice = request.args.getlist('choice[]')
    end_datetime = datetime.now()
    start_datetime = datetime.strptime(session["start_datetime"], '%Y-%m-%d %H:%M:%S')
    elapsed_time = end_datetime - start_datetime
    session["Q_no"] += 1
    user_choice_str = ', '.join(user_choice)
    correct_ans_str = ', '.join(correct_ans)
    answer = "正解" if set(user_choice) == correct_ans else f"不正解。正しい答えは: {', '.join(correct_ans)}"
    data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "name": session.get("username", "不明"),
        "genre": session["genre_name"],
        "qmap": session["qmap"],
        "question_id": session["current_question_id"],
        "start_time": start_datetime.strftime('%H:%M:%S'),
        "end_time": end_datetime.strftime('%H:%M:%S'),
        "elapsed_time": str(elapsed_time),
        "user_choice": user_choice,
        "correct_answers": list(correct_ans),
        "result": answer
    }
    log_w(data)
    logger.info(f"解説: {session.get('kaisetu')}")
    return render_template('kekka.html', answer=answer, et=str(elapsed_time), Q_no=session["Q_no"], user_choice=user_choice_str, correct_ans=correct_ans_str, kaisetu=session.get("kaisetu"), answer_feedback={c: ("○" if c in correct_ans else "×") for c in selected_choices})

@quiz_bp.route('/genre')
def genre():
    error = None
    return render_template('genre.html', error=error, genre_to_ids=genre_to_ids)

@quiz_bp.route('/firstquestion', methods=['POST'])
def firstquestion():
    genre_name = request.form.get('category')
    session["genre_name"] = genre_name
    genre_no = genre_to_ids[genre_name]
    session["genre_no"] = genre_no
    number = int(request.form['nanko'])
    session["number"] = number
    session["qmap"] = random.sample(genre_no, number)
    session["Q_no"] = 0
    session["isRetry"]=False
    return render_template('first.html')