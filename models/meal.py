from database import db

class Meal(db.Model):
    # id (int), id_user (int),food (str), description (str), date (date), is_it_a_diet (bool)
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    is_it_a_diet = db.Column(db.Boolean(), nullable=False, default=False)