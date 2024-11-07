from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
import os
from dotenv import load_dotenv
import time
import smtplib

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Constants for retry logic
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY = 5  # Delay between retries in seconds

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json
    recipient_email = data.get('recipient_email')
    form_data = data.get('form_data')  # Expected as a JSON object with dynamic fields

    if not recipient_email or not form_data:
        return jsonify({'error': 'Recipient email and form data are required'}), 400

    # Prepare email message
    msg = Message(subject="New Form Submission", recipients=[recipient_email])
    msg.body = f"Form Data:\n\n{form_data}"

    for attempt in range(MAX_RETRIES):
        try:
            mail.send(msg)
            return jsonify({'message': 'Form submitted successfully!'}), 200
        except (smtplib.SMTPException, ConnectionError) as e:
            print(f"Attempt {attempt + 1} - Error sending email: {e}")
            time.sleep(RETRY_DELAY)  # Wait before retrying

    # If all retries fail, return an error response
    return jsonify({'error': 'Failed to send email after multiple attempts'}), 500

if __name__ == '__main__':
    app.run(debug=True)
