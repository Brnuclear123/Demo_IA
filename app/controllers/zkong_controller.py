from flask import request, jsonify
from app.services.zkong_connection import get_or_upload_to_publish
from app.services.utils.slogan_video_generator import SloganVideoGenerator

def publish_content():
    try:
        data = request.get_json()
        print("Data: ", data)
        data_slogan = data.get('slogan')
        brand = data.get('brand')

        generator = SloganVideoGenerator(brand)
        video_path = generator.process_and_add_text(data_slogan)
        
        result = get_or_upload_to_publish(video_path)
        return jsonify({'status': 'success', 'message': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500