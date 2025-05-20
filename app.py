from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = None

def init_db():
    global conn
    conn = psycopg2.connect(
        host='localhost',
        database='payment_agent_db',
        user='postgres',
        password='admin123'
    )
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            invoice_no TEXT,
            vendor TEXT,
            vendor_email TEXT,
            invoice_date DATE,
            due_date DATE,
            amount NUMERIC,
            terms TEXT,
            status TEXT,
            scheduled_date DATE
        );
        ''')
        conn.commit()

def add_invoice(invoice):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO invoices (invoice_no, vendor, vendor_email, invoice_date, due_date, amount, terms, status, scheduled_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            invoice.get('invoice_no'),
            invoice.get('vendor'),
            invoice.get('vendor_email'),
            invoice.get('invoice_date'),
            invoice.get('due_date'),
            invoice.get('amount'),
            invoice.get('terms'),
            invoice.get('status'),
            invoice.get('scheduled_date')
        ))
        conn.commit()

def get_all_invoices():
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM invoices ORDER BY id DESC')
        return cur.fetchall()

def schedule_payments():
    """
    Simple logic to schedule payment dates:
    - If terms contain '2/10' (2% discount if paid within 10 days), schedule early payment.
    - Otherwise, scheduled_date = due_date.
    """
    invoices = get_all_invoices()
    for inv in invoices:
        scheduled_date = inv['due_date']
        if inv['terms'] and '2/10' in inv['terms']:
            early_payment_date = inv['invoice_date'] + timedelta(days=10)
            # Schedule early payment only if early_payment_date <= due_date
            if early_payment_date <= inv['due_date']:
                scheduled_date = early_payment_date
        # Update only if scheduled_date changed or not set
        if inv['scheduled_date'] != scheduled_date:
            with conn.cursor() as cur:
                cur.execute('UPDATE invoices SET scheduled_date = %s WHERE id = %s', (scheduled_date, inv['id']))
                conn.commit()

@app.route('/')
def index():
    schedule_payments()  # Update schedule on each page load
    entries = get_all_invoices()
    return render_template('index.html', entries=entries)

@app.route('/upload_form', methods=['POST'])
def upload_form():
    vendor_name = request.form.get('vendor_name')
    invoice_number = request.form.get('invoice_number')
    invoice_date = request.form.get('invoice_date')
    due_date = request.form.get('due_date')
    amount = request.form.get('amount')
    email = request.form.get('email')
    terms = request.form.get('terms', '')  # Optional field
    status = 'Scheduled'  # Default status
    scheduled_date = None

    try:
        invoice_date_obj = datetime.strptime(invoice_date, '%Y-%m-%d').date()
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        amount_float = float(amount)
    except Exception as e:
        flash('Invalid date or amount format', 'error')
        return redirect(url_for('index'))

    invoice = {
        'invoice_no': invoice_number,
        'vendor': vendor_name,
        'vendor_email': email,
        'invoice_date': invoice_date_obj,
        'due_date': due_date_obj,
        'amount': amount_float,
        'terms': terms,
        'status': status,
        'scheduled_date': scheduled_date
    }

    add_invoice(invoice)
    flash('Invoice added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('file')
    if not file:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    import csv
    import io
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)

    count = 0
    for row in reader:
        try:
            invoice_date_obj = datetime.strptime(row['invoice_date'], '%Y-%m-%d').date()
            due_date_obj = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
            amount_float = float(row['amount'])
            invoice = {
                'invoice_no': row.get('invoice_no'),
                'vendor': row.get('vendor'),
                'vendor_email': row.get('vendor_email'),
                'invoice_date': invoice_date_obj,
                'due_date': due_date_obj,
                'amount': amount_float,
                'terms': row.get('terms', ''),
                'status': 'Scheduled',
                'scheduled_date': None
            }
            add_invoice(invoice)
            count += 1
        except Exception as e:
            # Skip invalid rows or log error
            continue

    flash(f'{count} invoices uploaded successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
