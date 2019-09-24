from flask import Flask, url_for, send_from_directory, request,render_template
import logging, os
from werkzeug import secure_filename
import numpy as np
import pandas as pd
import pandas_profiling

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/upload', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['file']:
    	app.logger.info(app.config['UPLOAD_FOLDER'])
    	csv = request.files['file']
    	csv_name = secure_filename(csv.filename)
    	create_new_folder(app.config['UPLOAD_FOLDER'])
    	saved_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
    	app.logger.info("saving {}".format(saved_path))
    	csv.save(saved_path)
    	return send_from_directory(app.config['UPLOAD_FOLDER'],csv_name, as_attachment=True)
    else:
    	return "Where is the image?"

def dataframe():
    files = []
    for i in os.listdir("./uploads"):
        if i.endswith('.csv'):
            files.append(i)
    app.logger.info("files {}".format(files))
    df = pd.read_csv("./uploads/"+files[0])
    return df

@app.route('/dataframe', methods=("POST", "GET"))
def html_table():

	df = dataframe()
	head = df.head(10).to_json()
	return render_template('template/dataframe_table.html',  tables=[df.to_html(classes='head')], titles=df.columns.values)

@app.route('/profile', methods=("POST", "GET"))
def profile():
    df = dataframe()
    profile = pandas_profiling.ProfileReport(df)
    profile.to_file(output_file="output.html")
    return render_template("output.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)