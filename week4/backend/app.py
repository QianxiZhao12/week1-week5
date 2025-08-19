
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

@app.route('/api/get-param', methods=['GET'])
def get_param():
    """处理GET请求，获取URL参数"""
    param = request.args.get('param', '')
    return jsonify({
        'message': f'参数是{param}',
        'status': 'success'
    })

@app.route('/api/post-data', methods=['POST'])
def post_data():
    """处理POST请求，获取body和param"""
    # 获取URL参数
    url_param = request.args.get('param', '')
    
    # 获取请求体数据
    data = request.get_json()
    body_param = data.get('body_param', '') if data else ''
    
    return jsonify({
        'message': f'body中的参数是{body_param}，param中的参数是{url_param}',
        'status': 'success'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5050, host='0.0.0.0')