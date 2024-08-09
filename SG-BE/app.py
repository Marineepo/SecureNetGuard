from flask import Flask, request, jsonify
import ssl
import logging
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)
socketio = SocketIO(app)

users = {"admin": "password"} 

# SSL Context Configuration
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain('cert.pem', 'key.pem')

handler = RotatingFileHandler('securenetguard.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

policies = {
    "blocked_domains": ["example.com", "badwebsite.com"]
}

@app.before_request
def log_request_info():
    app.logger.info(f'User: {get_jwt_identity()}, Endpoint: {request.endpoint}, Method: {request.method}')


# Authentication endpoint
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

# Protect this route with JWT
@app.route('/api/policies', methods=['GET', 'POST'])
@jwt_required()
def policies():
    current_user = get_jwt_identity()
    # Add role-based access control here
    if current_user != "admin":
        return jsonify({"msg": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify(policies), 200
    if request.method == 'POST':
        data = request.json
        policies.update(data)
        socketio.emit('policy_update', policies)
        return jsonify({"status": "success", "data": policies}), 200

@app.route('/api/policies', methods=['POST'])
def update_policies():
    data = request.json
    policies.update(data)
    socketio.emit('policy_update', policies)
    return jsonify({"status": "success", "data": policies})

@socketio.on('connect')
def handle_connect():
    emit('policy_update', policies)
    app.logger.info('Client connected')

@app.route('/api/logs', methods=['POST'])
@jwt_required()
def log_event():
    data = request.json
    app.logger.info(f"Log: {data}, User: {get_jwt_identity()}")
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    socketio.run(app, ssl_context=context, debug=True)
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # context.load_cert_chain('cert.pem', 'key.pem')
    # app.run(ssl_context=context, debug=True)
