from flask import Flask, render_template, request, jsonify
import psycopg2
import json
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT hid, tipo, camas FROM habitaciones WHERE Estado = TRUE')
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', rooms=rooms)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    name = data['name']
    last_name = data['last_name']
    phone_number = data['phone_number']
    identificacion = data['identification']
    selected_rooms = data['selected_rooms']
    inicio = data['start_date']
    final = data['end_date']
    cliente = random.randint(1,1000)
    numeropersonas = data['numeropersonas']
    card_number = data['card_number']

    
    # Aquí podrías hacer algo con la información recibida, como insertarla en otra tabla.
    # Ejemplo de insertar en una tabla de reservas:
    conn = get_db_connection()
    cur = conn.cursor()
    for room in selected_rooms:
        cur.execute('INSERT INTO reservas (rid, habitacion, cliente, numeropersonas, inicio, final) VALUES (%s, %s, %s, %s, %s, %s)',
                    (random.randint(1,10000), int(room['idd']), cliente, numeropersonas, inicio, final))
    cur.execute('INSERT INTO Clientes (cid, nombre, apellido, identificacion, telefono, tarjeta) VALUES (%s, %s, %s, %s, %s, %s)', 
                (cliente, name, last_name, identificacion, phone_number, card_number))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
