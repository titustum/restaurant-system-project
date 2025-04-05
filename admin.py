from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin login decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add your admin authentication logic here
        # For example, check if user is logged in and is an admin
        if not session.get('is_admin'):
            flash('Please login as admin first.')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Add your admin login logic here
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

# Add more admin routes as needed





# Admin Dashboard Route
@admin_bp.route('/admin')
def admin_dashboard():
    orders = Order.query.all()
    return render_template('admin_dashboard.html', orders=orders)


# Admin Login Route
@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

# Add Menu Item (Admin)
@admin_bp.route('/admin/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_url = request.form['image_url']
        category = request.form['category']
        
        new_item = MenuItem(name=name, description=description, price=price, image_url=image_url, category=category)
        db.session.add(new_item)
        db.session.commit()
        flash('Menu Item Added Successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_menu_item.html')

# Delete Menu Item (Admin)
@admin_bp.route('/admin/menu/delete/<int:item_id>')
def delete_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    db.session.delete(menu_item)
    db.session.commit()
    flash('Menu Item Deleted Successfully!')
    return redirect(url_for('admin_dashboard'))

# Update Menu Item (Admin)
@admin_bp.route('/admin/menu/update/<int:item_id>', methods=['GET', 'POST'])
def update_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    if request.method == 'POST':
        menu_item.name = request.form['name']
        menu_item.description = request.form['description']
        menu_item.price = float(request.form['price'])
        menu_item.image_url = request.form['image_url']
        menu_item.category = request.form['category']
        
        db.session.commit()
        flash('Menu Item Updated Successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('update_menu_item.html', menu_item=menu_item)