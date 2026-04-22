CREATE TABLE IF NOT EXISTS activities (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    course_id TEXT REFERENCES courses(id) ON DELETE CASCADE,
    activity_no INT NOT NULL,
    activity_text TEXT NOT NULL,
    learning_objectives JSONB, 
    status TEXT DEFAULT 'NOT_STARTED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS scores (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    student_email TEXT REFERENCES students(student_email) ON DELETE CASCADE,
    course_id TEXT REFERENCES courses(id) ON DELETE CASCADE,
    activity_no INT NOT NULL,
    score FLOAT8 CHECK (score >= 0),
    meta JSONB,     is_achieved BOOLEAN DEFAULT FALSE, 
    graded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
