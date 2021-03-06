# Setting variables
from app import app
import os

# Todo - set MongoDB username and Password as variables for DB
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')
app.config['FLASK_PORT'] = int(os.getenv('FLASK_PORT', 5000))
app.config['CORS_DOMAIN'] = os.getenv('CORS_DOMAIN', '*')
app.config['FAUST_HOST'] = os.getenv('FAUST_HOST', 'http://localhost:6066')
app.config['SCRAPER_AGENT'] = os.getenv('SCRAPER_AGENT', 'http://localhost:7077')
app.config['MONGODB_SETTINGS'] = {
    'db': os.getenv('MONGO_DB', 'phishyme'),
    'host': os.getenv('DBHOST', 'localhost'),
    'port': int(os.getenv('DBPORT', 27017)),
    'username': os.getenv('MONGO_USER', None),
    'password': os.getenv('MONGO_PASSWORD', None),
}
