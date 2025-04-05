from app import db, create_app 

app = create_app()

from models.models import Category, MenuItem 

# Clear existing data in the tables (optional, for seeding purposes)
def clear_data():
    db.session.query(MenuItem).delete()
    db.session.query(Category).delete()
    db.session.commit()

# Create sample data for Categories
def create_categories():
    categories = [
        Category(name="Appetizers", image_url="12007283.png"),
        Category(name="Desserts", image_url="1531385.png"),  
        Category(name="Beverages", image_url="12007232.png"),
        Category(name="Snacks", image_url="9718703.png"),
        Category(name="Burgers", image_url="3075977.png"),
        Category(name="Pizza", image_url="1404945.png"),
        Category(name="Fruits", image_url="2153788.png"),
        Category(name="Beer", image_url="14112679.png"),
    ]
    db.session.bulk_save_objects(categories)
    db.session.commit()

# Create sample data for Menu Items
def create_menu_items():
    menu_items = [
        MenuItem(name="Spring Rolls", description="Crispy rolls filled with vegetables.", price=5.99, image_url="8622915.png", category_id=1),
        MenuItem(name="Grilled Chicken", description="Juicy grilled chicken served with vegetables.", price=12.99, image_url="12054083.png", category_id=2),
        MenuItem(name="Chocolate Cake", description="Rich chocolate cake topped with whipped cream.", price=6.49, image_url="6692143.png ", category_id=3),
        MenuItem(name="Lemonade", description="Freshly squeezed lemonade.", price=2.99, image_url="457829.png", category_id=4)
    ]
    db.session.bulk_save_objects(menu_items)
    db.session.commit()

# Run the seeder
def run_seeder():
    clear_data()         # Optional: Clear existing data before seeding
    create_categories()  # Add categories
    create_menu_items()  # Add menu items
    print("Seeder has run successfully!")

if __name__ == "__main__":
    # Create the tables in the database
    with app.app_context():
        run_seeder()
