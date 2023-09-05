import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Cafe TABLE Configuration
with app.app_context():
    class Cafe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250), unique=True, nullable=False)
        map_url = db.Column(db.String(500), nullable=False)
        img_url = db.Column(db.String(500), nullable=False)
        location = db.Column(db.String(250), nullable=False)
        seats = db.Column(db.String(250), nullable=False)
        has_toilet = db.Column(db.Boolean, nullable=False)
        has_wifi = db.Column(db.Boolean, nullable=False)
        has_sockets = db.Column(db.Boolean, nullable=False)
        can_take_calls = db.Column(db.Boolean, nullable=False)
        coffee_price = db.Column(db.String(250), nullable=True)

        def to_dict(self):
            # method 1
            # dictionary = {}
            # for column in self.__table__.columns:
            #     dictionary[column.name] = getattr(self, column.name)
            # return dictionary
            # method 2
            return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


#  HTTP GET - Read Record
@app.route("/random")
def get():
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def all():
    cafes = Cafe.query.all()
    data = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=data)


@app.route("/search")
def search():
    location = request.args.get("loc")
    data = Cafe.query.filter_by(location=location).first()
    if data:
        return jsonify(cafe=data.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


#  HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    seats=request.form.get('seats'),
                    has_toilet=bool(request.form.get('has_toilet')),
                    has_wifi=bool(request.form.get('has_wifi')),
                    has_sockets=bool(request.form.get('has_sockets')),
                    can_take_calls=bool(request.form.get('can_take_calls')),
                    coffee_price=request.form.get('coffee_price'),
                    )
    try:
        with app.app_context():
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."})
    except IntegrityError:
        return jsonify(response={"failed": "Failed to add the new cafe."})


#  HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    with app.app_context():
        cafe_to_update = db.session.get(Cafe, cafe_id)
        if cafe_to_update:
            print(cafe_to_update.coffee_price)
            print(request.args.get('new_price'))
            cafe_to_update.coffee_price = request.args.get('new_price')
            db.session.commit()
            return jsonify(success="Successfully updated the price.")
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


#  HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def report_closed(cafe_id):
    api_key = request.args.get("api-key")
    if api_key != "TopSecretAPIKey":
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403
    with app.app_context():
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Successfully deleted the cafe record.")
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
