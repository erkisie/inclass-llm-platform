
CREATE TABLE students (
    student_email TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    password TEXT );

CREATE TABLE instructors (
    instructor_email TEXT PRIMARY KEY,
    instructor_name TEXT NOT NULL,
    password TEXT );

CREATE TABLE courses (
    id TEXT PRIMARY KEY, 
    course_name TEXT NOT NULL
);