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
  if (data.ok) return "OK  " + successText;
  return "ERR  " + (data.message || "An error occurred");
}

function setLoginStatus(loggedIn, email) {
  const el = document.getElementById("loginStatus");
  if (!el) return;
  const dot = el.querySelector(".status-dot");
  const lbl = el.querySelector("span:last-child");
  if (loggedIn) {
    dot.className = "status-dot online";
    lbl.textContent = email;
  } else {
    dot.className = "status-dot offline";
    lbl.textContent = "Not logged in";
  }
}

async function login() {
  const creds = student();
  const data = await postRequest("/student/login", creds);
  const out = document.getElementById("loginOut");
  out.textContent = niceMessage(data, "Logged in successfully.");
  if (data.ok) setLoginStatus(true, creds.email);
}

async function getActivity() {
  const data = await postRequest("/student/get-activity", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo()
  });

  const card = document.getElementById("activityCard");
  const out  = document.getElementById("activityOut");

  card.style.display = "none";
  out.textContent = "";

  if (!data.ok) {
    out.textContent = niceMessage(data, "");
    return;
  }

  const activity = data.data || data.activity || data;
  const activityText =
    activity.activity_text ||
    (activity.data && activity.data.activity_text) ||
    null;

  if (activityText) {
    document.getElementById("activityBadge").textContent =
      `${courseId()}  ·  Activity ${activityNo()}`;
    document.getElementById("activityBody").textContent = activityText;
    card.style.display = "block";
  } else {
    out.textContent = "Activity is available. No text provided.";
  }
}

async function logScore() {
  const data = await postRequest("/student/log-score", {
    ...student(),
    course_id: courseId(),
    activity_no: activityNo(),
    score: document.getElementById("score").value,
    meta: document.getElementById("meta").value
  });

  const successEl = document.getElementById("scoreSuccess");
  const out = document.getElementById("scoreOut");

  if (data.ok) {
    successEl.style.display = "block";
    out.textContent = "";
  } else {
    successEl.style.display = "none";
    out.textContent = niceMessage(data, "");
  }
}
