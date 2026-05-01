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


def _check_student_credentials(email: str, password: str) -> bool:
    if supabase is None:
        return False

    response = (
        supabase
        .table("students")
        .select("*")
        .eq("student_email", email)
        .eq("password", password)
        .execute()
    )
    return bool(response.data)


def _check_instructor_credentials(email: str, password: str) -> bool:
    if supabase is None:
        return False

    response = (
        supabase
        .table("instructors")
        .select("*")
        .eq("instructor_email", email)
        .eq("password", password)
        .execute()
    )
    return bool(response.data)


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
    
    # ===== VALIDATION (Derin ekledi) =====
    if "@" not in email:
        return _error("Invalid email format")
    if len(password) < 4:
        return _error("Password must be at least 4 characters")
    # ====================================

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_student_credentials(email, password):
        return _error("Invalid student credentials")

    return _success({"email": email, "role": "student"}, "Student login successful")


def instructorLogin(email: str, password: str) -> dict:
    if not email or not password:
        return _error("Email and password are required")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

    return _success({"email": email, "role": "instructor"}, "Instructor login successful")


def listMyCourses(email: str, password: str) -> dict:
    if not email or not password:
        return _error("Email and password are required")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

    if not _check_student_credentials(email, password):
        return _error("Invalid student credentials")

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


def logScore(email: str, password: str, course_id: str, activity_no: int, score: float, meta: str | None = None) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if score < 0 or score > 100:
        return _error("Score must be between 0 and 100")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_student_credentials(email, password):
        return _error("Invalid student credentials")

    try:
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


def changeStudentPassword(email: str, password: str, new_password: str, old_password: str) -> dict:
    if not all([email, password, new_password, old_password]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if password != old_password:
        return _error("Provided password and old_password do not match")

    if not _check_student_credentials(email, old_password):
        return _error("Invalid student credentials")

    try:
        response = (
            supabase
            .table("students")
            .update({"password": new_password})
            .eq("student_email", email)
            .execute()
        )
        return _success(response.data, "Student password changed successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def setStudentPassword(email: str, password: str) -> dict:
    if not all([email, password]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    try:
        check = (
            supabase
            .table("students")
            .select("*")
            .eq("student_email", email)
            .execute()
        )

        if not check.data:
            return _error("Student not found")

        current = check.data[0].get("password")
        if current:
            return _error("Student already has a password")

        response = (
            supabase
            .table("students")
            .update({"password": password})
            .eq("student_email", email)
            .execute()
        )
        return _success(response.data, "Student password set successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def listActivities(email: str, password: str, course_id: str) -> dict:
    if not all([email, password, course_id]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

    try:
        if not _check_instructor_ownership(email, course_id):
            return _error("You are not authorized for this course")

        response = (
            supabase
            .table("activities")
            .select("*")
            .eq("course_id", course_id)
            .order("activity_no")
            .execute()
        )
        return _success(response.data, "Activities listed successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def createActivity(email: str, password: str, course_id: str, activity_text: str, learning_objectives: list[str], activity_no_optional: int | None = None) -> dict[str, object]:
    if not all([email, password, course_id, activity_text]) or not learning_objectives:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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


def updateActivity(email: str, password: str, course_id: str, activity_no: int, patch: dict) -> dict:
    if not all([email, password, course_id]) or activity_no is None or patch is None:
        return _error("Missing required fields")

    if not isinstance(patch, dict) or not patch:
        return _error("Patch must be a non-empty dictionary")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

    allowed_fields = {"activity_text", "learning_objectives", "status"}
    invalid_fields = [key for key in patch.keys() if key not in allowed_fields]
    if invalid_fields:
        return _error(f"Invalid patch fields: {invalid_fields}")

    if "learning_objectives" in patch and isinstance(patch["learning_objectives"], list):
        patch["learning_objectives"] = ", ".join(patch["learning_objectives"])

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
            .update(patch)
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

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

def exportScores(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

        rows = response.data or []

        # CSV oluştur
        csv_lines = [
            "student_email,course_id,activity_no,score,meta,is_achieved"
        ]

        for row in rows:
            student_email = str(row.get("student_email", ""))
            row_course_id = str(row.get("course_id", ""))
            row_activity_no = str(row.get("activity_no", ""))
            score = str(row.get("score", ""))
            meta = str(row.get("meta", "")).replace('"', '""')
            is_achieved = str(row.get("is_achieved", ""))

            csv_lines.append(
                f'"{student_email}","{row_course_id}","{row_activity_no}","{score}","{meta}","{is_achieved}"'
            )

        csv_text = "\n".join(csv_lines)

        return {
            "ok": True,
            "message": "Scores exported successfully",
            "data": rows,
            "csv": csv_text
        }

    except Exception as e:
        return _error(f"Database error: {str(e)}")
    
def resetActivity(email: str, password: str, course_id: str, activity_no: int) -> dict:
    if not all([email, password, course_id]) or activity_no is None:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

        supabase.table("scores").delete().eq("course_id", course_id).eq("activity_no", activity_no).execute()

        response = (
            supabase
            .table("activities")
            .update({"status": "ENDED"})
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

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

    if not _check_instructor_ownership(email, course_id):
        return _error("You are not authorized for this course")

    try:
        response = (
            supabase
            .table("students")
            .update({"password": new_password})
            .eq("student_email", student_email)
            .execute()
        )
        return _success(response.data, "Student password reset successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def changeInstructorPassword(email: str, password: str, old_password: str, new_password: str) -> dict:
    if not all([email, password, old_password, new_password]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if password != old_password:
        return _error("Provided password and old_password do not match")

    if not _check_instructor_credentials(email, old_password):
        return _error("Invalid instructor credentials")

    try:
        response = (
            supabase
            .table("instructors")
            .update({"password": new_password})
            .eq("instructor_email", email)
            .execute()
        )
        return _success(response.data, "Instructor password changed successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def setInstructorPassword(email: str, password: str | None = None) -> dict:
    if not email:
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if password is None:
        return _error("Password is required")

    try:
        check = (
            supabase
            .table("instructors")
            .select("*")
            .eq("instructor_email", email)
            .execute()
        )

        if not check.data:
            return _error("Instructor not found")

        current = check.data[0].get("password")
        if current:
            return _error("Instructor already has a password")

        response = (
            supabase
            .table("instructors")
            .update({"password": password})
            .eq("instructor_email", email)
            .execute()
        )
        return _success(response.data, "Instructor password set successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")


def getLeaderboard(email: str, password: str, course_id: str) -> dict:
    if not all([email, password, course_id]):
        return _error("Missing required fields")

    if supabase is None:
        return _error("Database connection is not configured")

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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
                student_scores[student] = {"total": 0, "count": 0}

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

    if not _check_instructor_credentials(email, password):
        return _error("Invalid instructor credentials")

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

        scores = response.data or []
        if not scores:
            return _success({
                "participant_count": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0
            }, "Activity stats generated successfully")

        values = [row["score"] for row in scores]

        stats = {
            "participant_count": len(scores),
            "average_score": round(sum(values) / len(values), 2),
            "max_score": max(values),
            "min_score": min(values)
        }

        return _success(stats, "Activity stats generated successfully")
    except Exception as e:
        return _error(f"Database error: {str(e)}")
