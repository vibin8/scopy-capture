from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:nobita3@localhost/capture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class CapturedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(2083), nullable=False)  # Max URL length

    def __repr__(self):
        return f'<CapturedData {self.email}, {self.url}>'

# Endpoint to capture data from the extension

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        email = None
        url = data.get('url')


        # find the email
        for key, value in data.items():
            if isinstance(value, str) and re.match(EMAIL_REGEX, value):
                email = value
            elif key == 'url':  # Assuming the URL will be sent with the key 'url'
                url = value
        
        if not email or not url:
            return jsonify({"error": "Email and URL are required"}), 400

        captured_data = CapturedData(email=email, url=url)
        db.session.add(captured_data)
        db.session.commit()

        return jsonify({"message": "Data captured successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
