

from flask import Flask,render_template,g,jsonify,request
import pyowm,os,sqlite3,json #pyown wrapper library for open weather api


app =  Flask(__name__)
## Fethcing the database configuration from app.conf filename
app.config.from_pyfile(os.path.join(".", "config/app.conf"), silent=False)

## Updating the dict of app configuration
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, str(app.config.get('DATABASE')[0])),
    SECRET_KEY=app.config.get('SECRET_KEY'),
    USERNAME=app.config.get('USERNAME'),
    PASSWORD=app.config.get('PASSWORD')
))

## Passing  the API_KEY to Pyowm object
owm = pyowm.OWM(app.config.get('API_KEY'))  # You MUST provide a valid API key


@app.route('/')
def index():

    return render_template('index.html')
## Connecting to sqlite  database
## Database value will be fetched from the dict created from the values present in app.config
## sqlite3.Row : This would use Row objects rather than dicts to return the results of queries

def connect_db():
    '''
    Connect to the database
    '''
    db = getattr(g, '_database', None)
    if db is None:
        conn = g._database = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
    return conn


def get_db():
    '''
    Opens a new database connection if there is none yet for the
    current application context
    '''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    '''
    Closes the database again at the end of request
    '''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

## Initial the database by reading the sql file and creating  the required tables in database
def init_db():
    '''
    Initialize database
    '''
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    load_city_info_db()
    db.commit()


## Custom command while initalizing the DATABASE
## Initialize DB with Following initdb_command
## Flask intidb
@app.cli.command('initdb')
def initdb_command():
    '''
    Initializes the database
    '''
    init_db()
    print('Initialized the database.')


## Loading the Data from the Json we dowmloaded into database
## We will use the file open and run a cusrsor to insert each record into DATABASE
## We are fetchin id,country,code, longitude and latititude from the json file
def load_city_info_db():
    '''
    Load city info to database
    '''
    db = get_db()
    with open('city.list.json',encoding="utf8") as f:
        for line in f:
            j = json.loads(line)
            db.cursor().execute('insert into cities (id, city, country_code, lon, lat) values (?, ?, ?, ?, ?)',
                               (j['_id'], j['name'], j['country'], j['coord']['lon'], j['coord']['lat']))

##  We will look into functional for context weather /weather
## Whenever /weather is passed we need to fetch details from the database for the Id
## We will verify if the city/code passed are valid from the json we stored in DATABASEself.

@app.route('/search/', methods = ['GET'])
def search():
    '''
    Function to search if the city and code are Valid.
    returns: data in json format
    '''
    db = get_db()
    value = request.args.get('city') + '%'
    q = db.cursor().execute("select distinct city,country_code,lon,lat from cities where city like ? order by city,country_code",[value])
    res = [x for x in q]
    data = []
    for i in res:
        data.append({'label' : i[0] + ' ' + i[1], 'city' : i[0],'country_code' : i[1]})
    return jsonify(json_data = data)
