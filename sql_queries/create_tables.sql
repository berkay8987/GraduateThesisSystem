-- START 

-- VARIABLES  

-- Thesis No: INT MAX 7 DIGIT 0 - 9,999,999
-- Title MAX 500C CHAR
-- Abstract (desc) MAX 5000 CHAR 
-- Author 
-- Year
-- Type => Master, Doctorate, Specialization in Medicine, Proficiency in Art
-- University
-- Institute
-- Num of pages (thesis pages i guess?)
-- Language of the thesis text
-- Submission date
-- Supervisor
-- Co Supervisor can be null (opt.)
-- keywords

-- TABLES 

-- Thesis => Theses No, Title, Abstract, Author, Year, Type, UNiverity, Insitute, num, lang, sub_date, supervisor, co_superviser
-- Topics => Topic No, Topic


-- TODO: ADD Author birth year, Thesis count, e-mail, 


USE GTS;

CREATE TABLE Authors (
	author_id INT IDENTITY(1,1) PRIMARY KEY,
	author_name VARCHAR(255) NOT NULL,
	author_surname VARCHAR(255) NOT NULL,
);

CREATE TABLE Professors (
	prof_id INT IDENTITY(1,1) PRIMARY KEY,
	prof_name VARCHAR(255) NOT NULL,
	prof_surname VARCHAR(255) NOT NULL,
);

CREATE TABLE Universities (
	university_id INT IDENTITY(1,1) PRIMARY KEY,
	university_name VARCHAR(255) NOT NULL,
);

CREATE TABLE Institutes (
	institute_id INT IDENTITY(1,1) PRIMARY KEY,
	institute_name VARCHAR(255) NOT NULL,
	university_id INT NOT NULL,

	FOREIGN KEY (university_id) REFERENCES Universities(university_id),
);

CREATE TABLE Theses (
	thesis_id INT IDENTITY(1,1) PRIMARY KEY CHECK (thesis_id >= 0 AND thesis_id <= 9999999),
	title VARCHAR(500) NOT NULL,
	abstract VARCHAR(5000) NOT NULL,
	author_id INT NOT NULL,
	year INTEGER NOT NULL,
	type VARCHAR(26) CHECK (type IN ('Master', 'Doctorate', 'Specialization in Medicine', 'Proficiency in Art')),
	university_id INT NOT NULL,
	institute_id INT NOT NULL,
	page_num INT NOT NULL,
	language VARCHAR(10) CHECK (language in ('Turkish', 'English', 'French')),
	submission_date DATE NOT NULL,

	FOREIGN KEY (author_id) REFERENCES Authors(author_id),
	FOREIGN KEY (university_id) REFERENCES Universities(university_id),
	FOREIGN KEY (institute_id) REFERENCES Institutes(institute_id)
);

CREATE TABLE Supervisors (
	supervisor_id INT IDENTITY(1,1) PRIMARY KEY,
	prof_id INT NOT NULL,
	thesis_id INT NOT NULL

	FOREIGN KEY (prof_id) REFERENCES Professors(prof_id),
	FOREIGN KEY (thesis_id) REFERENCES Theses(thesis_id),
);

CREATE TABLE CoSupervisors (
	cosupervisor_id INT IDENTITY(1,1) PRIMARY KEY,
	prof_id INT NOT NULL,
	thesis_id INT NOT NULL,

	FOREIGN KEY (prof_id) REFERENCES Professors(prof_id),
	FOREIGN KEY (thesis_id) REFERENCES Theses(thesis_id),
);

-- MAYBE LATER
/*
CREATE TABLE Thesis_Supervisors (
	thesis_id INT NOT NULL,
	supervisor_id INT NOT NULL,

	PRIMARY KEY (thesis_id, supervisor_id),
	FOREIGN KEY (thesis_id) REFERENCES Theses(thesis_id),
	FOREIGN KEY (supervisor_id) REFERENCES Supervisors(supervisor_id),
);
*/

CREATE TABLE Topics (
	topic_id INT IDENTITY(1,1) PRIMARY KEY,
	topic_name VARCHAR(255) NOT NULL,
);

CREATE TABLE ThesisTopics (
	thesis_id INT NOT NULL,
	topic_id INT NOT NULL,

	PRIMARY KEY (thesis_id, topic_id),
	FOREIGN KEY (thesis_id) REFERENCES Theses(thesis_id),
	FOREIGN KEY (topic_id) REFERENCES Topics(topic_id),
);

CREATE TABLE Keywords (
	keyword_id INT IDENTITY(1,1) PRIMARY KEY,
	keyword VARCHAR(255) NOT NULL,
);

CREATE TABLE ThesisKeywords (
	thesis_id INT NOT NULL,
	keyword_id INT NOT NULL,

	PRIMARY KEY (thesis_id, keyword_id),
	FOREIGN KEY (thesis_id) REFERENCES Theses(thesis_id),
	FOREIGN KEY (keyword_id) REFERENCES Keywords(keyword_id),
);
