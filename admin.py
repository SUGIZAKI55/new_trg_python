# admin.py
from flask import Blueprint, render_template, session, request
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/view', methods=['GET'])
def view():
    filename = "log.ndjson"
    result_data = {}
    username = session['username']
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                record = json.loads(line.strip())
                name = record["name"]

                if "genre" in record and record["genre"]:
                    genres = record["genre"].strip().split(":")
                else:
                    genres = ["不明"]

                result = record["result"]
                question_id = record.get("question_id", "不明")
                for genre in genres:
                    if name not in result_data:
                        result_data[name] = {}
                    if genre not in result_data[name]:
                        result_data[name][genre] = {"correct": 0, "total": 0, "error": []}
                    result_data[name][genre]["total"] += 1
                    if result.strip() == "正解":
                        result_data[name][genre]["correct"] += 1
                    else:
                        result_data[name][genre]["error"].append(question_id)

        for name, genres in result_data.items():
            for genre, data in genres.items():
                total = data["total"]
                correct = data["correct"]
                error = data["error"]
                if total > 0:
                    accuracy = (correct / total) * 100
                else:
                    accuracy = 0
        ans = result_data[username]
    except FileNotFoundError:
        print(f"ファイル '{filename}' が見つかりません。")
    except json.JSONDecodeError:
        print("JSON データの解析中にエラーが発生しました。")
    return render_template('view.html', ans=ans)

@admin_bp.route('/retry/<question_id>', methods=['GET'])
def retry_question(question_id):
    quiz_item = None
    for q in quiz_questions:
        if q[0] == question_id:
            quiz_item = q
            break
    if quiz_item is None:
        return "問題が見つかりませんでした。", 404
    session["qmap"] = [question_id]
    session["number"] = 1

    genre=request.args.get('genre', 'Unknown')

    session["current_question_id"] = question_id
    answer_choices = quiz_item[3].split(":")
    
    if len(answer_choices) < 4:
        max_choices = len(answer_choices)
    else:
        max_choices = 4
    session["isRetry"]=True
    kaisetu = quiz_item[5]
    session["kaisetu"]=kaisetu
    selected_choices = random.sample(answer_choices, max_choices)
    session["selected_choices"] = selected_choices
    correct_answers_temp = set(quiz_item[4].split(":"))
    session["correct_ans"] = set(selected_choices) & correct_answers_temp
    session["genre_name"] = genre
    start_datetime = datetime.now()
    formatted_date_string = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
    session["start_datetime"] = formatted_date_string

    return render_template('question.html', question=quiz_item[2], choices=selected_choices, genre_name=genre)
