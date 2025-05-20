import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date

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
            vendor_email TEXT,  -- New column
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
    """
    invoice: dict with keys:
    invoice_no, vendor, vendor_email, invoice_date, due_date, amount, terms, status, scheduled_date
    """
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO invoices (invoice_no, vendor, vendor_email, invoice_date, due_date, amount, terms, status, scheduled_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            invoice.get('invoice_no') or None,
            invoice.get('vendor') or None,
            invoice.get('vendor_email') or None,
            invoice.get('invoice_date'),
            invoice.get('due_date'),
            invoice.get('amount') or 0,
            invoice.get('terms') or None,
            invoice.get('status') or None,
            invoice.get('scheduled_date')
        ))
        conn.commit()

def get_all_invoices():
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM invoices ORDER BY id DESC')
        return cur.fetchall()
