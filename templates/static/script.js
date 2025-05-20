const form = document.getElementById('invoiceForm');
const notification = document.getElementById('notification');
const invoiceTableBody = document.querySelector('#invoiceTable tbody');
const statusFilter = document.getElementById('statusFilter');

// Show notification
function showNotification(message, type = "success") {
    notification.textContent = message;
    notification.className = type;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Fetch & render invoices
async function loadInvoices(filterStatus = 'All') {
    const res = await fetch(`/get-invoices?status=${filterStatus}`);
    const invoices = await res.json();

    invoiceTableBody.innerHTML = '';

    if (invoices.length === 0) {
        invoiceTableBody.innerHTML = `<tr><td colspan="5">No invoices found.</td></tr>`;
        return;
    }

    invoices.forEach(inv => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
      <td>${inv.invoice_no}</td>
      <td>${inv.vendor}</td>
      <td>${inv.due_date}</td>
      <td>₹${inv.amount}</td>
      <td>${inv.status}</td>
    `;
        invoiceTableBody.appendChild(tr);
    });
}

// On form submit: add invoice
form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = {
        invoice_no: form.invoice_no.value,
        vendor: form.vendor.value,
        due_date: form.due_date.value,
        amount: Number(form.amount.value),
    };

    const res = await fetch('/add-invoice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    showNotification(result.message, 'success');
    form.reset();
    loadInvoices(statusFilter.value);
});

// On filter change
statusFilter.addEventListener('change', () => {
    loadInvoices(statusFilter.value);
});

// Initial load
loadInvoices();
