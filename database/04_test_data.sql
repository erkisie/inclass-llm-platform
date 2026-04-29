-- ==============================================================================
-- 1. Instructors
-- ==============================================================================
INSERT INTO instructors (instructor_email, instructor_name, password)
VALUES 
('bekmezcii@mef.edu.tr', 'İlker Bekmezci', 'ilker123'),
('demirse@mef.edu.tr', 'Şeniz Demir', 'şeniz123')
ON CONFLICT (instructor_email) DO UPDATE 
SET instructor_name = EXCLUDED.instructor_name, password = EXCLUDED.password;

-- ==============================================================================
-- 2. Students
-- ==============================================================================
INSERT INTO students (student_email, student_name, password)
VALUES 
('zerdalib@mef.edu.tr', 'Beyza Zerdalı', 'beyza123'),
('erkisie@mef.edu.tr', 'Elif Erkişi', 'elif123'),
('yayimlid@mef.edu.tr', 'Derin Yayımlı', 'derin123')
ON CONFLICT (student_email) DO UPDATE 
SET student_name = EXCLUDED.student_name, password = EXCLUDED.password;

-- ==============================================================================
-- 3. Courses 
-- ==============================================================================
INSERT INTO courses (id, course_name)
VALUES 
('COMP302', 'Software Engineering'),
('COMP304', 'Operating Systems')
ON CONFLICT (id) DO UPDATE 
SET course_name = EXCLUDED.course_name;

-- ==============================================================================
-- 4. Enrollments
-- ==============================================================================
INSERT INTO enrollments (student_email, course_id)
VALUES 
('zerdalib@mef.edu.tr', 'COMP302'),
('erkisie@mef.edu.tr', 'COMP302'),
('erkisie@mef.edu.tr', 'COMP304'),
('yayimlid@mef.edu.tr', 'COMP304')
ON CONFLICT DO NOTHING;

-- ==============================================================================
-- 5. Activities
-- ==============================================================================
DELETE FROM scores;
DELETE FROM activities;

INSERT INTO activities (course_id, activity_no, activity_text, learning_objectives, status)
VALUES 
('COMP302', 1, 'Analyze the ATM system case study. Identify the primary business actors and extract the core functional requirements for the cash withdrawal process.', 
 '[{"objective_id": "OBJ_1", "description": "Identify Customer actor", "points": 1}, {"objective_id": "OBJ_2", "description": "Identify withdrawal requirement", "points": 1}]', 
 'Active'),
('COMP304', 1, 'Explain the Dining Philosophers problem. Detail the four necessary conditions for a deadlock and explain how the Circular Wait condition can be prevented in a distributed system.', 
 '[{"objective_id": "OBJ_1", "description": "Explain Circular Wait prevention", "points": 1}]', 
 'Ended');

-- ==============================================================================
-- 6. Scores
-- ==============================================================================
INSERT INTO scores (student_email, course_id, activity_no, score, is_achieved, meta)
VALUES 
('zerdalib@mef.edu.tr', 'COMP302', 1, 2.0, TRUE, '{"evaluation": "Perfect analysis of actors and requirements.", "objectives_achieved": ["OBJ_1", "OBJ_2"]}'),
('erkisie@mef.edu.tr', 'COMP302', 1, 1.0, FALSE, '{"evaluation": "Identified actors but missed the core withdrawal requirement.", "objectives_achieved": ["OBJ_1"]}'),
('yayimlid@mef.edu.tr', 'COMP304', 1, 1.0, TRUE, '{"evaluation": "Excellent explanation of deadlock prevention strategies.", "objectives_achieved": ["OBJ_1"]}');