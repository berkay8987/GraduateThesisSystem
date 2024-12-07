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
	Professors (prof_title, prof_name, prof_surname)
VALUES
	('Prof.', 'Volkan', 'Tunalý'),
	('MSc.', 'Oruç Raif', 'Önvüral'),
	('Ph.D.', 'Muhammed Burak', 'Alver'),
	('Yrd.', 'Berkay', 'Aþýkuzun'),
	('Dr.', 'Uður', 'Taþ'),

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
	Supervisors (prof_id, thesis_id)
VALUES	
	(1, 1), -- Prof. Volkan Tunalý is the supervisor of thesis 1
	(2, 2), -- MSc. Oruç Raif Önvüral is the supervisor of thesis 2
	(3, 3), -- Ph.D. Muhammed Burak Alver is the supervisor of thesis 3
	(4, 4), -- Yrd. Berkay Aþýkuzun is the supervisor of thesis 4
	(5, 5); -- Dr. Uður Taþ is the supervisor of thesis 5

INSERT INTO 
	CoSupervisors (prof_id, thesis_id)
VALUES 
	(1, 3), -- Prof. Volkan Tunalý is the co-supervisor of thesis 3
	(2, 4), -- MSc. Oruç Raif Önvüral is the co-supervisor of thesis 4
	(5, 2); -- Dr. Uður Taþ is the co-supervisor of thesis 2

INSERT INTO
	Topics (topic_name)
VALUES
	('Image Processing'),
	('Real-Time Scheduling'),
	('Renewable Energy Sources'),
	('Neural Networks'),
	('Global Climate Changes');

INSERT INTO
	ThesisTopics (thesis_id, topic_id)
VALUES
	(1, 1), -- => Thesis 1 is associated with topic 1 (Image Processing)
	(2, 2), -- => Thesis 2 is associated with topic 2 (Real-Time Scheduling)
	(3, 3), -- => Thesis 3 is associated with topic 3 (Renewable Energy Sources)
	(4, 4), -- => Thesis 4 is associated with topic 4 (Neural Networks)
	(5, 5); -- => Thesis 5 is associated with topic 5 (Global Climate Changes)

INSERT INTO
	Keywords (keyword)
VALUES
	('Image'),
	('CPU'),
	('Energy'),
	('Neurons'),
	('Climate');

INSERT INTO
	ThesisKeywords
VALUES
	(1, 1), -- => Thesis 1 is associated with keyword 1 (Image)
	(2, 2), -- => Thesis 2 is associated with keyword 2 (CPU)
	(3, 3), -- => Thesis 3 is associated with keyword 3 (Energy)
	(4, 4), -- => Thesis 4 is associated with keyword 4 (Neurons)
	(5, 5); -- => Thesis 5 is associated with keyword 5 (Climate)