import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import ssl
import logging
from logging.handlers import RotatingFileHandler
from flask_socketio import SocketIO, emit
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry for monitoring and error tracking
sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

app = Flask(__name__)

# Load SSL certificates from environment variables
SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', 'path/to/your/cert.pem')
SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', 'path/to/your/key.pem')

# Load Secret Keys from environment variables
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
BITBUCKET_SECRET_KEY = os.environ.get('BITBUCKET_SECRET_KEY')

# Initialize JWT
jwt = JWTManager(app)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app)

# Setup rotating log file handler
handler = RotatingFileHandler('securenetguard.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Dummy user store (use a proper database in production)
users = {"admin": "password"}  # Replace with actual user management system

# Policy storage (this should be replaced by a persistent data store in production)
policies = {
    "blocked_domains": ["example.com", "badwebsite.com"]
}

@app.before_request
def log_request_info():
    user = get_jwt_identity() if request.endpoint != 'login' else 'Unauthenticated'
    app.logger.info(f'User: {user}, Endpoint: {request.endpoint}, Method: {request.method}')

# Authentication endpoint
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

# Policy management endpoint (protected)
@app.route('/api/policies', methods=['GET', 'POST'])
@jwt_required()
def manage_policies():
    current_user = get_jwt_identity()
    
    # Role-based access control
    if current_user != "admin":
        return jsonify({"msg": "Unauthorized"}), 403
    
    if request.method == 'GET':
        return jsonify(policies), 200
    
    if request.method == 'POST':
        data = request.json
        policies.update(data)
        socketio.emit('policy_update', policies)
        return jsonify({"status": "success", "data": policies}), 200

# Logging endpoint (protected)
@app.route('/api/logs', methods=['POST'])
@jwt_required()
def log_event():
    data = request.json
    app.logger.info(f"Log: {data}, User: {get_jwt_identity()}")
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    # SSL context setup
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)
    socketio.run(app, ssl_context=context, debug=True)
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # context.load_cert_chain('cert.pem', 'key.pem')
    # app.run(ssl_context=context, debug=True)

#Environment Variables for SSL & Secret Keys:
#The SSL_CERT_PATH, SSL_KEY_PATH, JWT_SECRET_KEY, AWS_SECRET_KEY, and BITBUCKET_SECRET_KEY are loaded from environment variables.
#This approach allows you to securely manage sensitive information without hardcoding it in the application.
#JWT Configuration:
#The JWT secret key is now loaded from an environment variable, enhancing security.
#SSL Context:
#The SSL certificates are used to secure the Flask application by loading them into the SSL context.

#You will need to set up environment variables on the systems where the app is running:
#export SSL_CERT_PATH="/path/to/your/cert.pem"
#export SSL_KEY_PATH="/path/to/your/key.pem"
#export JWT_SECRET_KEY="your_jwt_secret_key"
#export AWS_SECRET_KEY="your_aws_secret_key"
#export BITBUCKET_SECRET_KEY="your_bitbucket_secret_key"

#For Windows, you can set these environment variables through the System Properties or using the command prompt:
#set SSL_CERT_PATH=C:\path\to\your\cert.pem
#set SSL_KEY_PATH=C:\path\to\your\key.pem
#set JWT_SECRET_KEY=your_jwt_secret_key
#set AWS_SECRET_KEY=your_aws_secret_key
#set BITBUCKET_SECRET_KEY=your_bitbucket_secret_key