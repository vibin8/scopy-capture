from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:nobita3@localhost/capture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class CapturedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)  # Ensure email is unique
    url = db.Column(db.String(2083), nullable=False)  # Max URL length

    def __repr__(self):
        return f'<CapturedData {self.email}, {self.url}>'

# Email validation function using regular expression
def is_valid_email(value):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, value) is not None

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.get_json()
        
        # Initialize a variable to store the found email
        found_email = None

        # Loop through the form fields in the JSON object
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if is_valid_email(item):
                        found_email = item
                        break  # Stop once we find an email
            elif isinstance(value, str):
                if is_valid_email(value):
                    found_email = value
                    break  # Stop once we find an email

        # Check if an email was found
        if found_email:
            url = data.get('url', 'No URL Provided')  # Get the URL, or default to a message

            # Check if the record already exists
            existing_record = CapturedData.query.filter_by(email=found_email).first()
            if existing_record:
                # Update the existing record
                existing_record.url = url
                db.session.commit()  # Commit the changes
                return jsonify({
                    "message": "Email updated successfully",
                    "email": found_email,
                    "url": url
                }), 200
            else:
                # Create a new record
                new_record = CapturedData(email=found_email, url=url)
                db.session.add(new_record)
                db.session.commit()  # Commit the changes
                return jsonify({
                    "message": "Email captured successfully",
                    "email": found_email,
                    "url": url
                }), 201
        else:
            return jsonify({"error": "No valid email found in form data"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the table if it doesn't exist
    app.run(debug=True)
