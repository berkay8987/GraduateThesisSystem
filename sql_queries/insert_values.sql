/*
Tables:
	- Authors
	- CoSupervisors
	- Institutes
	- Keywords
	- Supervisors
	- Theses
	- ThesisKeywords
	- ThesisTopics
	- Topics
	- Universities
*/

USE GTS;

INSERT INTO 
	Authors (author_name, author_surname) 
VALUES 
	('Alper Ege', 'Öztürk'),
	('Berkay', 'Ateþ'),
	('Ege Arda', 'Tepetan'),
	('Evrim', 'Çiçek'),
	('Onur Ulaþ', 'Canpolat');

INSERT INTO
	Professors ()
VALUES
	();

INSERT INTO
	Universities (university_name)
VALUES
	('Maltepe Üniversitesi'),
	('Marmara Üniversitesi'),
	('Ýstanbul Teknik Üniversitesi'),
	('Boðaziçi Üniversitesi'),
	('Yýldýz Teknik Üniversitesi');

INSERT INTO 
	Institutes (institute_name, university_id)
VALUES
	('Engineering and Natural Sciences', 1),
	('Medicine', 2),
	('Business School', 3),
	('Law School', 4),
	('Architecture', 5);

INSERT INTO
	Theses (title, abstract, author_id, year, type, university_id, institute_id, page_num, language, submission_date)
VALUES  
	('Noise Reduction in Images', 'Techniques to enhance images by minimizing noise.', 1, 2023, 'Master', 1, 1, 149, 'French', '2023-11-26'),
	('CPU Scheduling Algorithms', 'Comparison of FCFS, SJF, and Round Robin methods.', 2, 2014, 'Doctorate', 2, 2, 89, 'English', '2014-01-30'),
	('Energy Storage Methods', 'Study of efficient renewable energy storage solutions.', 3, 2017, 'Master', 3, 3, 111, 'English', '2017-06-11'),
	('Deep Learning in NLP', 'Using neural networks to improve language processing.', 4, 2021, 'Master', 4, 4, 102, 'Turkish', '2021-02-23'),
	('Climate Change Impacts', 'Effects of climate change on global ecosystems.', 5, 2020, 'Doctorate', 5, 5, 65, 'English', '2020-09-02');


INSERT INTO 
	Supervisors
VALUES	
	('Prof. Volkan', 'Tunalý', 1),
	('Prof. Oruç Raif', 'Önvüral', 2),
	('Prof. Muhammed Burak', 'Alver', 3),
	('Prof. Berkay', 'Aþýkuzun', 4),
	('Prof. Uður', 'Taþ', 5);

INSERT INTO 
	CoSupervisors
VALUES 
	()