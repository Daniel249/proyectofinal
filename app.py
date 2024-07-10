from flask import Flask, render_template, request, jsonify
import psycopg2
import random

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='Proyecto',
        user='postgres',
        password='admin',
        host='localhost',
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_rooms', methods=['POST'])
def fetch_rooms():
    data = request.get_json()
    start_date = data['start_date']
    end_date = data['end_date']
    
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT hid, tipo, camas 
        FROM habitaciones 
        WHERE hid NOT IN (
            SELECT habitacion 
            FROM reservas 
            WHERE (inicio <= %s AND final >= %s) 
               OR (inicio <= %s AND final >= %s)
        )
    """
    cur.execute(query, (start_date, start_date, end_date, end_date))
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(rooms)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data['name']
    last_name = data['last_name']
    phone_number = data['phone_number']
    identification = data['identification']
    selected_rooms = data['selected_rooms']
    start_date = data['start_date']
    end_date = data['end_date']
    cliente = random.randint(1, 1000)
    numeropersonas = data['numeropersonas']
    card_number = data['card_number']

    conn = get_db_connection()
    cur = conn.cursor()
    for room in selected_rooms:
        cur.execute('INSERT INTO reservas (rid, habitacion, cliente, numeropersonas, inicio, final) VALUES (%s, %s, %s, %s, %s, %s)',
                    (random.randint(1, 10000), int(room['idd']), cliente, numeropersonas, start_date, end_date))
    cur.execute('INSERT INTO Clientes (cid, nombre, apellido, identificacion, telefono, tarjeta) VALUES (%s, %s, %s, %s, %s, %s)', 
                (cliente, name, last_name, identification, phone_number, card_number))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
