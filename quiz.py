from flask import Blueprint, render_template, session, request, redirect, url_for
import random
from datetime import datetime
from log_manager import log_w #log_wをインポートします。

quiz_bp = Blueprint('quiz', __name__)

with open('quiz_questions.txt', 'r', encoding='utf-8') as file:
    content = file.read().strip()
questions = content.split('\n\n')
quiz_questions = []
for question in questions:
    parts = question.split('\n')
    if len(parts) == 6:
        quiz_questions.append(parts)

genre_to_ids = {}  # ジャンルとIDの対応を保持
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
        return redirect(url_for('login')) # login() のルートにリダイレクト
    else:
        Q_no = session["Q_no"]
        qmap = session["qmap"]
        qmaped_Q_no = qmap[Q_no]
        qmaped_Q_no = int(qmaped_Q_no)
        quiz_item = quiz_questions[qmaped_Q_no]

        # 問題IDを正確に保存
        question_id = quiz_item[0]
        session["current_question_id"] = question_id

        answer_choices = quiz_item[3].split(":")
        kaisetu = quiz_item[5]
        session["kaisetu"]=kaisetu

        if len(answer_choices) < 4:
            max_choices = len(answer_choices)
        else:
            max_choices = 4
        selected_choices = random.sample(answer_choices, max_choices)

        session["selected_choices"] = selected_choices
        correct_answers_temp = set(quiz_item[4].split(":"))
        correct_choices = set(selected_choices) & correct_answers_temp
        session["correct_ans"] = correct_choices

        start_datetime = datetime.now()
        formatted_date_string = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        session["start_datetime"] = formatted_date_string

        genre_name = session["genre_name"]
        return render_template('question.html', question=quiz_item[2], choices=selected_choices, genre_name=genre_name)

@quiz_bp.route('/answer', methods=['GET'])
def check_answer():
    selected_choices = session["selected_choices"]
    correct_ans = session.get("correct_ans", set())
    user_choice = request.args.getlist('choice[]')
    end_datetime = datetime.now()
    date_string = session["start_datetime"]
    start_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    elapsed_time = end_datetime - start_datetime
    elapsed_time_str = str(elapsed_time)
    user_set = set(user_choice)

    if user_set == correct_ans:
        answer = "正解"
    else:
        answer = f"不正解。正しい答えは: {', '.join(correct_ans)}"

    Q = session["Q_no"]
    Q += 1
    session["Q_no"] = Q

    user_choice_str = ', '.join(user_choice)
    correct_ans_str = ', '.join(correct_ans)

    data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "name": session.get("username", "不明"),
        "genre": session["genre_name"],
        "qmap": session["qmap"],
        "question_id": session["current_question_id"],
        "start_time": start_datetime.strftime('%H:%M:%S'),
        "end_time": end_datetime.strftime('%H:%M:%S'),
        "elapsed_time": elapsed_time_str,
        "user_choice": user_choice,
        "correct_answers": list(correct_ans),
        "result": answer
    }
    log_w(data) #ログの出力をする
    kst=session["kaisetu"]
    print(f"解説: {kst=}")
    return render_template('kekka.html', answer=answer, et=elapsed_time_str, Q_no=Q, user_choice=user_choice_str, correct_ans=correct_ans_str, kaisetu=session["kaisetu"],answer_feedback={c: ("○" if c in correct_ans else "×") for c in selected_choices})

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
    qmap = random.sample(genre_no, number)
    session["qmap"] = qmap
    Q_no = 0
    session["Q_no"] = Q_no
    session["isRetry"]=False
    return render_template('first.html')