from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/capture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for Captured Data
class CapturedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(2083), nullable=False)  # Max URL length

    def __repr__(self):
        return f'<CapturedData {self.email}, {self.url}>'

# Email validation function using regular expression
def is_valid_email(value):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, value) is not None

# Endpoint to capture data from the extension
@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()

        # Initialize a variable to store the found email
        found_email = None

        # Loop through the form fields in the JSON object
        for key, value in data.items():
            # If the value is a list, check each item in the list for an email
            if isinstance(value, list):
                for item in value:
                    if is_valid_email(item):
                        found_email = item
                        break  # Stop once we find an email
            # If the value is a string, check directly
            elif isinstance(value, str):
                if is_valid_email(value):
                    found_email = value
                    break  # Stop once we find an email

        # Check if an email was found
        if found_email:
            url = data.get('url', 'No URL Provided')  # Get the URL, or default to a message
            
            # Create CapturedData instance and save to DB
            captured_data = CapturedData(email=found_email, url=url)
            db.session.add(captured_data)
            db.session.commit()

            return jsonify({
                "message": "Email found and captured successfully",
                "email": found_email,
                "url": url
            }), 200
        else:
            return jsonify({"error": "No valid email found in form data"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
