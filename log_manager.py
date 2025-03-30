# log_manager.py
import json

def log_w(data):
    with open('log.ndjson', 'a', encoding='utf-8') as file:
        json_string = json.dumps(data, ensure_ascii=False)
        file.write(json_string + '\n')
        print("データを改行区切りJSON形式で保存しました。")
