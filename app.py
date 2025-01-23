from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    card_id = db.Column(db.String(20), nullable=True)

    logs = db.relationship('Log', backref='client', lazy=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(20), db.ForeignKey('client.card_id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(10), nullable=False) # entry or exit

class Attendance(db.Model):
    card_id = db.Column(db.String(20), db.ForeignKey('client.card_id'), primary_key=True)
    is_present = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.Integer, nullable=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(20), nullable=False)

def get_active_gym_members():
    return Attendance.query.filter_by(is_present=True).count()


def get_today_timestmap():
    start_of_day = int(datetime(datetime.today().year, datetime.today().month, datetime.today().day).timestamp())
    end_of_day = int(datetime(datetime.today().year, datetime.today().month, datetime.today().day, 23, 59, 59).timestamp())
    return (start_of_day, end_of_day)

def get_todays_entrances():
    start_of_day, end_of_day = get_today_timestmap()
    today_entrances = Log.query.filter(
       Log.timestamp >= start_of_day,
       Log.timestamp <= end_of_day,
       Log.action == 'entry'
    ).count()

    return today_entrances


def get_todays_logs():
    start_of_day, end_of_day = get_today_timestmap()
    todays_logs = Log.query.filter(
        Log.timestamp >= start_of_day,
        Log.timestamp <= end_of_day
    ).order_by(Log.timestamp.desc()).all()

    logs_info = []
    for log in todays_logs:
        client = log.client

        log_info = {
            "client_name": f"{client.name} {client.surname}",
            "timestamp": datetime.fromtimestamp(log.timestamp).strftime('%d.%m.%Y %H:%M:%S'),
            "action": log.action
        }
        logs_info.append(log_info)

    return logs_info


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clients')
def clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/client/<int:client_id>')
def client_detail(client_id):
    client = Client.query.get(client_id)
    if client:
        return render_template('client_detail.html', client=client)
    else:
        return "Client not found", 404


@app.route('/add_client', methods=['POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        status = request.form['status']
        gender = request.form['gender']
        card_id = request.form['card-id']

        new_client = Client(name=name, surname=surname, status=status, gender=gender, card_id=card_id)
        db.session.add(new_client)
        db.session.commit()

        return redirect(url_for('clients'))

@app.route('/edit_client', methods=['POST'])
def edit_client():
    if request.method == 'POST':
        client_id = request.form['id']
        client = Client.query.get(client_id)

        if client:
            client.name = request.form['name']
            client.surname = request.form['surname']
            client.gender = request.form['gender']
            client.status = request.form['status']
            client.card_id = request.form['card-id']

            db.session.commit()
        return redirect(url_for('clients'))

@app.route('/api/client/<int:client_id>')
def api_client_detail(client_id):
    client = Client.query.get(client_id)
    if client:
        logs_info = [
            {
                'timestamp': datetime.fromtimestamp(log.timestamp).strftime('%d.%m.%Y %H:%M:%S'),
                'action': log.action
            }
            for log in client.logs
        ]

        return jsonify({
            'logs': logs_info
        })


@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    active_members = get_active_gym_members()
    todays_entrances = get_todays_entrances()
    todays_logs = get_todays_logs()

    return jsonify({
        'active_members': active_members,
        'todays_entrances': todays_entrances,
        'todays_logs': todays_logs
    })


@app.route('/api/card_id', methods=['GET'])
def api_card_id():
    card_id = Card.query.order_by(Card.id.desc()).first()
    if card_id:
        return jsonify({'card_id': card_id.card_id})
    else:
        return jsonify({'card_id': None})

@app.route('/api/card_id', methods=['DELETE'])
def api_card_id_delete():
    try:
        Card.query.delete()
        db.session.commit()
        return jsonify({'message': 'Wszystkie rekordy zostały pomyślnie usunięte'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
