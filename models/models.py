from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# Database Models

# Users Model (Admins, Waiters, etc.)
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='waiter')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Category Model
class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    image_url = db.Column(db.String(255))  # Add image column  

    # Explicit relationship to MenuItem with back_populates
    menu_items = db.relationship('MenuItem', back_populates='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

# Menu Items Model 
class MenuItem(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255)) 
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    # Explicit relationship to Category with back_populates
    category = db.relationship('Category', back_populates='menu_items', lazy=True)

    def __repr__(self):
        return f"<MenuItem {self.name}>"


# Orders Model
class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    table_number = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(20), default='Pending')
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Order {self.name}>"

# Order Items Model (for individual items in orders)
class OrderItem(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.name}>"

# Payment Model
class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    
    def __repr__(self):
        return f"<Payment {self.name}>"