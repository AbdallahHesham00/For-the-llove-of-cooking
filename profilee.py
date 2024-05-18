from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import urllib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database configuration
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=LAPTOP-J2UJ75KP;"
                                 "DATABASE=cooking_app;"
                                 "Trusted_Connection=yes;")
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    bio = db.Column(db.Text)
    # Add other fields as needed

# Route for the profilee page
@app.route('/profilee/<int:user_id>', methods=['GET', 'POST'])
def profilee(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profilee.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
