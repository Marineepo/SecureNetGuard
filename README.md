1. Create a virtual environment
`python3 -m venv venv` 
`source venv/bin/activate`
On Windows, use `venv\Scripts\activate`
`pip install -r requirements.txt`
2. Generate SSL certificates (for development purposes):
`openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
3. Run npm run build
4. Run npm start
5. Run python app.py
Access Frontend at http://localhost:3000
Verify logs (`securenetguard.log`) and LogRocket server dashboard

# What this app does
1. JWT Authentication and Access Control (Flask)
    a. JWTManager is used for handling JWT-based authentication.
    b. login route issues a JWT upon successful login.
    c. Protected routes (/api/policies, /api/logs) are secured using the @jwt_required() decorator.
2. Real-Time Updates with Socket.IO (Flask & React)
    a. Flask-SocketIO handles real-time policy updates which are sent to connected clients
    b. React's Socket.IO client listens for these updates and adjusts policies in real-time
3. Logging & Monitoring
    a. Server-Side (Flask): Logs every request, including the user identity and the endpoint accessed.
    b. Client-Side (React): LogRocket is used for client-side monitoring, providing real-time insights into user interactions and errors
4. Authentication Flow & Error Handling
    a. The login component in App.tsx handles user authentication and stores the JWT in localStorage
    b. The app checks the authentication state before allowing access to protected content
    c. Error messages are displayed to the user and logged using both server-side and client-side logging mechanisms