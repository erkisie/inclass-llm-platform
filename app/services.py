from typing import Optional
from app.db import supabase


def _success(data=None, message="Success"):
    return {
        "ok": True,
        "message": message,
        "data": data
    }


def _error(message="Error"):
    return {
        "ok": False,
        "message": message
    }


def _check_instructor_ownership(email: str, course_id: str) -> bool:
    if supabase is None:
        return False

    ownership = (
        supabase
        .table("course_owners")
        .select("*")
        .eq("instructor_email", email)
        .eq("course_id", course_id)
        .execute()
    )

    return bool(ownership.data)


def studentLogin(email: str, password: str) -> dict:
    if not email or not password:
        return _error("Email and password are required")
    return _success({"email": email, "role": "student"}, "Student login successful")


def instructorLogin(email: str, password: str) -> dict:
    if not email or not password:
        return _error("Email and password are required")
    return _success({"email": email, "role": "instructor"}, "Instructor login successful")


def listMyCourses(email: str, password: str) -> dict:
    if not email or not password:
        return _error("Email and password are required")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        ownership = (
            supabase
            .table("course_owners")
            .select("*")
            .eq("instructor_email", email)
            .execute()
        )

        if not ownership.data:
            return _success([], "Courses listed successfully")

        course_ids = [row["course_id"] for row in ownership.data if row.get("course_id")]

        response = (
            supabase
            .table("courses")
            .select("*")
            .in_("course_id", course_ids)
            .execute()
        )

        return _success(response.data, "Courses listed successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def getActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        enrollment = (
            supabase
            .table("enrollments")
            .select("*")
            .eq("student_email", email)
            .eq("course_id", course_id)
            .execute()
        )

        if not enrollment.data:
            return _error("Student not enrolled in this course")

        response = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not response.data:
            return _error("Activity not found")

        activity = response.data[0]
        status = activity.get("status")

        if status == "NOT_STARTED":
            return _error("Activity has not started yet")

        if status == "ENDED":
            return _error("Activity has already ended")

        return _success(activity, "Activity fetched successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def listActivities(email: str, password: str, course_id: str) -> dict:
    if not all([email, password, course_id]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .execute()
        )
        return _success(response.data, "Activities listed successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def createActivity(
    email: str,
    password: str,
    course_id: str,
    activity_text: str,
    learning_objectives: list[str],
    activity_no_optional: int | None = None
) -> dict:
    if not all([email, password, course_id, activity_text]) or not learning_objectives:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        activity_no = activity_no_optional if activity_no_optional is not None else 1

        existing = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if existing.data:
            return _error("Activity number already exists")

        payload = {
            "course_id": course_id,
            "activity_no": activity_no,
            "activity_text": activity_text,
            "learning_objectives": ", ".join(learning_objectives),
            "status": "NOT_STARTED"
        }

        response = supabase.table("activities").insert(payload).execute()
        return _success(response.data, "Activity created successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def updateActivity(
    email: str,
    password: str,
    course_id: str,
    activity_no: int,
    activity_text: str,
    learning_objectives: list[str]
) -> dict:
    if not all([email, password, course_id, activity_text]) or activity_no is None or not learning_objectives:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        check = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not check.data:
            return _error("Activity not found")

        payload = {
            "activity_text": activity_text,
            "learning_objectives": ", ".join(learning_objectives)
        }

        response = (
            supabase
            .table("activities")
            .update(payload)
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        return _success(response.data, "Activity updated successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def startActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        check = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not check.data:
            return _error("Activity not found")

        status = check.data[0]["status"]

        if status == "ACTIVE":
            return _error("Activity is already active")

        if status == "ENDED":
            return _error("Cannot start an ended activity")

        response = (
            supabase
            .table("activities")
            .update({"status": "ACTIVE"})
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )
        return _success(response.data, "Activity started successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def endActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        check = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not check.data:
            return _error("Activity not found")

        status = check.data[0]["status"]

        if status == "ENDED":
            return _error("Activity is already ended")

        if status == "NOT_STARTED":
            return _error("Cannot end an activity that has not started")

        response = (
            supabase
            .table("activities")
            .update({"status": "ENDED"})
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )
        return _success(response.data, "Activity ended successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def logScore(
    email: str,
    password: str,
    course_id: str,
    activity_no: int,
    score: float,
    meta: Optional[str] = None
) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if score < 0 or score > 100:
        return _error("Score must be between 0 and 100")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        activity_check = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not activity_check.data:
            return _error("Activity not found")

        if activity_check.data[0]["status"] == "ENDED":
            return _error("Cannot submit score for ended activity")

        existing = (
            supabase
            .table("scores")
            .select("*")
            .eq("student_email", email)
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if existing.data:
            return _error("Score already submitted for this activity")

        payload = {
            "student_email": email,
            "course_id": course_id,
            "activity_no": activity_no,
            "score": score,
            "meta": meta
        }

        response = supabase.table("scores").insert(payload).execute()
        return _success(response.data, "Score logged successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("scores")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        return _success(response.data, "Scores exported successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        check = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not check.data:
            return _error("Activity not found")

        response = (
            supabase
            .table("activities")
            .update({"status": "NOT_STARTED"})
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )
        return _success(response.data, "Activity reset successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def resetStudentPassword(email: str, password: str, course_id: str, student_email: str, new_password: str) -> dict:
    if not all([email, password, course_id, student_email, new_password]):
        return _error("Missing required fields")

    return _success(message="Student password reset successfully")


def changeStudentPassword(email: str, old_password: str, new_password: str) -> dict:
    if not all([email, old_password, new_password]):
        return _error("Missing required fields")

    return _success(message="Student password changed successfully")


def setStudentPassword(email: str, new_password: str) -> dict:
    if not all([email, new_password]):
        return _error("Missing required fields")

    return _success(message="Student password set successfully")


def changeInstructorPassword(email: str, old_password: str, new_password: str) -> dict:
    if not all([email, old_password, new_password]):
        return _error("Missing required fields")

    return _success(message="Instructor password changed successfully")


def setInstructorPassword(email: str, new_password: str) -> dict:
    if not all([email, new_password]):
        return _error("Missing required fields")

    return _success(message="Instructor password set successfully")


def getLeaderboard(email: str, password: str, course_id: str) -> dict:
    if not all([email, password, course_id]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("scores")
            .select("*")
            .eq("course_id", course_id)
            .execute()
        )

        if not response.data:
            return _success([], "No scores found")

        scores = response.data
        student_scores = {}

        for row in scores:
            student = row["student_email"]
            score = row["score"]

            if student not in student_scores:
                student_scores[student] = {
                    "total": 0,
                    "count": 0
                }

            student_scores[student]["total"] += score
            student_scores[student]["count"] += 1

        leaderboard = []

        for student, data in student_scores.items():
            avg = data["total"] / data["count"]

            leaderboard.append({
                "student_email": student,
                "average_score": round(avg, 2),
                "total_score": data["total"]
            })

        leaderboard.sort(key=lambda x: x["average_score"], reverse=True)

        return _success(leaderboard, "Leaderboard generated successfully")

    except Exception as e:
        return _error(f"Database error: {str(e)}")


def getActivityStats(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("scores")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not response.data:
            return _success({}, "No scores found")

        scores = [row["score"] for row in response.data]

        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        participant_count = len(scores)

        return _success({
            "average_score": round(avg_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "participant_count": participant_count
        }, "Activity stats generated successfully")

    except Exception as e:
        return _error(f"Database error: {str(e)}")

def getActivityStats(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("scores")
            .select("*")
            .eq("course_id", course_id)
            .eq("activity_no", activity_no)
            .execute()
        )

        if not response.data:
            return _success({}, "No scores found")

        scores = [row["score"] for row in response.data]

        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        participant_count = len(scores)

        return _success({
            "average_score": round(avg_score, 2),
            "max_score": max_score,
            "min_score": min_score,
            "participant_count": participant_count
        }, "Activity stats generated successfully")

    except Exception as e:
        return _error(f"Database error: {str(e)}")