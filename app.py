# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from models import (
    get_user_by_username,
    get_all_cards,
    get_pending_bills,
    add_card,
    create_order,
    link_card_to_order,
    record_transaction,
    get_all_orders,
    generate_customer_id,
    get_pending_orders
)
from auth import verify_password
import os
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.secret_key = os.urandom(24)



# ---------------------- LOGIN ----------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        

        user_data = get_user_by_username(username)

        if not user_data:
            flash('User not found.', 'error')
            
            return render_template('login.html')

        stored_hash = user_data[2]
        if verify_password(stored_hash, password):
            session['logged_in'] = True
            session['username'] = user_data[1]
            session['user_role'] = user_data[3]
            flash('Login Successful!', 'success')
            print(">>> redirecting to dashboard")
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect password.', 'error')
            print(">>> wrong password")

    return render_template('login.html')

# ---------------------- LOGOUT ----------------------

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ---------------------- DASHBOARD ----------------------

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash("Not Logged in",'info')
        return redirect(url_for('login'))
    
    username = session.get('username')
    role = session.get('user_role')
    
    card_summary = get_all_cards()
    pending_orders = get_pending_orders()  # Changed from pending_bills
    
    return render_template('dashboard.html',
                         current_user={'username': username, 'role': role},
                         card_summary=card_summary,
                         pending_orders=pending_orders,  # Changed from pending_bills
                         current_year=datetime.now().year)

# ---------------------- STOCK ----------------------

@app.route("/add_card", methods=['GET', 'POST'])
def add_card_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('add_card.html')

    card_type = request.form.get('card_type')
    quantity = request.form.get('quantity')
    price = request.form.get("price")

    if add_card(card_type, int(quantity), Decimal(price)):
        flash(f"Card '{card_type}' added Successfully", 'success')
    else:
        flash(f"Failed to add card '{card_type}'", 'error')

    return redirect(url_for('add_card_route'))



@app.route('/view_stock')
def view_stock():
    if not session.get('logged_in'):
        flash("Not Logged in", 'info')
        return redirect(url_for('login'))

    cards = get_all_cards()
    return render_template('view_stock.html', card_data=cards)



@app.route('/edit_card/<int:card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    if not session.get('logged_in'):
        flash("Please login first.", 'info')
        return redirect(url_for('login'))

    if session.get('user_role') != 'admin':
        flash("Unauthorized action. Admins only.", 'error')
        return redirect(url_for('dashboard'))

    from models import get_card_by_id, update_card
    card_details = get_card_by_id(card_id)

    if request.method == 'GET':
        if not card_details:
            flash("Card not found.", 'error')
            return redirect(url_for('view_stock'))
        return render_template('edit_card.html', card=card_details)

    new_quantity = request.form.get('quantity')
    new_price = request.form.get('price')

    if not new_quantity or not new_price:
        flash("Quantity and Price are required.", 'error')
        return redirect(url_for('edit_card', card_id=card_id))

    success = update_card(card_id, int(new_quantity), Decimal(new_price))
    if success:
        flash("Card updated successfully.", 'success')
    else:
        flash("Failed to update card. Try again.", 'error')

    return redirect(url_for('view_stock'))

# ---------------------- CUSTOMER/ORDER ----------------------


@app.route('/create_order', methods=['GET', 'POST'])
def create_order_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_id = request.form.get('customer_id')
        order_date = request.form.get('order_date')
        delivery_status = request.form.get('delivery_status')
        advance_paid = request.form.get('advance')
        total_amount = request.form.get('total_amount')

        order_id = create_order(customer_name, customer_id, order_date, delivery_status, advance_paid, total_amount)

        selected_card_ids = request.form.getlist('card_ids')
        for card_id in selected_card_ids:
            quantity = request.form.get(f'quantities_{card_id}')
            if quantity:
                link_card_to_order(order_id, int(card_id), int(quantity))

        flash('Order created successfully!', 'success')
        return redirect(url_for('create_order_route'))  # This will show a fresh form with next customer ID

    # GET request - generate the next customer ID for this order
    available_cards = get_all_cards()
    from models import generate_customer_id
    next_customer_id = generate_customer_id()
    
    return render_template('create_orders.html', 
                         card_types=available_cards, 
                         suggested_customer_id=next_customer_id)


@app.route('/view_orders')
def view_orders():
    return render_template('view_orders.html')



@app.route('/record_payment/<order_id>', methods=['GET', 'POST'])
def record_payment(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('record_payment.html', order_id=order_id)

    amount = request.form.get('amount')
    date = request.form.get('date')
    note = request.form.get('note')

    if not amount or not date:
        flash("Amount and Date are required fields.", 'error')
        return redirect(url_for('record_payment', order_id=order_id))

    success = record_transaction(order_id, date, amount, note)
    if success:
        flash("Transaction Stored Successfully", 'success')
    else:
        flash("Failed to store transaction. Try again.", 'error')

    return redirect(url_for('dashboard'))

# ---------------------- BILLS ----------------------

@app.route('/pending_bills')
def pending_bills():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        flash('Only admins can view pending bills.', 'error')
        return redirect(url_for('dashboard'))

    bills = get_pending_bills()
    return render_template('pending_bills.html', bills=bills)

# ---------------------- RUN ----------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)