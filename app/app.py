import pyodbc

from flask import Flask
from flask import render_template

app = Flask(__name__)

DRIVER = "SQL SERVER"
SERVER = "DESKTOP-773QVTP\SQLEXPRESS"
DATABASE = "GTS"
connection_string = f"""
    DRIVER={{{DRIVER}}};
    SERVER={SERVER};
    DATABASE={DATABASE};
    Trust_Connection=yes;
"""

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/theses")
def theses():
    return render_template("theses.html")

@app.route("/persons")
def persons():
    return render_template("persons.html")

@app.route("/universities")
def universities():
    return render_template("universities.html")

@app.route("/institutes")
def institutes():
    return render_template("institutes.html")

@app.route("/search")
def search():
    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)