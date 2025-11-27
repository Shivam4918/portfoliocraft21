from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Step 1: Create the Flask app context
app = create_app()

# Step 2: Use app context to access database
with app.app_context():
    # Step 3: Create admin user
    admin = User(
        full_name="Admin",                    # Name of admin
        email="mangoppoppo@gmail.com",            # Admin email
        password=generate_password_hash("admin123", method='pbkdf2:sha256'),  # Hashed password
        is_admin=True                         # Set as admin
    )

    # Step 4: Add admin to database
    db.session.add(admin)
    db.session.commit()

    print("✅ Admin user created successfully!")
