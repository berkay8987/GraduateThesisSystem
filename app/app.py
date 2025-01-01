import pyodbc

from flask import Flask
from flask import render_template
from flask import request

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

    cursor.execute("""
        SELECT 
            T.thesis_id,
            T.title AS thesis_title,
            A.author_name + ' ' + A.author_surname AS author_full_name,
            T.abstract AS thesis_abstract,
            P1.prof_title + ' ' + P1.prof_name + ' ' + P1.prof_surname AS supervisor_full_name,
            P2.prof_title + ' ' + P2.prof_name + ' ' + P2.prof_surname AS cosupervisor_full_name,
            T.type AS thesis_type,
            U.university_name,
            I.institute_name,
            T.submission_date,
            T.page_num,
            T.year,
            T.language,
            STRING_AGG(K.keyword, ', ') AS thesis_keywords,
            STRING_AGG(Tto.topic_name, ', ') AS thesis_topics
        FROM 
            Theses T
        JOIN 
            Authors A ON T.author_id = A.author_id
        LEFT JOIN 
            Supervisors S ON T.thesis_id = S.thesis_id
        LEFT JOIN 
            Professors P1 ON S.prof_id = P1.prof_id
        LEFT JOIN 
            CoSupervisors CS ON T.thesis_id = CS.thesis_id
        LEFT JOIN 
            Professors P2 ON CS.prof_id = P2.prof_id
        JOIN 
            Universities U ON T.university_id = U.university_id
        JOIN 
            Institutes I ON T.institute_id = I.institute_id
        LEFT JOIN 
            ThesisKeywords TK ON T.thesis_id = TK.thesis_id
        LEFT JOIN 
            Keywords K ON TK.keyword_id = K.keyword_id
        LEFT JOIN 
            ThesisTopics TT ON T.thesis_id = TT.thesis_id
        LEFT JOIN 
            Topics Tto ON TT.topic_id = Tto.topic_id
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("theses.html", detailed_theses=detailed_theses)

@app.route("/edit_thesis/<int:id>", methods=["POST"])
def edit_thesis(id):

    title = request.form.get("title")
    abstract = request.form.get("description")
    language = request.form.get("language")
    page_num = request.form.get("page_num")

    cursor.execute("UPDATE Theses SET title = ?, abstract = ?, language = ?, page_num = ? WHERE thesis_id = ?", (title, abstract, language, page_num, id))
    cursor.commit()

    return render_template("index.html") 

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