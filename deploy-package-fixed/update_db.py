from database import db
from models.user import User
from flask import Flask
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    # Create all tables with new columns
    db.create_all()
    print('Database updated successfully with new columns')
    
    # Check if columns exist
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            print(f"Current columns in users table: {columns}")
            
            if 'operational_balance_usd' not in columns:
                print("Adding operational_balance_usd column...")
                conn.execute(db.text("ALTER TABLE users ADD COLUMN operational_balance_usd FLOAT DEFAULT 0.0"))
                conn.commit()
                
            if 'last_conversion_rate' not in columns:
                print("Adding last_conversion_rate column...")
                conn.execute(db.text("ALTER TABLE users ADD COLUMN last_conversion_rate FLOAT"))
                conn.commit()
                
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")