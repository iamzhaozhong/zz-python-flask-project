from flask import Flask  # Server & Routes
from flask import request  # Parsing HTTP requests
from flask import jsonify  # Converting Python dictionaries into JSON
import wbgapi as wb

from peewee import *  # Python Classes to SQL Tables
import psycopg2
from playhouse.shortcuts import model_to_dict  # Convert Peewee Model to Dictionary

# Create our database object for Python
# Assumes we have a database called 'people' and a user named 'postgres'
db = PostgresqlDatabase('python_flask_project', user = 'zhaozhong', password = '', host = 'localhost', port = 5432)


# Base model that all models will extend from that establishes relationship to database
class BaseModel(Model):
    class Meta:
        database = db


class Countries(BaseModel):
    country_code = CharField()
    country_name = CharField()
    income_level = CharField()
    capital_city = CharField()


class GDP(BaseModel):
    value_in_USD = FloatField(null = True)
    series = CharField()
    country_code = CharField(null = True)
    fiscal_year = CharField()


# Gross National Income PCAP
class GNI(BaseModel):
    value_in_USD = FloatField(null = True)
    series = CharField()
    country_code = CharField()
    fiscal_year = CharField()


db.connect()  # Connect to the database
db.drop_tables([Countries, GDP, GNI])
db.create_tables([Countries, GDP, GNI], safe = True)  # Create the Person table


# Grab the data from WB
def country_instance():
    wb_countries = wb.economy.list()
    for x in wb_countries:
        x = Countries(country_code = x['id'], country_name = x['value'], income_level = x['incomeLevel'],
                      capital_city = x['capitalCity'])
        x.save()


def gdp_instance():
    wb_gdp = wb.data.fetch('NY.GDP.PCAP.CD', mrv = 5)
    response = []
    for row in wb_gdp:
        response.append(row)
    for x in response:
        x = GDP(value_in_USD = x['value'], series = x['series'], country_code = x['economy'], fiscal_year = x['time'])
        x.save()


def gni_instance():
    wb_gni = wb.data.fetch('NY.GNP.PCAP.CD', mrv = 5)
    response = []
    for row in wb_gni:
        response.append(row)
    for x in response:
        x = GNI(value_in_USD = x['value'], series = x['series'], country_code = x['economy'], fiscal_year = x['time'])
        x.save()


country_instance()
gdp_instance()
gni_instance()

app = Flask(__name__)


# Define the route '/economy'
@app.route('/economy', methods = ['GET'])
@app.route('/economy/<string:country>', methods = ['GET'])
def economy(country = None):
    if country:
        result = []
        for x in Countries.select().where(Countries.country_code == country):
            result.append(model_to_dict(x))
        return jsonify(result)
    else:
        result = []
        for x in Countries.select():
            result.append(model_to_dict(x))
        return jsonify(result)


# Define a '/gdp' endpoint that accepts GET requests
@app.route('/gdp', methods = ['GET'])
@app.route('/gdp/<string:param>', methods = ['GET'])
def gdp(param = None):
    if param:
        while param.isdigit():
            gdp = GDP.get(GDP.id == param)
            gdp = model_to_dict(gdp)
            return jsonify(gdp)
        while param.isalpha():
            gdp = []
            for x in GDP.select().where(GDP.country_code == param):
                gdp.append(model_to_dict(x))
            return jsonify(gdp)
    else:
        gdp = []
        for x in GDP.select():
            gdp.append(model_to_dict(x))
        return jsonify(gdp)


# Define a '/gdp' endpoint that accepts GET requests
@app.route('/gni', methods = ['GET'])
@app.route('/gni/<string:var>', methods = ['GET'])
def gni(var = None):
    if var:
        while var.isdigit():
            gni = GNI.get(GDP.id == var)
            gni = model_to_dict(gni)
            return jsonify(gni)
        while var.isalpha():
            gni = []
            for x in GNI.select().where(GNI.country_code == var):
                gni.append(model_to_dict(x))
            return jsonify(gni)
    else:
        gni = []
        for x in GNI.select():
            gni.append(model_to_dict(x))
        return jsonify(gni)


# Start server, listen on port 9000 and re-start server on file change
app.run(port = 9000, debug = True)
