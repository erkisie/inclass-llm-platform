
ALTER TABLE activities 
ADD CONSTRAINT unique_course_activity UNIQUE (course_id, activity_no);


DROP TABLE IF EXISTS chat_messages;

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_email TEXT REFERENCES students(student_email) ON DELETE CASCADE,
    course_id TEXT,
    activity_no INTEGER,
    role TEXT CHECK (role IN ('system', 'user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (course_id, activity_no) REFERENCES activities(course_id, activity_no) ON DELETE CASCADE
);


CREATE INDEX idx_chat_messages_lookup ON chat_messages (student_email, course_id, activity_no, created_at);

INSERT INTO chat_messages (student_email, course_id, activity_no, role, content)
VALUES 
('zerdalib@mef.edu.tr', 'COMP302', 1, 'system', 'You are an expert Software Engineering tutor.'),
('zerdalib@mef.edu.tr', 'COMP302', 1, 'assistant', 'Hello Beyza! Let''s look at the ATM system.'),
('zerdalib@mef.edu.tr', 'COMP302', 1, 'user', 'I think it is the Customer actor.'),
('zerdalib@mef.edu.tr', 'COMP302', 1, 'assistant', 'Excellent! (+1 score). Now, what is the core requirement?');