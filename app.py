import bcrypt
from datetime import datetime
from flask import Flask, jsonify, request
from database import db
from models.user import User
from models.meal import Meal
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:daily123@127.0.0.1:3306/daily-diet'

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

# view login
login_manager.login_view = 'login'

@login_manager.user_loader # recuperar usuario
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/user', methods=['POST'])
# @login_required # Protege a criação de usuário para apenas usuários logados
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None:
        if username and password:
            hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
            user_filter = User(username=username, password=hashed_password)
            db.session.add(user_filter)
            db.session.commit()
            return jsonify({'message': 'User created successfully'})
        return jsonify({'message': 'Invalid username or password'}), 400
    
    return jsonify({'message': 'User already exists'}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        # login
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({'message': 'Login success'})
        return jsonify({'message': 'Invalid username or password'}), 400
    
    return jsonify({'message': 'Invalid username or password'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout success'})


@app.route('/meals', methods=['POST'])
@login_required
def create_meal():
    data = request.json
    food = data.get('food')
    description = data.get('description')
    date = datetime.now()
    date_format = date.strftime('%Y-%m-%d')
    is_it_a_diet = data.get('is_it_a_diet')

    if food and description and is_it_a_diet is not None:
        meal = Meal(food=food, description=description, date=date_format, is_it_a_diet=is_it_a_diet, id_user=current_user.id)
        db.session.add(meal)
        db.session.commit()
        return jsonify({'message': f'Meal created successfully on user{current_user.id}'}), 20
    return jsonify({'message': 'Invalid data'}), 400

@app.route('/meals', methods=['GET'])
@login_required
def read_meals():
    meals = Meal.query.filter_by(id_user=current_user.id).all()
    list_meals = [{'id':meal.id,'food': meal.food, 'description': meal.description, 'date': meal.date, 'is_it_a_diet': meal.is_it_a_diet} for meal in meals]
    return jsonify(list_meals)

@app.route('/meals/<int:food_id>', methods=['GET'])
@login_required
def read_meal(food_id):
    meal = Meal.query.filter_by(id=food_id, id_user=current_user.id).first()

    if meal:
        return jsonify({'id':meal.id,'food': meal.food, 'description': meal.description, 'date': meal.date, 'is_it_a_diet': meal.is_it_a_diet})
    return jsonify({'message': 'Meal not found'}), 404
    

@app.route('/meals/<int:food_id>', methods=['PUT'])
@login_required
def update_meal(food_id):
    data = request.json
    food = data.get('food')
    description = data.get('description')
    date = data.get('date')
    is_it_a_diet = data.get('is_it_a_diet')

    meal = Meal.query.filter_by(id=food_id, id_user=current_user.id).first()

    if meal:
        meal.food = food
        meal.description = description
        meal.date = date
        meal.is_it_a_diet = is_it_a_diet
        db.session.commit()
        return jsonify({'message': f'Meal {food_id} updated successfully'}), 200
    return jsonify({'message': 'Meal not found'}), 404

@app.route('/meals/<int:food_id>', methods=['DELETE'])
@login_required
def delete_meal(food_id):
    meal = Meal.query.filter_by(id=food_id, id_user=current_user.id).first()

    if meal:
        db.session.delete(meal)
        db.session.commit()
        return jsonify({'message': f'Meal {food_id} deleted successfully'}), 200
    return jsonify({'message': 'Meal not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)