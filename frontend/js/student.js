function student() {
  return {
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value.trim()
  };
}

function courseId() {
  return document.getElementById("courseId").value.trim();
}

function activityNo() {
  return document.getElementById("activityNo").value.trim();
}

function message(data, okText) {
  return data.ok ? "✔ " + okText : "✖ " + data.message;
}

async function login() {
  document.getElementById("loginOut").textContent = "Loading...";
  const data = await postRequest("/student/login", student());
  document.getElementById("loginOut").textContent =
    message(data, "Student login successful.");
}

async function getActivity() {
  document.getElementById("activityOut").textContent = "Loading activity...";

  const data = await postRequest("/student/get-activity", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  if (!data.ok) {
    document.getElementById("activityStatus").textContent = "Blocked";
    document.getElementById("activityOut").textContent =
      "✖ " + data.message + "\n\nPlease ask your instructor to start an active activity.";
    return;
  }

  const activity = data.data || data.activity || data;
  const text =
    activity.activity_text ||
    (activity.data && activity.data.activity_text) ||
    "Activity is available.";

  document.getElementById("activityStatus").textContent = "ACTIVE";
  document.getElementById("activityOut").textContent =
    "✔ Activity loaded successfully.\n\n" +
    text +
    "\n\nLearning objectives are hidden from student view.";
}

async function logScore() {
  document.getElementById("scoreOut").textContent = "Submitting score...";

  const data = await postRequest("/student/log-score", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo(),
    score: document.getElementById("score").value,
    meta: document.getElementById("meta").value
  });

  if (data.ok) {
    document.getElementById("currentScore").textContent =
      Number(document.getElementById("currentScore").textContent || 0) + 1;

    document.getElementById("scoreOut").textContent =
      "✔ Score submitted successfully. +1 point earned.";
  } else {
    document.getElementById("scoreOut").textContent =
      "✖ " + data.message + "\n\nRepeated achievements should not increase the score again.";
  }
}