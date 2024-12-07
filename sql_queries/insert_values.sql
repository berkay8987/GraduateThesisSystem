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
	('Alper Ege', '�zt�rk'),
	('Berkay', 'Ate�'),
	('Ege Arda', 'Tepetan'),
	('Evrim', '�i�ek'),
	('Onur Ula�', 'Canpolat');

INSERT INTO
	Professors (prof_title, prof_name, prof_surname)
VALUES
	('Prof.', 'Volkan', 'Tunal�'),
	('', 'Oru� Raif', '�nv�ral'),
	('', 'Muhammed Burak', 'Alver'),
	('', 'Berkay', 'A��kuzun'),
	('', 'U�ur', 'Ta�');

INSERT INTO
	Universities (university_name)
VALUES
	('Maltepe �niversitesi'),
	('Marmara �niversitesi'),
	('�stanbul Teknik �niversitesi'),
	('Bo�azi�i �niversitesi'),
	('Y�ld�z Teknik �niversitesi');

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
	(1, 1), -- Volkan Tunal� is the supervisor of thesis 1
	(2, 2), -- Oru� Raif �nv�ral is the supervisor of thesis 2
	(3, 3), -- Muhammed Burak Alver is the supervisor of thesis 2
	(4, 4), -- Oru� Raif �nv�ral is the supervisor of thesis 2
	(5, 5); -- Oru� Raif �nv�ral is the supervisor of thesis 2

INSERT INTO 
	CoSupervisors
VALUES 
	()