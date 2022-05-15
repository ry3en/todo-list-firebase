from flask import Flask, redirect, render_template, request, flash, url_for
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'AIzaSyBm9-0qUx0uyFIfHi_uh9Ws6pOGrD3gJsk'
# Configuraciones para firebase
cred = credentials.Certificate('serviceAccountKey.json')
fire = firebase_admin.initialize_app(cred)
db = firestore.client()
# tasks_ref = db.collection('tasks')
users_ref = db.collection('users')
tasks_ref = users_ref.document('mauro').collection('tasks')
API_KEY = 'AIzaSyBm9-0qUx0uyFIfHi_uh9Ws6pOGrD3gJsk'


def login_firebase(email, password):
    credentials = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(
        'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(API_KEY),
        data=credentials)
    if response.status_code == 200:
        content = response.content
        data = response.json()
        print(data['localId'])
    elif response.status_code == 400:
        print(response.content)

    return response.content


def read_tasks(ref):
    docs = ref.get()
    all_tasks = []
    for doc in docs:
        task = doc.to_dict()
        task['id'] = doc.id
        all_tasks.append(task)
    return all_tasks


def create_task(ref, task):
    new_task = {'name': task,
                'check': False,
                'fecha': datetime.datetime.now()}
    ref.document().set(new_task)


def update_task(ref, id):
    ref.document(id).update({'check': True})


def delete_task(ref, id):
    ref = ref.document(id).delete()


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_auth
    if request.method == 'GET':
        return render_template('login.html')
    else:  # POST
        email = request.form["email"]
        password = request.form["password"]
        print(f'{email}:{password}')
        try:
            if email == 'jose@correo.com' and password == 'con123':
                user_auth = True
                return redirect('/')
            else:
                print("Sesion fallida...")
                flash('Credenciales invalidas')
                return redirect('/')
        except:
            print("Sesion fallida...")
            flash('Credenciales invalidas')
            return redirect('/')
@app.route('/logout', methods=['POST'])
def logout():
    global user_auth
    user_auth = False
    return redirect('/')
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if user_auth:
            try:
                tasks = read_tasks(tasks_ref)
                completed = []
                incompleted = []
                for task in tasks:
                    print(task['check'])
                    if task['check'] == True:
                        completed.append(task)
                    else:
                        incompleted.append(task)
            except:
                print("Error...")
                tasks = []

            response = {'completed': completed,
                        'incompleted': incompleted,
                        'counter1': len(completed),
                        'counter2': len(incompleted)}
            return render_template('index.html', response=response)
        else:
            return redirect(url_for('login'))
    else:  # POST
        name = request.form["name"]
        print(f"\n{name}\n")


@app.route("/update/<string:id>", methods=['GET'])
def update(id):
    print(f"\nVas a actualizar la tarea: {id}\n")
    try:
        update_task(tasks_ref, id)
        return redirect('/')
    except:
        return render_template('error.html', response='response')


@app.route("/delete/<string:id>", methods=['GET'])
def delete(id):
    print(f"\nVas a borrar la tarea: {id}\n")

    try:
        delete_task(tasks_ref, id)
        print("Tarea eliminada...")
        return redirect('/')
    except:
        return render_template('error.html', response='response')


PORT = int(os.environ.get("PORT", 8080))
if __name__ == '__main__':
    app.run(debug=True)
