from flask import Flask,render_template,request,url_for,redirect,session,Response
from todo import app
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import requests
import re


app.secret_key = 'somesecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'todo'


mysql = MySQL(app)



def logged_in_status():
    status = False
    if 'loggedin' in session:
        status = True
    
    return status


@app.route('/')
def home_page():

    if  logged_in_status() == False and request.method == 'GET':
         return redirect(url_for('login'))
     
    elif logged_in_status() == True:
        username = session['username']
        id = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tasks where user_id = %s",(id,) )
        data = cursor.fetchall()
        return render_template('home.html',data = data)
       

@app.route('/insert',methods=['GET','POST'])
def insert_page():

  
    
    if request.method == 'POST':
        task =  request.form.get('task')
        start_date =  request.form.get('start_date')
        due_date =  request.form.get('end_date')
        user_id = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO `tasks`(`task_id`, `title`, `start_date`, `due_date`, `user_id`) VALUES (NULL,%s,%s,%s,%s)",(task,start_date,due_date,user_id));
        mysql.connection.commit()
        return redirect(url_for('home_page'))
    else:
        return redirect(url_for('register'))
    
@app.route('/delete/<string:task_id>', methods = ['GET'])
def delete(task_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = %s",(task_id,))
    mysql.connection.commit()
    return redirect(url_for('home_page'))


@app.route('/update/<string:task_id>',methods = ['GET','POST'])
def update(task_id):
       
         
       if request.method == "POST":
        task = request.form['task']
        start = request.form['start']
        end = request.form['end']
        user_id = session['id']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE tasks SET task_id = %s, title = %s, start_date = %s, due_date = %s, user_id = %s WHERE task_id = %s;",(task_id,task,start,end,user_id,task_id))
        mysql.connection.commit()
        return redirect(url_for('home_page'))
        
        

@app.route('/register',methods=['GET','POST'])
def register():

         
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
                
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * from user where username = %s ;",(username,))
        existing_user = cursor.fetchone()

        if existing_user:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute("INSERT INTO `user`(`id`, `username`, `email`, `password`) VALUES (NULL ,%s,%s,%s)",(username,email,password));
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for('login'))

        cursor.close()

    elif request.method == 'POST':
        msg = "Please fill out the form"

        
    return render_template('register.html',msg = msg)

            
    
@app.route('/login',methods=['GET','POST'])
def login():
    
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            msg = 'Logged in successfully'

            return redirect(url_for('home_page'))
        
    else:
        msg = "Incorrect credentials"
   
    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))