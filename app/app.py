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
    cursor.execute("SELECT CONCAT(author_name, ' ', author_surname) FROM Authors")
    names = [name[0] for name in cursor.fetchall()]
    print(names)
    return render_template("index.html", names = names)

if __name__ == "__main__":
    app.run(debug=True)