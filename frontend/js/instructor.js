function inst() {
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
  const data = await postRequest("/instructor/login", inst());
  document.getElementById("loginOut").textContent =
    message(data, "Instructor login successful.");
}

async function listActivities() {
  document.getElementById("activityOut").textContent = "Loading activities...";

  const data = await postRequest("/instructor/list-activities", {
    ...inst(),
    course_id: courseId()
  });

  if (!data.ok) {
    document.getElementById("activityOut").textContent = "✖ " + data.message;
    return;
  }

  const activities = data.data || [];

  if (activities.length === 0) {
    document.getElementById("activityOut").textContent = "No activities found.";
    return;
  }

  let html = "✔ Activities listed successfully.\n\n";
  html += "Activity No | Status | Activity Text\n";
  html += "--------------------------------------\n";

  activities.forEach(a => {
    html += `${a.activity_no} | ${a.status} | ${a.activity_text}\n`;
  });

  document.getElementById("activityOut").textContent = html;
}

async function createActivity() {
  document.getElementById("createOut").textContent = "Creating activity...";

  const data = await postRequest("/instructor/create-activity", {
    ...inst(),
    course_id: courseId(),
    activity_text: document.getElementById("activityText").value,
    activity_no_optional: document.getElementById("newActivityNo").value
  }, ["Message types", "Message format"]);

  document.getElementById("createOut").textContent =
    message(data, "Activity created successfully.");
}

async function startActivity() {
  document.getElementById("activityOut").textContent = "Starting activity...";

  const data = await postRequest("/instructor/start-activity", {
    ...inst(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  document.getElementById("activityOut").textContent =
    message(data, "Activity started successfully.");
}

async function endActivity() {
  document.getElementById("activityOut").textContent = "Ending activity...";

  const data = await postRequest("/instructor/end-activity", {
    ...inst(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  document.getElementById("activityOut").textContent =
    message(data, "Activity ended successfully.");
}

async function exportScores() {
  document.getElementById("scoreOut").textContent = "Exporting scores...";

  const data = await postRequest("/instructor/export-scores", {
    ...inst(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  if (!data.ok) {
    document.getElementById("scoreOut").textContent = "✖ " + data.message;
    return;
  }

  const rows = data.data || [];

  if (rows.length === 0) {
    document.getElementById("scoreOut").textContent =
      "✔ Scores exported successfully.\n\nNo score records found.";
    return;
  }

  let text = "✔ Scores exported successfully.\n\n";
  text += "Student | Score | Meta\n";
  text += "----------------------\n";

  rows.forEach(r => {
    text += `${r.student_email} | ${r.score} | ${r.meta}\n`;
  });

  document.getElementById("scoreOut").textContent = text;
}

async function leaderboard() {
  document.getElementById("scoreOut").textContent = "Loading leaderboard...";

  const data = await postRequest("/instructor/leaderboard", {
    ...inst(),
    course_id: courseId()
  });

  if (!data.ok) {
    document.getElementById("scoreOut").textContent = "✖ " + data.message;
    return;
  }

  document.getElementById("scoreOut").textContent =
    "✔ Leaderboard loaded successfully.\n\n" +
    JSON.stringify(data.data, null, 2);
}

async function stats() {
  document.getElementById("scoreOut").textContent = "Loading activity statistics...";

  const data = await postRequest("/instructor/activity-stats", {
    ...inst(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  if (!data.ok) {
    document.getElementById("scoreOut").textContent = "✖ " + data.message;
    return;
  }

  const s = data.data || {};

  document.getElementById("scoreOut").textContent =
    "✔ Activity statistics loaded successfully.\n\n" +
    `Participants: ${s.participant_count}\n` +
    `Average Score: ${s.average_score}\n` +
    `Max Score: ${s.max_score}\n` +
    `Min Score: ${s.min_score}`;
}