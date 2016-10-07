from flask import Flask, request, render_template, redirect, session, flash
from mysqlconnection import MySQLConnector
import hashlib
import random
import string
import re 
import md5
import os, binascii
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
from flask.ext.bcrypt import Bcrypt
app =Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key="ThisIsSecret"
mysql = MySQLConnector(app,'Walltwo')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/wall', methods=['post'])
def register_page():
	return render_template('register.html')

@app.route('/login', methods=['post'])
def login_page():
	return render_template('login.html')

@app.route('/process', methods=['post'])
def register():
	isvalid=True
	if len(request.form['first'])<1:
		flash("Name cannot be blank")
		isvalid= False
	if len(request.form['last'])<1:
		flash("Last name cannot be blank")
		isvalid= False
	if len(request.form['email'])<1:
		flash("Email cannot be blank")
		isvalid=False
	if len(request.form['password'])<1:
		flash("Password cannto be blank")
		isvalid= False
	if isvalid==False:
		return render_template('register.html')
	else:
		salt = "".join( [random.choice(string.letters) for i in xrange(15)] )
		pw_hash = salt + request.form['password'];
		output_hash = hashlib.sha256(pw_hash).hexdigest()
				
		query = "INSERT INTO users (first_name, last_name, email,  pw_hash, salt,  created_at, updated_at) Values(:first, :last, :email, :pw_hash, :salt, NOW(), NOW())"
		data= {
				'first':request.form['first'],
				'last':request.form['last'],
				'email':request.form['email'],
				'pw_hash':request.form['password'], 
				'salt':salt, 
				'pw_hash':output_hash		
		}
		mysql.query_db(query, data)
	return render_template('message.html')

@app.route('/signin', methods=['Post'])
def login():

	query= "SELECT * FROM users WHERE email = :email LIMIT 1"
	data= {'email':request.form['email']}
	rows=mysql.query_db(query, data)

	if len(rows)==0:
		flash("Sorry, there is no match for that email address")
		return render_template('login.html')
	user = rows[0]
	password_guess= request.form['password']
	salt = user['salt']
	output_hash= user['pw_hash']

	text= salt + password_guess
	new_hash= hashlib.sha256(text).hexdigest()

	if new_hash== output_hash:
		session ['logged_in_as']= user['id']
		return render_template ('message.html')
	else:
		flash ("wrong password")
		return redirect('/login')
@app.route('/message', methods=['post'])
def message():
	
	return render_template('message.html')
	



app.run(debug=True)
