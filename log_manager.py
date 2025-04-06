# log_manager.py
import json
import logging

logger = logging.getLogger(__name__)

def log_w(data):
    try:
        log_message = json.dumps(data, ensure_ascii=False)
        logger.info(log_message)
    except Exception as e:
        logger.error(f"ログデータのJSONエンコードに失敗しました: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_w({"message": "テストログ"})