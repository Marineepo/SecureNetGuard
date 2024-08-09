from flask import Flask, request, jsonify
import ssl
import logging
from logging.handlers import RotatingFileHandler
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

handler = RotatingFileHandler('securenetguard.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

policies = {
    "blocked_domains": ["example.com", "badwebsite.com"]
}

@app.route('/api/policies', methods=['POST'])
def update_policies():
    data = request.json
    policies.update(data)
    socketio.emit('policy_update', policies)
    app.logger.info('Policies updated', policies)
    return jsonify({"status": "success", "data": policies})

@socketio.on('connect')
def handle_connect():
    emit('policy_update', policies)
    app.logger.info('Client connected')

@app.route('/api/logs', methods=['POST'])
def log_event():
    data = request.json
    app.logger.info(f"Log: {data}")
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('cert.pem', 'key.pem')
    socketio.run(app, ssl_context=context, debug=True)
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # context.load_cert_chain('cert.pem', 'key.pem')
    # app.run(ssl_context=context, debug=True)
