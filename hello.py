from flask import Flask,render_template

app =  Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello/<int:name>')
def hello_world(name):
    return render_template('hello.html',t_planet = name)
