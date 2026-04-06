from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
import urllib.request

app = Flask(__name__, static_folder='.')

DATA_FILE = 'responses.json'
GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbz_p7Hit6jlQtXV2hWmRAlTilbhrAXRBHrA-YmQiuaAEb_J-LdDndGcZYcNqrZ8iRSq/exec'

def send_to_google_sheet(data):
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            GOOGLE_SHEET_URL,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f'[구글 시트 전송 실패] {e}')

def load_responses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_responses(responses):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

@app.route('/')
def survey():
    return send_from_directory('.', 'survey.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    if not data:
        return jsonify({'error': '데이터가 없습니다.'}), 400
    responses = load_responses()
    data['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['id'] = len(responses) + 1
    responses.append(data)
    save_responses(responses)
    send_to_google_sheet(data)
    return jsonify({'success': True, 'message': '설문이 성공적으로 제출되었습니다.'})

@app.route('/api/results')
def results():
    return jsonify(load_responses())

@app.route('/api/summary')
def summary():
    responses = load_responses()
    if not responses:
        return jsonify({'total': 0})

    out = {
        'total': len(responses),
        'level': {},
        'style': {},
        'intensity': {},
        'goals': {},
    }

    for r in responses:
        for key in ('level', 'style', 'intensity'):
            val = r.get(key, '')
            if val:
                out[key][val] = out[key].get(val, 0) + 1
        for g in r.get('goals', []):
            out['goals'][g] = out['goals'].get(g, 0) + 1

    return jsonify(out)

@app.route('/api/delete/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    responses = [r for r in load_responses() if r.get('id') != response_id]
    save_responses(responses)
    return jsonify({'success': True})

@app.route('/api/reset', methods=['DELETE'])
def reset_all():
    save_responses([])
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n🧘 MBC 경영센터 요가 설문 서버")
    print("━" * 35)
    print("📋 설문 페이지   →  http://localhost:5000")
    print("📊 관리자 페이지 →  http://localhost:5000/admin")
    print("━" * 35 + "\n")
    app.run(debug=True, port=5000)
