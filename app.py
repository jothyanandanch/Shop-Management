import time
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
    generate_order_id,
    get_pending_orders,get_card_by_id, 
    update_card,
    get_order_details,
    get_total_payments,
    update_order_delivery_status,
    update_payment_status
    ,delete_card_by_id,delete_order_by_id
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

@app.route('/')
def dashboard_redirect():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash("Not Logged in",'info')
        return redirect(url_for('login'))
    
    username = session.get('username')
    role = session.get('user_role')
    
    card_summary = get_all_cards()
    pending_orders = get_pending_orders()  
    
    return render_template('dashboard.html',
                         current_user={'username': username, 'role': role},
                         card_summary=card_summary,
                         pending_orders=pending_orders,
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
        flash(f"Failed to add card '{card_type} !,Try Again or Contact Developer", 'error')

    return redirect(url_for('add_card_route'))



@app.route('/view_stock')
def view_stock():
    if not session.get('logged_in'):
        flash("Not Logged in", 'info')
        return redirect(url_for('login'))

    cards = get_all_cards()
    print(f"Debug: Cards data = {cards}")  # For debugging
    print(f"Debug: Number of cards = {len(cards) if cards else 0}")
    return render_template('stock.html', cards=cards)



@app.route('/edit_card/<int:card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    if not session.get('logged_in'):
        flash("Please login first.", 'info')
        time.sleep(2)
        return redirect(url_for('login'))

    if session.get('user_role') != 'admin':
        flash("Unauthorized action. Admins only.", 'error')
        return redirect(url_for('dashboard'))

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

@app.route('/delete_card/<int:card_id>',methods=['DELETE'])
def delete_card(card_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}),401
    

    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    try:
        success = delete_card_by_id(card_id)
        
        if success:
            return jsonify({'message': 'Card deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete card'}), 500
            
    except Exception as e:
        print(f"Error deleting card: {e}")
        return jsonify({'error': 'Server error'}), 500
# ---------------------- CUSTOMER/ORDER ----------------------


@app.route('/create_order', methods=['GET', 'POST'])
def create_order_route():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data including customer phone
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        order_id = request.form.get('order_id')  # business order number
        order_date = request.form.get('order_date')
        delivery_status = request.form.get('delivery_status')
        advance_paid = request.form.get('advance')
        total_amount = request.form.get('total_amount')
        payment_status = request.form.get('payment_status')

        curr_order_db_id = create_order(
            customer_name,
            customer_phone,
            order_id,
            order_date,
            delivery_status,
            advance_paid,
            total_amount,
            payment_status
        )

        if not curr_order_db_id:
            flash('Failed to create order!', 'error')
            return redirect(url_for('create_order_route'))

        # Link cards to the order with DB primary key, not business order number
        selected_card_ids = request.form.getlist('card_ids')
        for card_id in selected_card_ids:
            quantity = request.form.get(f'quantities_{card_id}')
            if quantity:
                link_card_to_order(curr_order_db_id, int(card_id), int(quantity))

        flash('Order created successfully!', 'success')
        return redirect(url_for('create_order_route'))

    # GET Request
    available_cards = get_all_cards()
    next_order_id = generate_order_id()
    return render_template(
        'create_orders.html',
        card_types=available_cards,
        suggested_order_id=next_order_id
    )

@app.route('/view_orders')
def view_orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    orders=get_all_orders()
    return render_template('view_orders.html',orders=orders)



@app.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401

    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        success = delete_order_by_id(order_id)
        if success:
            return jsonify({'message': 'Order deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete order'}), 500
    except Exception as e:
        print(f"Error deleting order: {e}")
        return jsonify({'error': 'Server error'}), 500



@app.route('/record_payment/<order_id>', methods=['GET', 'POST'])
def record_payment(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Your existing GET logic remains the same
        
        
        order = get_order_details(order_id)
        if not order:
            flash('Order not found!', 'error')
            return redirect(url_for('dashboard'))
        
        total_payments = get_total_payments(order_id)
        balance_amount = float(order[4]) - float(order[5]) - total_payments
        
        return render_template('record_payment.html', 
                             order=order,
                             order_id=order_id, 
                             balance_amount=balance_amount,
                             total_payments=total_payments)

    # POST logic with payment status update
    amount = request.form.get('amount')
    date = request.form.get('date')
    note = request.form.get('note')
    delivery_status = request.form.get('delivery_status')
    # In the POST section, add:
    manual_payment_status = request.form.get('payment_status')

    if manual_payment_status:
        # User manually selected status
        update_payment_status(order_id, manual_payment_status)
    else:
        # Auto-calculate based on balance
        if new_balance <= 0:
            update_payment_status(order_id, 'Paid')
        else:
            update_payment_status(order_id, 'Pending')

    if not amount or not date:
        flash("Amount and Date are required fields.", 'error')
        return redirect(url_for('record_payment', order_id=order_id))

    # Record the transaction
    success = record_transaction(order_id, date, amount, note)
    
    if success:
        # Calculate new balance after this payment
               
        order = get_order_details(order_id)
        total_payments = get_total_payments(order_id) + float(amount)  # Include current payment
        new_balance = float(order[4]) - float(order[5]) - total_payments  # total - advance - all_payments
        
        # Automatically update payment status based on balance
        if new_balance <= 0:
            update_payment_status(order_id, 'Paid')
        else:
            update_payment_status(order_id, 'Pending')
        
        # Update delivery status if needed
        if delivery_status:
            
            update_order_delivery_status(order_id, delivery_status)
        
        flash("Payment recorded and status updated successfully!", 'success')
    else:
        flash("Failed to record payment. Try again.", 'error')

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