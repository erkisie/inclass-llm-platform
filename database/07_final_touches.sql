CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instructor_email TEXT REFERENCES instructors(instructor_email),
    course_id TEXT,
    activity_no INTEGER,
    action_type TEXT CHECK (action_type IN ('START', 'END', 'RESET', 'UPDATE')),
    action_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (course_id, activity_no) REFERENCES activities(course_id, activity_no)
);


UPDATE scores 
SET meta = '{}' 
WHERE meta::TEXT NOT LIKE '{%';

-- activities tablosundaki bozuk verileri temizle 
UPDATE activities 
SET learning_objectives = '[]' 
WHERE learning_objectives::TEXT NOT LIKE '[%';


DROP VIEW IF EXISTS view_objective_stats;

CREATE OR REPLACE VIEW view_objective_stats AS
SELECT 
    a.course_id,
    a.activity_no,
    obj->>'objective_id' AS obj_id,
    obj->>'description' AS obj_desc,
    (
        SELECT COUNT(*) 
        FROM scores s 
        WHERE s.course_id = a.course_id 
          AND s.activity_no = a.activity_no 
          AND (s.meta::TEXT::JSONB)->'objectives_achieved' ? (obj->>'objective_id')
    ) AS achievement_count
FROM activities a
CROSS JOIN LATERAL jsonb_array_elements(a.learning_objectives::TEXT::JSONB) AS obj;