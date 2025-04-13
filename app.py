from collections import Counter
from functools import wraps
import os
from random import uniform
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy import desc
from werkzeug.utils import secure_filename 
import stripe
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # Allowed image extensions

def create_app():
    return app

# app.register_blueprint(admin_bp)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Database Models

from models.models import *

# Home Route
@app.route('/')
def index():
    categories = Category.query.all() 
    menu_items = MenuItem.query.all()
    for item in menu_items:
        item.random_rating = round(uniform(3, 5), 1)
    return render_template('index.html', menu_items=menu_items, categories=categories)

# View items that belongs to category
@app.route('/category_items/<int:category_id>' , methods=['GET'])  
def category_items(category_id):
    categories = Category.query.all() 
    category = Category.query.get(category_id) 
    menu_items = MenuItem.query.filter_by(category_id=category_id).all()
    for item in menu_items:
        item.random_rating = round(uniform(3, 5), 1)
    return render_template('categorized_items.html', menu_items=menu_items, category=category.name, categories=categories)

# Search items
@app.route('/search' , methods=['GET'])  
def search_items():
    search_term = request.args.get('search', '').lower()
    categories = Category.query.all()  
    menu_items = MenuItem.query.filter(MenuItem.name.ilike(f'%{search_term}%')).all()
    return render_template('categorized_items.html', menu_items=menu_items, category="Searched", categories=categories)


# Home Route
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# admin routes

@wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@login_required
@app.route('/dashboard')
def admin_dashboard():
    total_categories = Category.query.count()
    total_orders = Order.query.count()
    total_menu_items = MenuItem.query.count()
    total_payments = 0

    # Get the most recent menu items added (e.g., last 5 items)
    recent_items = MenuItem.query.order_by(desc(MenuItem.item_id)).limit(5).all()

    logged_user = None 
    if 'user_id' in session:
        logged_user = User.query.get(session['user_id'])


        # Get the total orders by status
    order_status_count = Counter(order.order_status for order in Order.query.all())

    # Get total sales by category (sum of prices of items in orders grouped by category)
    category_sales = {}
    for order_item in OrderItem.query.all():
        category = order_item.menu_item.category.name  # Assuming MenuItem has a category relation
        if category not in category_sales:
            category_sales[category] = 0
        category_sales[category] += order_item.price * order_item.quantity

    # Prepare data for Chart.js
    order_status_data = {
        "labels": list(order_status_count.keys()),
        "data": list(order_status_count.values())
    }

    category_sales_data = {
        "labels": list(category_sales.keys()),
        "data": list(category_sales.values())
    }

    return render_template('admin/dashboard.html', 
                           total_categories=total_categories, 
                           total_orders=total_orders,
                           total_menu_items=total_menu_items,
                           total_payments=total_payments,
                           recent_items=recent_items,
                           order_status_data=order_status_data,
                           category_sales_data=category_sales_data,
                           logged_user = logged_user) 



@login_required
@app.route('/add/category', methods=['GET', 'POST'])
def add_category():
    logged_user = User.query.get(session['user_id'])
    if request.method == 'POST':
        name = request.form['name']
        image = request.files.get('image')
        
        if image and allowed_file(image.filename):
            # Secure the file name to prevent unsafe characters
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER']+"/categories", filename)
            image.save(image_path)

            # Create a new category instance and save to the database
            new_category = Category(name=name, image_url=filename)
            db.session.add(new_category)
            db.session.commit()
            
            flash('Category added successfully!', 'success', logged_user=logged_user)
            return redirect(url_for('add_category'))  # Redirect to the form page or another page

    return render_template('admin/add_category.html', logged_user=logged_user)


@login_required
@app.route('/add/item', methods=['GET', 'POST'])
def add_menu_item():
    logged_user = User.query.get(session['user_id'])
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category']
        image = request.files.get('image')

        if image and allowed_file(image.filename):
            # Secure the file name to prevent unsafe characters
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER']+"/items", filename)
            image.save(image_path)
 

            # Create a new menu item instance and save to the database
            new_menu_item = MenuItem(
                name=name, 
                description=description, 
                price=price, 
                image_url=filename, 
                category_id=category_id
            )
            db.session.add(new_menu_item)
            db.session.commit()
            
            flash('Menu item added successfully!', 'success')
            return redirect(url_for('add_menu_item', logged_user=logged_user))  # Redirect to the form page or another page

    # Fetch all categories for the dropdown
    categories = Category.query.all()

    return render_template('admin/add_menu_item.html', categories=categories, logged_user=logged_user)


@login_required
@app.route('/remove/item/<int:item_id>', methods=['POST'])
def remove_menu_item(item_id):
    logged_user = User.query.get(session['user_id'])
    # Find the menu item by item_id
    item_to_remove = MenuItem.query.get(item_id) 
    if item_to_remove: 
        db.session.delete(item_to_remove)
        db.session.commit() 
        flash('Menu item removed successfully!', 'success')
    else:
        # Item not found, flash a failure message
        flash('Menu item not found!', 'danger') 
    return redirect(url_for('view_menu_items', logged_user=logged_user))  # Redirect to the menu view


@login_required
@app.route('/edit/item/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id): 
    logged_user = User.query.get(session['user_id'])
    categories = Category.query.all()
    item = MenuItem.query.get(item_id) 
    if item is None:
        flash('Menu item not found!', 'danger')
        return redirect(url_for('view_menu_items', logged_user=logged_user))  # Redirect to the menu view if the item doesn't exist
    
    if request.method == 'POST':
        # Update the item with the new values from the form
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        item.category_id = request.form['category_id'] 
        db.session.commit()

        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('view_menu_items', logged_user=logged_user))  # Redirect to the menu view
    return render_template('admin/edit_menu_item.html', item=item, categories=categories, logged_user=logged_user)  # Redirect to the menu view


@login_required
@app.route('/view/items', methods=['GET', 'POST'])
def view_menu_items():
    logged_user = User.query.get(session['user_id'])
    menu_items = MenuItem.query.order_by(MenuItem.item_id).limit(20).all()
    return render_template("admin/menu_items.html", menu_items=menu_items, logged_user=logged_user)

@app.route('/categories', methods=['GET'])
def side_categories():
    categories = Category.query.all()
    return render_template("categories.html",categories=categories)


@login_required
@app.route('/view/categories', methods=['GET', 'POST'])
def view_categories():
    logged_user = User.query.get(session['user_id'])
    categories = Category.query.order_by(Category.category_id).limit(20).all()
    return render_template("admin/categories.html", categories=categories, logged_user=logged_user)


#add to cart
@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    # Convert item_id to string for session keys
    item_id_str = str(item_id)
    quantity = request.form.get('quantity', type=int, default=1)
    menu_item = MenuItem.query.get(item_id)

    # Provide a default image_url if it's missing
    image_url = menu_item.image_url if menu_item.image_url else 'default_image.png'

    if not menu_item:
        return redirect(url_for('index'))

    if 'cart' not in session:
        session['cart'] = {}

    # Use string key to access the cart
    if item_id_str in session['cart']:
        session['cart'][item_id_str]['quantity'] += quantity
    else:
        session['cart'][item_id_str] = {
            'name': menu_item.name,
            'price': menu_item.price,
            'image_url': image_url,
            'quantity': quantity
        }

    session.modified = True 
    return redirect(url_for('view_cart'))


#view cart
@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    categories = Category.query.order_by(Category.category_id).limit(20).all()
    return render_template('cart.html', cart=cart, total_price=total_price, categories=categories)

#Remove from cart
@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    item_id_str = str(item_id)
    
    # Check if 'cart' exists in session and if item exists in the cart
    if 'cart' in session and item_id_str in session['cart']:
        # Remove the item from the cart
        del session['cart'][item_id_str]
        session.modified = True

    # Redirect back to the cart view
    return redirect(url_for('view_cart'))

 

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty, please add items before placing an order.", "danger")
        return redirect(url_for('view_cart'))  # Redirect to the cart if empty

    # Get customer information from the form
    customer_name = request.form.get('name')
    table_number = request.form.get('table_number')

    # Calculate the total price from the cart
    total_price = 0
    for item_id, item_details in session['cart'].items():
        total_price += item_details['price'] * item_details['quantity']

    # Create a new order and save to the database
    new_order = Order(
        customer_name=customer_name,
        table_number=table_number,
        total_price=total_price
    )

    db.session.add(new_order)
    db.session.commit()

    # Create OrderItems and save to the database
    for item_id, item_details in session['cart'].items():
        order_item = OrderItem(
            order_id=new_order.order_id,
            menu_item_id=item_id,
            quantity=item_details['quantity'],
            price=item_details['price']
        )
        db.session.add(order_item)

    db.session.commit()

    # Optionally clear the cart after the order is placed
    session.pop('cart', None)

    # Redirect to a confirmation page or show success message
    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('order_confirmation', order_id=new_order.order_id))



#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.user_id
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('admin_dashboard'))  # or role-based redirect
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'waiter')  # defaults to waiter if not provided

        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Create and save new user
        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.user_id
        session['user_role'] = new_user.role
        flash(f'Welcome back, {new_user.name}!', 'success')
        return redirect(url_for('admin_dashboard'))  # or role-based redirect

    return render_template('register.html')


@login_required
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@login_required
@app.route('/orders')
def orders(): 
    logged_user = User.query.get(session['user_id'])
    orders = Order.query.all()
    return render_template('admin/orders.html', orders = orders, logged_user = logged_user)



@login_required
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    logged_user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_status = request.form.get('order_status')
        if new_status:
            order.order_status = new_status
            db.session.commit()
            flash('Order status updated successfully.', 'success')
            return redirect(url_for('orders'))

    return render_template('admin/edit_order.html', order=order,  logged_user = logged_user)


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get(order_id)
    if not order:
        return redirect(url_for('index'))  # Redirect to index if order not found

    # Fetch the related order items
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    return render_template('order_confirmation.html', order=order, order_items=order_items)




# api routes
@app.route('/api/view/items', methods=['GET'])
def api_view_menu_items():
    menu_items = MenuItem.query.order_by(MenuItem.item_id).limit(20).all()
    return jsonify(menu_items=[
        {
            'item_id': item.item_id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'image_url': item.image_url,
            'category_id': item.category_id
        } for item in menu_items
    ])

if __name__ == "__main__": 
    app.run(debug=True)
