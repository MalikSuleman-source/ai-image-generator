from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import base64
import io
from datetime import datetime

app = Flask(__name__)

HF_API_KEY = os.environ.get('HF_API_KEY')

MODELS = {
    "realistic": "stabilityai/stable-diffusion-2-1",
    "anime": "hakurei/animagine-xl-3.1",
    "artistic": "runwayml/stable-diffusion-v1-5",
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    style = data.get('style', 'realistic')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    model = MODELS.get(style, MODELS['realistic'])
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return jsonify({
                'success': True,
                'image': image_base64,
                'prompt': prompt,
                'style': style,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({'error': 'Model is loading, please try again in 20 seconds'}), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
