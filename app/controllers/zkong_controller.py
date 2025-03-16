from flask import request, jsonify
from app.services.zkong_connection import get_or_upload_to_publish

def publish_content():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        result = get_or_upload_to_publish(file_path)
        return jsonify({'status': 'success', 'message': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500