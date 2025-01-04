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

    cursor.execute("SELECT university_id, university_name FROM Universities")
    universities = cursor.fetchall()

    cursor.execute("SELECT institute_id, institute_name FROM Institutes")
    institutes = cursor.fetchall()

    cursor.execute("SELECT author_id, CONCAT(author_name, ' ', author_surname) FROM Authors")
    authors = cursor.fetchall()

    cursor.execute("SELECT topic_id, topic_name FROM Topics")
    topics = cursor.fetchall()

    # For supervisors, and cosupervisors
    cursor.execute("SELECT prof_id, CONCAT(prof_title, ' ', prof_name, ' ', prof_surname) FROM Professors")
    professors = cursor.fetchall()

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

    return render_template("theses.html", detailed_theses=detailed_theses, universities=universities, institutes=institutes, authors=authors, topics=topics, professors=professors)

@app.route("/edit_thesis/<int:id>", methods=["POST"])
def edit_thesis(id):

    title = request.form.get("title")
    abstract = request.form.get("description")
    language = request.form.get("language")
    page_num = request.form.get("page_num")

    cursor.execute("UPDATE Theses SET title = ?, abstract = ?, language = ?, page_num = ? WHERE thesis_id = ?", (title, abstract, language, page_num, id))
    cursor.commit()

    return render_template("result.html", response=f"Sucessfully Edited Thesis!", page="theses")

@app.route("/add_thesis", methods=["POST"])
def add_thesis():
    title = request.form.get("title")
    abstract = request.form.get("abstract")
    author = request.form.get("author")
    supervisor = request.form.get("supervisors")
    cosupervisor = request.form.get("cosupervisors")
    uni = request.form.get("uni")
    ins = request.form.get("ins")
    type = request.form.get("type")
    num_pages = request.form.get("num_pages")
    language = request.form.get("language")
    topics = request.form.get("topics")
    keywords = request.form.get("keywords")
    submission_date = request.form.get("submission_date")
    # get year from date
    year = submission_date[:4]

    tt = f"""
        <h4>{title}</h4>
        <h4>{abstract}</h4>
        <h4>{author}</h4>
        <h4>{supervisor}</h4>
        <h4>{cosupervisor}</h4>
        <h4>{uni}</h4>
        <h4>{ins}</h4>
        <h4>{type}</h4>
        <h4>{num_pages}</h4>
        <h4>{language}</h4>
        <h4>{topics}</h4>
        <h4>{keywords}</h4>
        <h4>{submission_date}</h4>
        <h4>{year}</h4>
    """

    # Update Theses table
    cursor.execute("""  
        INSERT INTO Theses
            (title, abstract, author_id, year, type, university_id, institute_id, page_num, language, submission_date) 
        VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (title, abstract, author, year, type, uni, ins, num_pages, language, submission_date))
    cursor.commit()

    cursor.execute("SELECT TOP 1 thesis_id FROM Theses ORDER BY thesis_id DESC;")
    thesis_id = cursor.fetchall()[0][0]


    # Update Supervisors
    cursor.execute("""
        INSERT INTO Supervisors
            (prof_id, thesis_id)
        VALUES
            (?, ?);
    """, (supervisor, thesis_id))
    cursor.commit()

    # Update CoSupervisors
    cursor.execute("""
        INSERT INTO CoSupervisors
            (prof_id, thesis_id)
        VALUES
            (?, ?);
    """, (cosupervisor, thesis_id))
    cursor.commit()

    # Update ThesisTopics
    cursor.execute("""
        INSERT INTO ThesisTopics
            (thesis_id, topic_id)
        VALUES
            (?, ?);
    """, (thesis_id, topics))
    cursor.commit()

    # Updating ThesisKeywords is gonna be different.
    # Since we might have multiple keywords associated with 1 thesis, there will be a loop
    # And we have to add the keywords into Keywords table (if that keyword doesn't exist)
    
    # Check if keyword exist
    keywords = [k.strip() for k in keywords.split(",")]

    for i in range(len(keywords)):
        cursor.execute("SELECT keyword_id FROM Keywords WHERE keyword = ?", (keywords[i]))
        res = cursor.fetchall()

        if res == []:
            # That means keyword doesn't exist, we first have to add it to Keywords table then add it to ThesisKeywords.
            cursor.execute("INSERT INTO Keywords (keyword) VALUES (?)", (keywords[i]))
            cursor.commit()

            # Get new keyword_id
            cursor.execute("SELECT keyword_id FROM Keywords WHERE keyword = ?", (keywords[i]))
            keyword_id = cursor.fetchall()[0][0]
            print(keyword_id)

            # Now update ThesisKeywords
            cursor.execute("INSERT INTO ThesisKeywords (thesis_id, keyword_id) VALUES (?, ?)", (thesis_id, keyword_id))
            cursor.commit()
        else:
            # That means keyword does exist, so we can directly add it to ThesisKeywords
            cursor.execute("INSERT INTO ThesisKeywords (thesis_id, keyword_id) VALUES (?, ?)", (thesis_id, res[0][0]))
            cursor.commit()

    return render_template("result.html", response=f"Sucessfully Added New Thesis => thesis_id = {thesis_id}", page="theses")

@app.route("/delete_thesis/<int:id>", methods=["POST"])
def delete_thesis(id):
    # In order to delete a thesis, we have to delete from other tables as well.

    # Delete from Supervisors
    cursor.execute("DELETE FROM Supervisors WHERE thesis_id = ?", id)
    cursor.commit()

    # Delete from CoSupervisors
    cursor.execute("DELETE FROM CoSupervisors WHERE thesis_id = ?", id)
    cursor.commit()
    
    # Delete from ThesisKeywords
    cursor.execute("DELETE FROM ThesisKeywords WHERE thesis_id = ?", id)
    cursor.commit()

    # Delete from ThesisTopics
    cursor.execute("DELETE FROM ThesisTopics WHERE thesis_id = ?", id)
    cursor.commit()

    cursor.execute("DELETE FROM Theses WHERE thesis_id = ?", id)
    return render_template("result.html", response=f"Sucessfully Deleted Theses => thesis_id {id}", page="theses")

@app.route("/persons")
def persons():
    cursor.execute("SELECT author_id, author_name, author_surname FROM Authors")
    authors_content = cursor.fetchall()
    cols = ["author_id", "author_name", "author_surname"]
    authors = [dict(zip(cols, c)) for c in authors_content]

    cursor.execute("SELECT prof_id, prof_title, prof_name, prof_surname FROM Professors")
    professors_content = cursor.fetchall()
    cols = ["prof_id", "prof_title", "prof_name", "prof_surname"]
    professors = [dict(zip(cols, c)) for c in professors_content]

    return render_template("persons.html", authors=authors, professors=professors)

@app.route("/add_author", methods=["POST"])
def add_author():
    name = request.form.get("name")
    surname = request.form.get("surname")
    cursor.execute("INSERT INTO Authors (author_name, author_surname) VALUES (?,?)", (name, surname))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Added New Author => {name} {surname} - {id}", page="persons")

@app.route("/edit_author/<int:id>", methods=["POST"])
def edit_author(id):
    name = request.form.get("name")
    surname = request.form.get("surname")
    cursor.execute("UPDATE Authors SET author_name = ?, author_surname = ? WHERE author_id = ?", (name, surname, id))

    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Edited Author => author_id = {id}", page="persons")

@app.route("/delete_author/<int:id>", methods=["POST"])
def delete_author(id):
    try:
        cursor.execute("DELETE FROM Authors WHERE author_id = ?", id)
        cursor.commit()
    except pyodbc.Error as e:
        return render_template("result.html", response=f"Failed to Delete Author => author_id = {id}\n {e}", page="persons", error=True)
    return render_template("result.html", response=f"Sucessfully Deleted Author => author_id = {id}", page="persons")

@app.route("/add_prof", methods=["POST"])
def add_prof():
    title = request.form.get("title")
    name = request.form.get("name")
    surname = request.form.get("surname")
    cursor.execute("INSERT INTO Professors (prof_title, prof_name, prof_surname) VALUES (?,?,?)", (title, name, surname))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Added New Professor => {title} {name} {surname} - {id}", page="persons")

@app.route("/edit_prof/<int:id>", methods=["POST"])
def edit_prof(id):
    title = request.form.get("title")
    name = request.form.get("name")
    surname = request.form.get("surname")
    cursor.execute("UPDATE Professors SET prof_title = ?, prof_name = ?, prof_surname = ? WHERE prof_id = ?", (title, name, surname, id))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Edited Professor => prof_id = {id}", page="persons")

@app.route("/delete_prof/<int:id>", methods=["POST"])
def delete_prof(id):
    cursor.execute("DELETE FROM Professors WHERE prof_id = ?", id)
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Deleted Professor => prof_id = {id}", page="persons")

@app.route("/universities")
def universities():
    cursor.execute("SELECT university_id, university_name FROM Universities")
    content = cursor.fetchall()
    cols = ["university_id", "university_name"]
    universities = [dict(zip(cols, c)) for c in content]
    return render_template("universities.html", universities=universities)

@app.route("/edit_university/<int:id>", methods=["POST"])
def edit_university(id):
    name = request.form.get("name")
    cursor.execute("UPDATE Universities SET university_name = ? WHERE university_id = ?", (name, id))
    return render_template("result.html", response=f"Sucessfully Edited University => university_id = {id}", page="universities")

@app.route("/delete_university/<int:id>", methods=["POST"])
def delete_university(id):
    cursor.execute("DELETE FROM Universities WHERE university_id = ?", id)
    return render_template("result.html", response=f"Sucessfully Deleted University => university_id = {id}", page="universities")

@app.route("/add_university", methods=["POST"])
def add_university():
    name = request.form.get("name")

    # Check if already exists
    cursor.execute("SELECT university_id FROM Universities WHERE university_name = ?", (name))
    uni = cursor.fetchall()

    if uni:
        return "<h1>That University Already Exists!</h1>"
    
    cursor.execute("INSERT INTO Universities (university_name) VALUES (?)", name)
    cursor.commit()

    return render_template("result.html", response=f"Sucessfully Added New University => {name} - {id}", page="universities")

@app.route("/institutes")
def institutes():
    cursor.execute("SELECT university_id, university_name FROM Universities")
    content = cursor.fetchall()
    cols = ["university_id", "university_name"]
    universities = [dict(zip(cols, c)) for c in content]

    cursor.execute("""
        SELECT 
            I.institute_id,
            I.institute_name,
            U.university_name
        FROM 
            Institutes I
        JOIN 
            Universities U ON I.university_id = U.university_id
    """)
    content = cursor.fetchall()
    cols = ["institute_id", "institute_name", "university_name"]
    institutes = [dict(zip(cols, c)) for c in content]
    return render_template("institutes.html", institutes=institutes, universities=universities)

@app.route("/add_institute", methods=["POST"])
def add_institute():
    name = request.form.get("name")
    uni_id = request.form.get("uni")

    cursor.execute("INSERT INTO Institutes (institute_name, university_id) VALUES (?, ?)", (name, uni_id))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Added New Institute => {name}", page="institutes")

@app.route("/delete_institute/<int:id>", methods=["POST"])
def delete_institute(id):
    cursor.execute("DELETE FROM Institutes WHERE institute_id = ?", id)
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Deleted Institute => institute_id = {id}", page="institutes")

@app.route("/edit_institute/<int:id>", methods=["POST"])
def edit_institute(id):
    name = request.form.get("name")
    cursor.execute("UPDATE Institutes SET institute_name = ? WHERE institute_id = ?", (name, id))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Edited Institute => institute_id = {id}", page="institutes")

@app.route("/topics")
def topics():
    cursor.execute("SELECT topic_id, topic_name FROM Topics")
    content = cursor.fetchall()
    cols = ["topic_id", "topic_name"]
    topics = [dict(zip(cols, c)) for c in content]
    return render_template("topics.html", topics=topics)

@app.route("/add_topic", methods=["POST"])
def add_topic():
    name = request.form.get("name")

    # Check if exists
    cursor.execute("SELECT topic_id FROM Topics WHERE topic_name = ?", name)
    res = cursor.fetchall()

    if res:
        return render_template("result.html", response=f"Failed to Add Topic, '{name}' already exists!", page="topics", error=True)

    # If not, add
    cursor.execute("INSERT INTO Topics (topic_name) VALUES (?)", name)
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Added New Topic => {name}", page="topics")

@app.route("/delete_topic/<int:id>", methods=["POST"])
def delete_topic(id):
    cursor.execute("DELETE FROM Topics WHERE topic_id = ?", id)
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Deleted Topic => topic_id = {id}", page="topics")

@app.route("/edit_topic/<int:id>", methods=["POST"])
def edit_topic(id):
    name = request.form.get("name")
    cursor.execute("UPDATE Topics SET topic_name = ? WHERE topic_id = ?", (name, id))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Edited Topic => topic_id = {id}", page="topics")

@app.route("/keywords")
def keywords():
    cursor.execute("SELECT keyword_id, keyword FROM Keywords")
    keyword_content = cursor.fetchall()
    cols = ["keyword_id", "keyword_name"]
    keywords = [dict(zip(cols, c)) for c in keyword_content]

    return render_template("keywords.html", keywords=keywords)

@app.route("/add_keyword", methods=["POST"])
def add_keyword():
    keyword = request.form.get("name")
    
    # Check if keyword already exists
    cursor.execute("SELECT keyword_id FROM Keywords WHERE keyword = ?", keyword)
    kid = cursor.fetchall()

    if kid:
        return render_template("result.html", response=f"Keyword Already Exists! => keyword_id = {kid[0][0]}", page="keywords", error=True)

    cursor.execute("INSERT INTO Keywords (keyword) VALUES (?)", keyword)
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Added New Keyword => {keyword}", page="keywords")

@app.route("/edit_keyword/<int:id>", methods=["POST"])
def edit_keyword(id):
    keyword = request.form.get("name")
    cursor.execute("UPDATE Keywords SET keyword = ? WHERE keyword_id = ?", (keyword, id))
    cursor.commit()
    return render_template("result.html", response=f"Sucessfully Edited Keyword => keyword_id = {id}", page="keywords")

@app.route("/delete_keyword/<int:id>", methods=["POST"])
def delete_keyword(id):
    try:
        cursor.execute("DELETE FROM Keywords WHERE keyword_id = ?", id)
        cursor.commit()
    except pyodbc.Error as e:
        return render_template("result.html", response="Cannot delete keyword as it's being used by (a) thesis.", page="keywords", error=True)
    return render_template("result.html", response=f"Sucessfully Deleted Keyword => keyword_id = {id}", page="keywords")

@app.route("/search")
def search():
    cursor.execute("SELECT author_id, CONCAT(author_name, ' ', author_surname) FROM Authors")
    author_content = cursor.fetchall()
    cols = ["author_id", "author_name"]
    authors = [dict(zip(cols, c)) for c in author_content] 

    # For supervisors and cosupervisors
    cursor.execute("SELECT prof_id, CONCAT(prof_title, ' ', prof_name, ' ', prof_surname) FROM Professors")
    profs_content = cursor.fetchall()
    cols = ["prof_id", "prof_name"]
    profs = [dict(zip(cols, c)) for c in profs_content]

    cursor.execute("SELECT university_id, university_name FROM Universities")
    university_content = cursor.fetchall()
    cols = ["university_id", "university_name"]
    universities = [dict(zip(cols, c)) for c in university_content]

    cursor.execute("SELECT institute_id, institute_name FROM Institutes")
    institute_content = cursor.fetchall()
    cols = ["institute_id", "institute_name"]
    institutes = [dict(zip(cols, c)) for c in institute_content]

    cursor.execute("SELECT keyword_id, keyword FROM Keywords")
    keyword_content = cursor.fetchall()
    cols = ["keyword_id", "keyword"]
    keywords = [dict(zip(cols, c)) for c in keyword_content]

    cursor.execute("SELECT topic_id, topic_name FROM Topics")
    topic_content = cursor.fetchall()
    cols = ["topic_id", "topic_name"]
    topics = [dict(zip(cols, c)) for c in topic_content]
    
    return render_template("search.html", authors=authors, profs=profs, universities=universities, institutes=institutes, keywords=keywords, topics=topics)

@app.route("/search_by_thesis_id/", methods=["POST"])
def search_by_thesis_id():
    thesis_id = request.form.get("thesis_id")

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
        WHERE 
            T.thesis_id = ?
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """, thesis_id)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_author", methods=["POST"])
def search_by_author():
    author = request.form.get("author")

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
        WHERE 
            T.author_id = ?
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """, author)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_supervisor", methods=["POST"])
def search_by_supervisor():
    prof = request.form.get("supervisor")

    cursor.execute("SELECT thesis_id FROM Supervisors WHERE prof_id = ?", prof)
    thesis_ids = cursor.fetchall()

    detailed_content = []
    for t in thesis_ids:
        
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
            WHERE 
                T.thesis_id = ?
            GROUP BY 
                T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
                P1.prof_title, P1.prof_name, P1.prof_surname, 
                P2.prof_title, P2.prof_name, P2.prof_surname, 
                T.type, U.university_name, I.institute_name, 
                T.submission_date, T.page_num, T.year, T.language
            ORDER BY 
                T.thesis_id;
        """, t[0])
        detailed_content += cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_cosupervisor", methods=["POST"])
def search_by_cosupervisor():
    prof = request.form.get("cosupervisor")

    cursor.execute("SELECT thesis_id FROM CoSupervisors WHERE prof_id = ?", prof)
    thesis_ids = cursor.fetchall()

    detailed_content = []
    for t in thesis_ids:
        
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
            WHERE 
                T.thesis_id = ?
            GROUP BY 
                T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
                P1.prof_title, P1.prof_name, P1.prof_surname, 
                P2.prof_title, P2.prof_name, P2.prof_surname, 
                T.type, U.university_name, I.institute_name, 
                T.submission_date, T.page_num, T.year, T.language
            ORDER BY 
                T.thesis_id;
        """, t[0])
        detailed_content += cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_language", methods=["POST"])
def search_by_language():
    language = request.form.get("language")

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
        WHERE 
            T.language = ?    
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """, language)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_university", methods=["POST"])
def search_by_university():
    uni = request.form.get("university")

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
        WHERE 
            T.university_id = ?    
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """, uni)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_institute", methods=["POST"])
def search_by_institute():
    ins = request.form.get("institute")

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
        WHERE 
            T.institute_id = ?    
        GROUP BY 
            T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
            P1.prof_title, P1.prof_name, P1.prof_surname, 
            P2.prof_title, P2.prof_name, P2.prof_surname, 
            T.type, U.university_name, I.institute_name, 
            T.submission_date, T.page_num, T.year, T.language
        ORDER BY 
            T.thesis_id;
    """, ins)
    detailed_content= cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_topic", methods=["POST"])
def search_by_topic():
    topic_id = request.form.get("topic")

    cursor.execute("SELECT thesis_id FROM ThesisTopics WHERE topic_id = ?", topic_id)
    thesis_ids = cursor.fetchall()

    detailed_content = []
    for t in thesis_ids:
        
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
            WHERE 
                T.thesis_id = ?
            GROUP BY 
                T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
                P1.prof_title, P1.prof_name, P1.prof_surname, 
                P2.prof_title, P2.prof_name, P2.prof_surname, 
                T.type, U.university_name, I.institute_name, 
                T.submission_date, T.page_num, T.year, T.language
            ORDER BY 
                T.thesis_id;
        """, t[0])
        detailed_content += cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

@app.route("/search_by_keyword", methods=["POST"])
def search_by_keyword():
    keyword_id = request.form.get("keyword")

    cursor.execute("SELECT thesis_id FROM ThesisKeywords WHERE keyword_id = ?", keyword_id)
    thesis_ids = cursor.fetchall()

    detailed_content = []
    for t in thesis_ids:
        
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
            WHERE 
                T.thesis_id = ?
            GROUP BY 
                T.thesis_id, T.title, A.author_name, A.author_surname, T.abstract, 
                P1.prof_title, P1.prof_name, P1.prof_surname, 
                P2.prof_title, P2.prof_name, P2.prof_surname, 
                T.type, U.university_name, I.institute_name, 
                T.submission_date, T.page_num, T.year, T.language
            ORDER BY 
                T.thesis_id;
        """, t[0])
        detailed_content += cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    detailed_theses = [dict(zip(cols, c)) for c in detailed_content]

    return render_template("search_result.html", detailed_theses=detailed_theses)

if __name__ == "__main__":
    app.run(debug=True)