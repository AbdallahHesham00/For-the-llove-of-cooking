from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
import urllib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define Recipe model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(100))
    cook_time = db.Column(db.String(20))
    ingredients = db.Column(db.Text)
    instructions = db.Column(db.Text)
    comments = db.Column(db.Text)

# Define routes
@app.route('/')
def my_recipes():
    recipes = Recipe.query.all()
    return render_template('myrecipe.html', recipes=recipes)

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
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('my_recipes'))

    return render_template('editrecipe.html', recipe=recipe)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('my_recipes'))

    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully.', 'success')
    return redirect(url_for('my_recipes'))

if __name__ == '__main__':
    app.run(debug=True)
