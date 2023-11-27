from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
import os

seats = list(range(1, 61))



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)


class AddBusForm(FlaskForm):
    location_start = StringField('Start Location', validators=[DataRequired()])
    location_end = StringField('Arrival Location', validators=[DataRequired()])
    date_start = StringField('Departure Date', validators=[DataRequired()])
    date_arrival = StringField('Arrival Date', validators=[DataRequired()])
    time_start = StringField('Departure Time', validators=[DataRequired()])
    time_end = StringField('Arrival Time', validators=[DataRequired()])
    buss_capacity = IntegerField('Bus Capacity', validators=[DataRequired()])
    occupied_seats = IntegerField('Occupied Seats', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Add Bus', validators=[DataRequired()])


class ReserveForm(FlaskForm):
    full_name = StringField('Write full name', validators=[DataRequired()])
    number_of_seats = SelectField('How many seats do you want?', validators=[DataRequired()], choices=seats)
    submit = SubmitField('Make reservation', validators=[DataRequired()])




app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///busses.db")
db = SQLAlchemy()
db.init_app(app)


class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    location_start = db.Column(db.String, nullable=False)
    location_end = db.Column(db.String, nullable=False)
    date_start = db.Column(db.String, nullable=False)
    date_arival = db.Column(db.String, nullable=False)
    time_start = db.Column(db.String, nullable=False)
    time_end = db.Column(db.String, nullable=True)
    buss_capacity = db.Column(db.Integer, nullable=True)
    occupied_seats = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    number_of_seats = db.Column(db.Integer, nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bus = db.relationship('Bus', backref='reservations')

with app.app_context():
    db.create_all()



@app.route("/")
def home():
    result = db.session.execute(db.select(Bus))
    all_busses = result.scalars()
    print(all_busses)
    return render_template("index.html", busses = all_busses)



@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddBusForm()
    if form.validate_on_submit():
        new_buss = Bus(
        location_start = form.location_start.data,
        location_end = form.location_end.data,
        date_start = form.date_start.data,
        date_arival = form.date_arrival.data,
        time_start = form.time_start.data,
        time_end = form.time_end.data,
        buss_capacity = form.buss_capacity.data,
        occupied_seats = form.occupied_seats.data,
        price = form.price.data, 
        )
        with app.app_context():
            db.session.add(new_buss)
            db.session.commit()
    return render_template("add.html", form=form)


@app.route("/reserve", methods=["GET", "POST"])
def reserve_seats():
    bus_id = request.args.get("id")
    form = ReserveForm()
    bus = db.get_or_404(Bus, bus_id)
    available_seats = bus.buss_capacity - bus.occupied_seats 
    if form.validate_on_submit():
            requested_seats = int(form.number_of_seats.data)            
            if requested_seats > available_seats:
                flash("Sorry, there are not enough available seats.", "danger")
            else:
                reservation = Reservation(
                full_name=form.full_name.data,
                number_of_seats=requested_seats,
                bus_id = bus.id,
                price = bus.price * requested_seats,               
                bus=bus
                )
                db.session.add(reservation)

                bus.occupied_seats += requested_seats
                db.session.commit()
                flash(f"Successfully reserved {requested_seats} seats. Totla: {bus.price * int(form.number_of_seats.data)}", "success")

    return render_template("reserve.html", form=form, bus=bus, available_seats=available_seats, occupied_seats = bus.occupied_seats)




if __name__ == '__main__':
    app.run(debug=True)
