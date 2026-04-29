CREATE TABLE enrollments (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    student_email TEXT REFERENCES students(student_email) ON DELETE CASCADE,
    course_id TEXT REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(student_email, course_id)
);


CREATE TABLE course_owners (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    instructor_email TEXT REFERENCES instructors(instructor_email) ON DELETE CASCADE,
    course_id TEXT REFERENCES courses(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(instructor_email, course_id)
);