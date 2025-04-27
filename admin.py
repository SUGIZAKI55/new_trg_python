# admin.py
from flask import Blueprint, render_template, session, request, abort, redirect, url_for, g
import json
from datetime import datetime
import logging
from quiz import quiz_questions  # 明示的にインポート

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = sqlite3.connect('sugizaki.db')
        conn.row_factory = sqlite3.Row
    return conn

@admin_bp.teardown_request
def close_db(error):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@admin_bp.route('/view', methods=['GET'])
def view():
    filename = "log.ndjson"
    result_data = {}
    username = session.get('username')
    ans = {}
    if not username:
        return redirect(url_for('auth.login_form'))

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line.strip())
                    name = record.get("name")
                    if not name:
                        continue
                    genres = [g.strip() for g in record.get("genre", "不明").split(":")]
                    result = record.get("result")
                    question_id = record.get("question_id", "不明")
                    if name not in result_data:
                        result_data[name] = {}
                    for genre in genres:
                        if genre not in result_data[name]:
                            result_data[name][genre] = {"correct": 0, "total": 0, "error": []}
                        result_data[name][genre]["total"] += 1
                        if result and result.strip() == "正解":
                            result_data[name][genre]["correct"] += 1
                        elif result:
                            result_data[name][genre]["error"].append(question_id)
                except json.JSONDecodeError:
                    logger.error(f"JSON デコードエラー: 行をスキップしました - {line.strip()}")
                except Exception as e:
                    logger.error(f"ログ解析中に予期しないエラーが発生しました: {e}")

        ans = result_data.get(username, {})
    except FileNotFoundError:
        logger.warning(f"ログファイル '{filename}' が見つかりません。")
        ans = {}
    except Exception as e:
        logger.error(f"ログファイル処理中に予期しないエラーが発生しました: {e}")
        ans = {}

    return render_template('admin.html', ans=ans,username=username)

@admin_bp.route('/retry/<question_id>', methods=['GET'])
def retry_question(question_id):
    quiz_item = next((q for q in quiz_questions if q[0] == question_id), None)
    if quiz_item is None:
        abort(404, description="問題が見つかりませんでした。")
    session["qmap"] = [question_id]
    session["number"] = 1
    genre=request.args.get('genre', 'Unknown')
    session["current_question_id"] = question_id
    answer_choices = quiz_item[3].split(":")
    max_choices = min(len(answer_choices), 4)
    session["isRetry"]=True
    session["kaisetu"]= quiz_item[5]
    selected_choices = random.sample(answer_choices, max_choices)
    session["selected_choices"] = selected_choices
    correct_answers_temp = set(quiz_item[4].split(":"))
    session["correct_ans"] = set(selected_choices) & correct_answers_temp
    session["genre_name"] = genre
    session["start_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('question.html', question=quiz_item[2], choices=selected_choices, genre_name=genre)