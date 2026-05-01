from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.services import (
    studentLogin,
    changeStudentPassword,
    setStudentPassword,
    getActivity,
    logScore,
    instructorLogin,
    changeInstructorPassword,
    setInstructorPassword,
    listMyCourses,
    listActivities,
    createActivity,
    updateActivity,
    startActivity,
    endActivity,
    exportScores,
    resetActivity,
    resetStudentPassword,
    getLeaderboard,
    getActivityStats,
)

app = FastAPI(title="InClass LLM Platform")

# ✅ CORS FIX (EN ÖNEMLİ KISIM)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "message": "API is running"}

# ---------- STUDENT ----------

@app.post("/student/login")
def student_login(email: str, password: str):
    return studentLogin(email, password)

@app.post("/student/change-password")
def student_change_password(email: str, password: str, new_password: str, old_password: str):
    return changeStudentPassword(email, password, new_password, old_password)

@app.post("/student/set-password")
def student_set_password(email: str, password: str):
    return setStudentPassword(email, password)

@app.post("/student/get-activity")
def student_get_activity(email: str, password: str, course_id: str, activity_no: int):
    return getActivity(email, password, course_id, activity_no)

@app.post("/student/log-score")
def student_log_score(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None):
    return logScore(email, password, course_id, activity_no, score, meta)

# ---------- INSTRUCTOR ----------

@app.post("/instructor/login")
def instructor_login(email: str, password: str):
    return instructorLogin(email, password)

@app.post("/instructor/change-password")
def instructor_change_password(email: str, password: str, old_password: str, new_password: str):
    return changeInstructorPassword(email, password, old_password, new_password)

@app.post("/instructor/set-password")
def instructor_set_password(email: str, password: str | None = None):
    return setInstructorPassword(email, password)

@app.post("/instructor/list-my-courses")
def instructor_list_my_courses(email: str, password: str):
    return listMyCourses(email, password)

@app.post("/instructor/list-activities")
def instructor_list_activities(email: str, password: str, course_id: str):
    return listActivities(email, password, course_id)

@app.post("/instructor/create-activity")
def instructor_create_activity(
    email: str,
    password: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None
):
    return createActivity(email, password, course_id, activity_text, learning_objectives, activity_no_optional)

@app.post("/instructor/update-activity")
def instructor_update_activity(email: str, password: str, course_id: str, activity_no: int, patch: dict):
    return updateActivity(email, password, course_id, activity_no, patch)

@app.post("/instructor/start-activity")
def instructor_start_activity(email: str, password: str, course_id: str, activity_no: int):
    return startActivity(email, password, course_id, activity_no)

@app.post("/instructor/end-activity")
def instructor_end_activity(email: str, password: str, course_id: str, activity_no: int):
    return endActivity(email, password, course_id, activity_no)

@app.post("/instructor/export-scores")
def instructor_export_scores(email: str, password: str, course_id: str, activity_no: int):
    return exportScores(email, password, course_id, activity_no)

@app.post("/instructor/reset-activity")
def instructor_reset_activity(email: str, password: str, course_id: str, activity_no: int):
    return resetActivity(email, password, course_id, activity_no)

@app.post("/instructor/reset-student-password")
def instructor_reset_student_password(email: str, password: str, course_id: str, student_email: str, new_password: str):
    return resetStudentPassword(email, password, course_id, student_email, new_password)

@app.post("/instructor/leaderboard")
def instructor_leaderboard(email: str, password: str, course_id: str):
    return getLeaderboard(email, password, course_id)

@app.post("/instructor/activity-stats")
def instructor_activity_stats(email: str, password: str, course_id: str, activity_no: int):
    return getActivityStats(email, password, course_id, activity_no)

# ---------- HEALTH ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")
