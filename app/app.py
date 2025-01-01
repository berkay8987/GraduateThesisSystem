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
    """ Main page of the app """
    return render_template("index.html")

@app.route("/theses")
def theses():
    """ Get theses from database, show it to the user. Make them be able to add, edit or delete a thesis """
    cursor.execute("SELECT * FROM Theses")
    content = cursor.fetchall()

    col = [desc[0] for desc in cursor.description]

    theses = [dict(zip(col, c)) for c in content]

    return render_template("theses.html", theses=theses)

@app.route("/persons")
def persons():
    return render_template("persons.html")

@app.route("/universities")
def universities():
    return render_template("universities.html")

@app.route("/institutes")
def institutes():
    return render_template("institutes.html")

@app.route("/topics")
def topics():
    return render_template("topics.html")

@app.route("/search")
def search():
    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)