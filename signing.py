from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import urllib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database configuration
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                 "SERVER=LAPTOP-J2UJ75KP;"
                                 "DATABASE=cooking_app;"
                                 "Trusted_Connection=yes;")
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models
class User(db.Model):
    __tablename__ = 'Users'
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Bio = db.Column(db.Text)
    ProfilePictureUrl = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=db.func.current_timestamp())

class Recipe(db.Model):
    __tablename__ = 'Recipes'
    Id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    Title = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    Ingredients = db.Column(db.Text)
    Instructions = db.Column(db.Text)
    ImageUrl = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=db.func.current_timestamp())

class Follower(db.Model):
    __tablename__ = 'Followers'
    Id = db.Column(db.Integer, primary_key=True)
    FollowerId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    FollowingId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    __table_args__ = (db.UniqueConstraint('FollowerId', 'FollowingId', name='_follower_following_uc'),)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            flash('Email is already registered. Please sign in.', 'danger')
            return redirect(url_for('sign_in'))
        
        new_user = User(Username=username, Email=email, PasswordHash=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Sign-up successful! Please complete your profile.', 'success')
        return redirect(url_for('profile', user_id=new_user.Id))
    return render_template('sign_up.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(Email=email).first()
        if user and user.PasswordHash == password:
            session['user_id'] = user.Id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('sign_in.html')

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.Bio = request.form['bio']
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.ProfilePictureUrl = url_for('static', filename='uploads/' + filename)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile', user_id=user.Id))
    return render_template('profile.html', user=user)

@app.route('/profilee', methods=['GET', 'POST'])
def profilee():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please sign in to view your profile.', 'danger')
        return redirect(url_for('sign_in'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.Bio = request.form['bio']
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.ProfilePictureUrl = url_for('static', filename='uploads/' + filename)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profilee'))
    
    return render_template('profilee.html', user=user)

@app.route('/my_recipes')
def my_recipes():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please sign in to view your recipes.', 'danger')
        return redirect(url_for('sign_in'))
    
    # Fetch recipes associated with the current user from the database
    recipes = Recipe.query.filter_by(UserId=user_id).all()

    return render_template('myrecipe.html', recipes=recipes)


@app.route('/edit_recipe/<int:recipe_id>')
def edit_recipe(recipe_id):
    # Fetch the recipe from the database based on recipe_id
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('my_recipes'))

    # Redirect to the edit recipe page with the recipe details
    return render_template('editrecipe.html', recipe=recipe)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Fetch the recipe from the database based on recipe_id
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('my_recipes'))

    # Delete the recipe from the database
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully.', 'success')
    return redirect(url_for('my_recipes'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
