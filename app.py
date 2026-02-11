from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = 'secret_key_change_this_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    farmer_name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    kilo_list = db.Column(db.String(500)) 
    total_kilos = db.Column(db.Float)
    bags = db.Column(db.Integer)
    manumulu = db.Column(db.Float)
    market_price = db.Column(db.Integer)
    extra_amount = db.Column(db.Integer)
    price_per_unit = db.Column(db.Integer)
    grand_total = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending') 

class BusinessmanSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    date = db.Column(db.String(50))
    businessman_name = db.Column(db.String(100))
    bags_sold = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    farmer_name = db.Column(db.String(100))
    date = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    method = db.Column(db.String(50)) 
    status = db.Column(db.String(20), default='Pending')  # ✅ NEW STATUS COLUMN

# --- LOGIN SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

USERS = { "admin": "password123", "farmer": "farm2024" }

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS: return User(user_id)
    return None

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            login_user(User(username))
            return redirect(url_for('home'))
        else:
            error = "Invalid Username or Password!"
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS: error = "User already exists!"
        else:
            USERS[username] = password
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- HOME (CALCULATOR) ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    result = None
    existing_names = [r.farmer_name for r in Bill.query.filter_by(username=current_user.id).with_entities(Bill.farmer_name).distinct()]
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            k_list = request.form.get('kilos').split(',')
            tk = sum(float(k) for k in k_list)
            mp = int(request.form.get('market_price'))
            ex = int(request.form.get('extra_amount'))
            manu = round(tk / 11.25, 2)
            ppu = mp + ex
            gt = round(manu * ppu, 2)
            
            new_bill = Bill(username=current_user.id, farmer_name=name, date=request.form.get('bill_date'), kilo_list=request.form.get('kilos'), total_kilos=tk, bags=len(k_list), manumulu=manu, market_price=mp, extra_amount=ex, price_per_unit=ppu, grand_total=gt, status='Pending')
            db.session.add(new_bill)
            db.session.commit()
            existing_names = [r.farmer_name for r in Bill.query.filter_by(username=current_user.id).with_entities(Bill.farmer_name).distinct()]
            result = {'name': name, 'date': new_bill.date, 'total_kilos': tk, 'bags': len(k_list), 'manumulu': manu, 'market_price': mp, 'extra_amount': ex, 'price_per_unit': ppu, 'grand_total': gt}
        except: pass
    return render_template('index.html', result=result, user=current_user, existing_names=existing_names)

# --- DASHBOARD ---
@app.route('/dashboard')
@login_required
def dashboard():
    all_bills = Bill.query.filter_by(username=current_user.id).all()
    all_payments = Payment.query.filter_by(username=current_user.id).all()
    
    farmers = {}
    total_bags = total_kilos = total_revenue = 0

    for b in all_bills:
        total_bags += b.bags
        total_kilos += b.total_kilos
        total_revenue += b.grand_total
        if b.farmer_name not in farmers: farmers[b.farmer_name] = {'name': b.farmer_name, 'balance': 0.0, 'contact': 'No Contact'}
        if b.status != 'Completed': farmers[b.farmer_name]['balance'] += b.grand_total

    for p in all_payments:
        if p.farmer_name in farmers:
            farmers[p.farmer_name]['balance'] -= p.amount

    for f in farmers.values(): f['balance'] = round(f['balance'], 2)
    
    return render_template('manage_farmers.html', farmers=farmers, total_bags=total_bags, total_kilos=round(total_kilos,2), total_revenue=round(total_revenue,2))

# --- LEDGER ---
@app.route('/ledger/<farmer_name>')
@login_required
def ledger(farmer_name):
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    bill_query = Bill.query.filter_by(username=current_user.id, farmer_name=farmer_name)
    if start and end: bill_query = bill_query.filter(Bill.date >= start).filter(Bill.date <= end)
    bills = bill_query.order_by(Bill.date.desc()).all()

    pay_query = Payment.query.filter_by(username=current_user.id, farmer_name=farmer_name)
    if start and end: pay_query = pay_query.filter(Payment.date >= start).filter(Payment.date <= end)
    payments = pay_query.order_by(Payment.date.desc()).all()

    total_bill_amount = sum(b.grand_total for b in bills if b.status != 'Completed')
    total_paid_amount = sum(p.amount for p in payments) # We subtract ALL payments made
    net_balance = round(total_bill_amount - total_paid_amount, 2)
    
    period_bags = sum(b.bags for b in bills)
    period_kilos = sum(b.total_kilos for b in bills)
    period_amt = sum(b.grand_total for b in bills)

    return render_template('ledger.html', farmer_name=farmer_name, bills=bills, payments=payments, total_balance=net_balance, period_bags=period_bags, period_kilos=period_kilos, period_amount=period_amt, start_date=start, end_date=end)

# --- PAYMENTS ---
@app.route('/add_payment/<farmer_name>', methods=['POST'])
@login_required
def add_payment(farmer_name):
    try:
        new_pay = Payment(username=current_user.id, farmer_name=farmer_name, date=request.form['date'], amount=int(request.form['amount']), method=request.form['method'], status='Pending')
        db.session.add(new_pay)
        db.session.commit()
    except: pass
    return redirect(url_for('ledger', farmer_name=farmer_name))

@app.route('/delete_payment/<int:id>', methods=['POST'])
@login_required
def delete_payment(id):
    pay = Payment.query.get(id)
    if pay and pay.username == current_user.id:
        name = pay.farmer_name
        db.session.delete(pay)
        db.session.commit()
        return redirect(url_for('ledger', farmer_name=name))
    return redirect(url_for('dashboard'))

# ✅ NEW: Undo Payment Settle
@app.route('/undo_payment/<int:id>', methods=['POST'])
@login_required
def undo_payment(id):
    pay = Payment.query.get(id)
    if pay and pay.username == current_user.id:
        pay.status = 'Pending'
        db.session.commit()
    return redirect(url_for('ledger', farmer_name=pay.farmer_name))

# --- BUSINESSMAN ROUTES ---
@app.route('/businessman', methods=['GET', 'POST'])
@login_required
def businessman():
    if request.method == 'POST':
        date = request.form['sale_date']
        name = request.form['name'].strip().title()
        try:
            bags = int(request.form['bags'])
            if name and bags > 0:
                new_sale = BusinessmanSale(username=current_user.id, date=date, businessman_name=name, bags_sold=bags, status='Pending')
                db.session.add(new_sale)
                db.session.commit()
        except ValueError: pass
        return redirect(url_for('businessman'))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = BusinessmanSale.query.filter_by(username=current_user.id)
    if start_date and end_date: query = query.filter(BusinessmanSale.date >= start_date).filter(BusinessmanSale.date <= end_date)
    raw_sales = query.all()
    
    grouped = {}
    global_total_bags = 0
    for sale in raw_sales:
        global_total_bags += sale.bags_sold
        name = sale.businessman_name
        if name not in grouped: grouped[name] = { 'name': name, 'pending_bags': 0 }
        if sale.status != 'Completed': grouped[name]['pending_bags'] += sale.bags_sold

    return render_template('businessman.html', businessmen=grouped, global_total_bags=global_total_bags, start_date=start_date, end_date=end_date)

@app.route('/businessman_history/<name>')
@login_required
def businessman_history(name):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = BusinessmanSale.query.filter_by(username=current_user.id, businessman_name=name)
    if start_date and end_date: query = query.filter(BusinessmanSale.date >= start_date).filter(BusinessmanSale.date <= end_date)
    sales = query.order_by(BusinessmanSale.date.desc()).all()
    total_pending = sum(s.bags_sold for s in sales if s.status != 'Completed')
    return render_template('businessman_history.html', name=name, sales=sales, total_pending=total_pending, start_date=start_date, end_date=end_date)

@app.route('/settle_sales', methods=['POST'])
@login_required
def settle_sales():
    ids = request.form.getlist('sale_ids')
    name = None
    for sid in ids:
        sale = BusinessmanSale.query.get(sid)
        if sale and sale.username == current_user.id:
            sale.status = 'Completed'
            name = sale.businessman_name
    db.session.commit()
    if name: return redirect(url_for('businessman_history', name=name))
    return redirect(url_for('businessman'))

@app.route('/undo_sale_settle/<int:id>', methods=['POST'])
@login_required
def undo_sale_settle(id):
    sale = BusinessmanSale.query.get(id)
    if sale.username == current_user.id:
        sale.status = 'Pending'
        db.session.commit()
    return redirect(url_for('businessman_history', name=sale.businessman_name))

@app.route('/edit_sale/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sale(id):
    sale = BusinessmanSale.query.get_or_404(id)
    if sale.username != current_user.id: return "Unauthorized"
    if request.method == 'POST':
        sale.date = request.form['date']
        sale.businessman_name = request.form['name']
        try:
            sale.bags_sold = int(request.form['bags'])
            db.session.commit()
            return redirect(url_for('businessman_history', name=sale.businessman_name))
        except: return "Invalid"
    return render_template('edit_sale.html', sale=sale)

@app.route('/delete_sale/<int:id>', methods=['POST'])
@login_required
def delete_sale(id):
    sale = BusinessmanSale.query.get_or_404(id)
    name = sale.businessman_name
    if sale.username == current_user.id:
        db.session.delete(sale)
        db.session.commit()
    return redirect(url_for('businessman_history', name=name))

# --- BILL UTILS ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bill(id):
    bill = Bill.query.get_or_404(id)
    if request.method == 'POST':
        try:
            bill.date = request.form['bill_date']
            k_list = request.form.get('kilos').split(',')
            bill.kilo_list = request.form['kilos']
            bill.total_kilos = sum(float(k) for k in k_list)
            bill.bags = len(k_list)
            bill.manumulu = round(bill.total_kilos / 11.25, 2)
            bill.market_price = int(request.form['market_price'])
            bill.extra_amount = int(request.form['extra_amount'])
            bill.price_per_unit = bill.market_price + bill.extra_amount
            bill.grand_total = round(bill.manumulu * bill.price_per_unit, 2)
            db.session.commit()
            return redirect(url_for('ledger', farmer_name=bill.farmer_name))
        except: return "Error"
    return render_template('edit_bill.html', bill=bill)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_bill(id):
    bill = Bill.query.get_or_404(id)
    name = bill.farmer_name
    db.session.delete(bill)
    db.session.commit()
    return redirect(url_for('ledger', farmer_name=name))

@app.route('/undo_settle/<int:id>', methods=['POST'])
@login_required
def undo_settle(id):
    bill = Bill.query.get(id)
    bill.status = 'Pending'
    db.session.commit()
    return redirect(url_for('ledger', farmer_name=bill.farmer_name))

# ✅ UPDATED: PRINTING NOW MARKS BOTH BILLS AND PAYMENTS AS COMPLETED
@app.route('/print_selected', methods=['POST'])
@login_required
def print_selected():
    bill_ids = request.form.getlist('bill_ids')
    payment_ids = request.form.getlist('payment_ids')
    
    selected_bills = []
    for bid in bill_ids:
        bill = Bill.query.get(bid)
        if bill and bill.username == current_user.id:
            bill.status = 'Completed'
            selected_bills.append(bill)

    selected_payments = []
    for pid in payment_ids:
        pay = Payment.query.get(pid)
        if pay and pay.username == current_user.id:
            pay.status = 'Completed' # ✅ NOW MARKING PAYMENTS COMPLETED
            selected_payments.append(pay)

    db.session.commit()

    bill_total = sum(b.grand_total for b in selected_bills)
    payment_total = sum(p.amount for p in selected_payments)
    net_payable = bill_total - payment_total
    
    farmer_name = "Statement"
    if selected_bills: farmer_name = selected_bills[0].farmer_name
    elif selected_payments: farmer_name = selected_payments[0].farmer_name

    return render_template('print_bill.html', bills=selected_bills, payments=selected_payments, farmer_name=farmer_name, bill_total=bill_total, payment_total=payment_total, net_payable=net_payable)

@app.route('/print/<int:id>')
@login_required
def print_bill(id):
    bill = Bill.query.get_or_404(id)
    return render_template('print_bill.html', bills=[bill], payments=[], farmer_name=bill.farmer_name, bill_total=bill.grand_total, payment_total=0, net_payable=bill.grand_total)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)