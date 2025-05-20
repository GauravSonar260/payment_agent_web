from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from dateutil.parser import parse  # ✅ NEW

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/payment_agent_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'
db = SQLAlchemy(app)

EMAIL_HOST_USER = 'gauravsonar260@gmail.com'
EMAIL_HOST_PASSWORD = 'jvvk uxqm tdos zpep'

class PaymentEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    invoice_number = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
   
    email = db.Column(db.String(120), nullable=False)

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

def check_and_send_reminders():
    today = datetime.today().date()
    cutoff = today + timedelta(days=3)
    due_entries = PaymentEntry.query.filter(PaymentEntry.due_date <= cutoff).all()

    for entry in due_entries:
        subject = f"🕒 Payment Reminder: Invoice {entry.invoice_number}"
        body = (
            f"Dear Finance Team,\n\n"
            f"This is a reminder that a payment of Rs. {entry.amount} to vendor '{entry.vendor_name}' "
            f"(Invoice No: {entry.invoice_number}) is due on {entry.due_date}.\n\n"
            f"Please ensure timely processing to maintain healthy vendor relationships.\n\n"
            f"Thank you."
        )
        send_email(entry.email, subject, body)

@app.route('/')
def index():
    entries = PaymentEntry.query.order_by(PaymentEntry.due_date).all()
    return render_template('index.html', entries=entries)

@app.route('/upload_form', methods=['POST'])
def upload_form():
    vendor_name    = request.form['vendor_name']
    invoice_number = request.form['invoice_number']
    invoice_date   = parse(request.form['invoice_date']).date()  # ✅ UPDATED
    due_date       = parse(request.form['due_date']).date()      # ✅ UPDATED
    amount         = float(request.form['amount'])
    email          = request.form['email']

    entry = PaymentEntry(
        vendor_name=vendor_name,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        amount=amount,
        email=email
    )
    db.session.add(entry)
    db.session.commit()

    check_and_send_reminders()
    flash("Entry added and reminders checked.", "success")
    return redirect(url_for('index'))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    if file and file.filename.lower().endswith('.csv'):
        import csv
        stream = file.stream.read().decode("utf-8").splitlines()
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            invoice_date = parse(row[2]).date()  # ✅ FLEXIBLE DATE
            due_date     = parse(row[3]).date()  # ✅ FLEXIBLE DATE
            entry = PaymentEntry(
                vendor_name    = row[0],
                invoice_number = row[1],
                invoice_date   = invoice_date,
                due_date       = due_date,
                amount         = float(row[4]),
                email          = row[5]
            )
            db.session.add(entry)
        db.session.commit()

        check_and_send_reminders()
        flash("CSV uploaded and reminders checked.", "success")
    else:
        flash("Please upload a valid .csv file.", "error")

    return redirect(url_for('index'))

@app.route('/test_email')
def test_email():
    check_and_send_reminders()
    flash("Reminder check executed.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
