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

function niceMessage(data, successText) {
  if (data.ok) {
    return "✔ " + successText;
  }
  return "✖ " + data.message;
}

async function login() {
  const data = await postRequest("/student/login", student());
  document.getElementById("loginOut").textContent =
    niceMessage(data, "Student login successful.");
}

async function getActivity() {
  const data = await postRequest("/student/get-activity", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  if (!data.ok) {
    document.getElementById("activityOut").textContent = "✖ " + data.message;
    return;
  }

  const activity = data.data || data.activity || data;

  let text = "✔ Activity loaded successfully.\n\n";

  if (activity.activity_text) {
    text += activity.activity_text;
  } else if (activity.data && activity.data.activity_text) {
    text += activity.data.activity_text;
  } else {
    text += "Activity is available.";
  }

  text += "\n\nLearning objectives are hidden from student view.";

  document.getElementById("activityOut").textContent = text;
}

async function logScore() {
  const data = await postRequest("/student/log-score", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo(),
    score: document.getElementById("score").value,
    meta: document.getElementById("meta").value
  });

  document.getElementById("scoreOut").textContent =
    niceMessage(data, "Score submitted successfully.");
}