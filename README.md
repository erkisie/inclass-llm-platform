# InClass Activity Platform

A full-stack classroom activity management system developed as a Software Engineering term project.

The platform enables instructors to create and manage activities, while students participate in active sessions and earn scores based on their responses through a controlled activity-based learning environment.

---

# Project Overview

The InClass Activity Platform is designed to support interactive classroom participation using instructor-controlled activities. Instructors can create, manage, start, end, and reset activities while monitoring student participation and score progression.

Students can only access activities that are currently active and associated with courses in which they are enrolled. The system also includes dynamic score logging, duplicate submission prevention, authorization validation, and hidden learning objectives.

The project was developed using Agile/Scrum methodologies with GitHub-based collaboration and ClickUp sprint management.

---

# Core Features

## Instructor Features

- Instructor authentication
- Course ownership validation
- Create activities
- Update activities
- Start activities
- End activities
- Reset activities
- Export scores
- View leaderboard
- View activity statistics
- Monitor student participation
- Manage activities securely

---

## Student Features

- Student authentication
- Access active activities
- Participate only in enrolled courses
- Submit answers
- Earn dynamic scores
- View activity content
- Prevent duplicate score submissions
- Receive validation feedback messages

---

# Key Concepts

- Activity-based learning system
- Objective-driven scoring mechanism
- Real-time activity management
- Dynamic score logging
- Duplicate submission prevention
- Hidden learning objectives
- Backend authorization validation
- Instructor ownership control
- Student enrollment validation
- API-based architecture
- Frontend-backend integration

---

# Validation & Security Features

The platform includes several validation and authorization mechanisms to ensure system reliability and secure usage.

## Authorization Features

- Only authorized instructors can manage their own courses
- Students can only access enrolled courses
- Unauthorized users are rejected
- Backend-side validation is enforced

---

## Activity Validation

- Activities cannot be accessed before they start
- Activities cannot be accessed after they end
- Scores cannot be submitted for ended activities
- Duplicate score submissions are blocked

---

## Hidden Learning Objectives

Learning objectives are intentionally hidden from student API responses and frontend interfaces to preserve the activity-based learning flow.

---

# Technologies Used

## Backend

- Python
- FastAPI

## Database

- Supabase
- PostgreSQL

## Frontend

- HTML
- CSS
- JavaScript

## API Testing

- Swagger UI

## Project Management

- GitHub
- ClickUp

---

# System Architecture

The system follows a client-server architecture:

- Frontend communicates with backend APIs
- FastAPI handles request processing and validation
- Supabase/PostgreSQL stores users, activities, enrollments, and scores
- Instructor and student operations are separated through role-based endpoints

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/erkisie/inclass-llm-platform
cd inclass-llm-platform

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/erkisie/inclass-llm-platform
cd inclass-llm-platform
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

### Mac/Linux

```bash
python3 -m venv venv
```

---

## 3. Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 4. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root directory.

Example:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

---

## 6. Run the Backend

```bash
uvicorn app.main:app --reload
```

---

# Frontend URLs

## Home Page

```text
http://127.0.0.1:8000/ui/index.html
```

## Instructor Panel

```text
http://127.0.0.1:8000/ui/instructor.html
```

## Student Panel

```text
http://127.0.0.1:8000/ui/student.html
```

## Swagger API Documentation

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Instructor Endpoints

- `/instructor/login`
- `/instructor/list-my-courses`
- `/instructor/list-activities`
- `/instructor/create-activity`
- `/instructor/update-activity`
- `/instructor/start-activity`
- `/instructor/end-activity`
- `/instructor/reset-activity`
- `/instructor/export-scores`
- `/instructor/activity-stats`
- `/instructor/leaderboard`

---

## Student Endpoints

- `/student/login`
- `/student/get-activity`
- `/student/log-score`
- `/student/change-password`

---

# Example System Flow

## Instructor Flow

1. Instructor logs in
2. Instructor lists activities
3. Instructor creates or updates an activity
4. Instructor starts the activity
5. Students participate
6. Instructor exports scores
7. Instructor ends or resets the activity

---

## Student Flow

1. Student logs in
2. Student accesses active activity
3. Student submits responses
4. Score is logged dynamically
5. Duplicate submissions are prevented
6. Student receives feedback

---

# Example Validation Scenarios

## Authorized Instructor Access

Only instructors who own the course can manage activities.

---

## Student Enrollment Validation

Students who are not enrolled in a course cannot access activities.

---

## Activity State Validation

- NOT_STARTED activities cannot be accessed
- ACTIVE activities can be accessed
- ENDED activities reject new submissions

---

## Duplicate Prevention

Students cannot receive duplicate scores for the same activity objective.

---

# Testing & Validation

The platform was tested using:

- Swagger API testing
- Frontend integration testing
- Backend validation testing
- Enrollment authorization testing
- Activity status testing
- Export functionality testing
- Duplicate score prevention testing

---

# Scrum & Project Management

The project was developed using Agile/Scrum methodologies.

## Tools Used

- ClickUp for sprint and task management
- GitHub for version control and collaboration

---

## Scrum Practices

- Sprint planning
- Sprint tracking
- Task assignment
- Daily progress updates
- Sprint reviews
- Sprint retrospectives

---

# GitHub Workflow

The team used:

- Feature branches
- Pull requests
- Merge reviews
- Sprint tags
- Collaborative commits

---

## Sprint Tags

- sprint-1
- sprint-2

---

# Demo Highlights

The final demo includes:

- Instructor activity management
- Student activity participation
- Hidden learning objectives
- Backend authorization validation
- Dynamic score logging
- Duplicate prevention
- Activity state control
- Export score functionality

---

# Future Improvements

Possible future enhancements include:

- Real-time websocket updates
- Advanced analytics dashboard
- LLM-assisted tutoring flow
- Mobile-responsive redesign
- Authentication token support
- Advanced reporting system

---

# Team Project

Developed as part of a Software Engineering term project using collaborative Agile/Scrum development practices.

The project includes:

- Full-stack system design
- Backend API development
- Frontend integration
- Validation testing
- Sprint-based teamwork
- GitHub collaboration
- ClickUp project management

---

# License

This project was developed for educational purposes as part of a university Software Engineering course.
