1. Create a virtual environment
`python3 -m venv venv` 
`source venv/bin/activate`
On Windows, use `venv\Scripts\activate`
# run command
`pip install -r requirements.txt`
2. Generate SSL certificates (for development purposes):
`openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
3. Run npm run build
4. Run npm start
5. Run python app.py