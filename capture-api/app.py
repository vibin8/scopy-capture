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
# Email validation function using regular expression
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.route('/capture', methods=['POST'])
def capture():
    try:
        # Get JSON data from the request body
        data = request.get_json()

        # Check if 'email' key exists in the form data
        if 'email' in data:
            email_list = data['email']  # Get the array of email(s)
            if isinstance(email_list, list) and len(email_list) > 0:
                email = email_list[0]  # Take the first email from the list
                if is_valid_email(email):
                    # Process or store the email as needed
                    url = data.get('url')  # Get the URL if available

                    # Store to DB, process the data, etc.
                    return jsonify({
                        "message": "Data captured successfully",
                        "email": email,
                        "url": url
                    }), 200
                else:
                    return jsonify({"error": "Invalid email format"}), 400
            else:
                return jsonify({"error": "Email field is empty"}), 400
        else:
            return jsonify({"error": "Email field is missing"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
