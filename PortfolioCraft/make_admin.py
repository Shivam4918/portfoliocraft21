import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

email_to_promote = "mangoppoppo@gmail.com"

user = User.query.filter_by(email=email_to_promote).first()

if user:
    user.is_admin = True
    db.session.commit()
    print(f"{user.full_name} ({user.email}) is now an admin.")
else:
    print("User not found.")
