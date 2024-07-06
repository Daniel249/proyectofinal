from flask import Flask, render_template, request, session,jsonify, redirect, url_for
import psycopg2
#import random
#import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='proyecto',
    user='postgres',
    password='admin',
    host='localhost'
)

@app.route('/check_subscription', methods=['POST'])
def check_subscription():
    data = request.get_json()
    title = data['title']
    
    # Check if the event title is in the subscribed events in the session
    is_subscribed = 'asistir' in session and title in session['asistir']
    
    return jsonify({"status": "subscribed" if is_subscribed else "unsubscribed", "title": title})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    title = data['title']
    
    # Add the event title to the subscribed events in the session
    if 'asistir' not in session:
        session['asistir'] = []
    
    if title not in session['asistir']:
        session['asistir'].append(title)
        session.modified = True

    user = session.get('user')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO atendimientos (cuenta, evento) VALUES (%s, %s);", (user['username'], title))
    conn.commit()
    print(title)
    cursor.close()
    
    return jsonify({"status": "subscribed", "title": title})

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    title = data['title']
    
    # Remove the event title from the subscribed events in the session
    if 'asistir' in session and title in session['asistir']:
        session['asistir'].remove(title)
        session.modified = True
    
    user = session.get('user')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM atendimientos WHERE cuenta = %s AND evento = %s;", (user['username'], title))
    conn.commit()
    print(title)
    #cursor.execute('SELECT evento FROM atendimientos WHERE cuenta = %s', (user['username'],))
    cursor.close()
    return jsonify({"status": "unsubscribed", "title": title})


@app.route('/perfil')
def perfil():
    if 'username' not in session:
        return redirect(url_for('login'))


    username = session['username']
    cursor = conn.cursor()

    # Obtener los eventos a los que el usuario está suscrito
    cursor.execute('SELECT evento FROM atendimientos WHERE cuenta = %s', (username,))
    subscribed_event_names = cursor.fetchall()
    
    # Extraer solo los nombres de los eventos en una lista
    subscribed_event_names = [event[0] for event in subscribed_event_names]
    print(subscribed_event_names)
    # Obtener detalles de los eventos suscritos
    if subscribed_event_names:
        format_strings = ','.join(['%s'] * len(subscribed_event_names))
        cursor.execute(f'SELECT nombre, organizador, linkfoto, descripcion, fecha, duracion, ciudad, direccion FROM eventos WHERE nombre IN ({format_strings})', tuple(subscribed_event_names))
        subscribed_events = cursor.fetchall()
    else:
        subscribed_events = []

    cursor.close()
    conn.close()

    return render_template('perfil.html', events=subscribed_events)

@app.route('/')
def index():
    user = session.get('user')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, organizador, linkfoto, descripcion, fecha, duracion, ciudad, direccion FROM eventos')
    events = cursor.fetchall()
    if(user):
        cursor.execute('SELECT evento FROM atendimientos WHERE cuenta = %s', (user['username'],))
        asistir = cursor.fetchall()
        asistir = [item for sublist in asistir for item in sublist]
    else:
        asistir = []
    session['asistir'] = asistir

    #print(user)
    print(asistir)
    cursor.close()
    #data_json = json.dumps(asistir)
    #return render_template('index.html', user=user, events=events, data_json=data_json)
    return render_template('index.html', user=user, events=events, asistir=asistir)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("entro en html")
    if request.method == 'POST':
        print("entro en post")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("marco las variables")
        # Insert data into the Cuentas table
        cursor = conn.cursor()
        print("se conecto exitosamente")
        cursor.execute('INSERT INTO public."cuentas" (usuario, correo, contrasena) VALUES (%s, %s, %s)', (username, email, password))
        print("realizo el insert")
        conn.commit()
        cursor.close()
        print("llego al final")
        return redirect(url_for('index'))
    print("renderea como siempre")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        testt = username


        # Verifica si el usuario existe en la base de datos
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cuentas WHERE usuario = %s AND contrasena = %s', (testt, password))
        user = cursor.fetchone()
        print("busca en la base de datos")
        cursor.close()

        if user:
            print("if user")
            session['user'] = {'username': user[0]}
            return redirect(url_for('index'))
        else:
            print("else not user")
            #return 'Nombre de usuario o contraseña incorrectos.'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/create_event', methods=['POST'])
def create_event():
    if 'user' in session and request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        image = request.form['image']
        organizador = request.form['organizador']
        lugar = request.form['lugar']
        fecha = request.form['fecha']
        ciudad = request.form['ciudad']
        duracion = request.form['duracion']
        # Insertar nuevo evento en la base de datos
    
        cursor = conn.cursor()
        cursor.execute('Select max(eventoid), COUNT(*) as cantidadFilas From eventos')
        temp = cursor.fetchone()
        if temp[1] == 0:
            eventoid = 0
        else:
            eventoid = temp[0] + 1
        cursor.execute('INSERT INTO eventos (nombre, descripcion, linkfoto, eventoid, organizador, direccion, fecha, ciudad, duracion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (title, description, image, eventoid, organizador, lugar, fecha, ciudad, duracion))
        conn.commit()
        cursor.close()

        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)