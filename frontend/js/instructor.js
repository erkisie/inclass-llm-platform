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
  return parseInt(document.getElementById("activityNo").value.trim());
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

// ── LOGIN ──────────────────────────────────────────────────────────────────
async function login() {
  const creds = inst();
  const data = await postRequest("/instructor/login", creds);
  const out = document.getElementById("loginOut");
  out.textContent = niceMessage(data, "Login successful");
  if (data.ok) setLoginStatus(true, creds.email);
}

// ── COURSES ────────────────────────────────────────────────────────────────
async function listCourses() {
  const data = await postRequest("/instructor/list-my-courses", inst());
  const container = document.getElementById("courseList");

  if (!data.ok || !data.data) {
    container.innerHTML = `<pre>${niceMessage(data, "")}</pre>`;
    return;
  }

  const courses = Array.isArray(data.data) ? data.data : Object.values(data.data);

  if (courses.length === 0) {
    container.innerHTML = `<pre>No courses found.</pre>`;
    return;
  }

  container.innerHTML = `
    <div class="activity-list" style="margin-top:14px">
      ${courses.map(c => `
        <div class="activity-item">
          <div class="activity-item-info">
            <h4>${c.course_id || c.id || c.name || JSON.stringify(c)}</h4>
            <p>${c.course_name || c.description || ""}</p>
          </div>
        </div>
      `).join("")}
    </div>`;
}

// ── LIST ACTIVITIES ────────────────────────────────────────────────────────
async function listActivities() {
  const data = await postRequest("/instructor/list-activities", {
    ...inst(),
    course_id: courseId()
  });

  const out = document.getElementById("activityOut");
  const listEl = document.getElementById("activityList");

  if (!data.ok) {
    out.textContent = niceMessage(data, "");
    listEl.innerHTML = "";
    return;
  }

  out.textContent = "";
  const activities = data.data || [];

  if (activities.length === 0) {
    listEl.innerHTML = `<pre style="margin-top:12px">No activities found.</pre>`;
    return;
  }

  function pillClass(status) {
    if (!status) return "inactive";
    const s = status.toLowerCase();
    if (s === "active" || s === "started") return "active";
    if (s === "ended" || s === "closed") return "ended";
    if (s === "pending") return "pending";
    return "inactive";
  }

  listEl.innerHTML = `
    <div class="activity-list">
      ${activities.map(a => `
        <div class="activity-item">
          <div class="activity-item-info">
            <h4>Activity ${a.activity_no}</h4>
            <p>${a.activity_text || "No description"}</p>
          </div>
          <span class="status-pill ${pillClass(a.status)}">${a.status || "unknown"}</span>
        </div>
      `).join("")}
    </div>`;
}

// ── CREATE ACTIVITY ───────────────────────────
async function createActivity() {
  const createCourseId = document.getElementById("createCourseId").value.trim();
  const actNo = parseInt(document.getElementById("newActivityNo").value) || null;
  const actText = document.getElementById("activityText").value;
  const objectives = document.getElementById("learningObjectives").value
    .split(",").map(s => s.trim()).filter(Boolean);
    
  const data = await postRequest("/instructor/create-activity", {
    ...inst(),
    course_id: createCourseId,
    activity_text: actText,
    activity_no_optional: actNo,
    learning_objectives: objectives
  });
  
  document.getElementById("createOut").textContent =
    niceMessage(data, "Activity created successfully");
}

// ── START / END / UPDATE / RESET ───────────────────────────────────────────
async function startActivity() {
  const data = await postRequest("/instructor/start-activity", {
    ...inst(), course_id: courseId(), activity_no: activityNo()
  });
  document.getElementById("activityOut").textContent =
    niceMessage(data, "Activity started");
}

async function endActivity() {
  const data = await postRequest("/instructor/end-activity", {
    ...inst(), course_id: courseId(), activity_no: activityNo()
  });
  document.getElementById("activityOut").textContent =
    niceMessage(data, "Activity ended");
}

async function updateActivity() {
  const data = await postRequest(
    "/instructor/update-activity",
    { ...inst(), course_id: courseId(), activity_no: activityNo() },
    { activity_text: document.getElementById("updateText").value }
  );
  document.getElementById("activityOut").textContent =
    niceMessage(data, "Activity updated");
}

async function resetActivity() {
  const data = await postRequest("/instructor/reset-activity", {
    ...inst(), course_id: courseId(), activity_no: activityNo()
  });
  document.getElementById("activityOut").textContent =
    niceMessage(data, "Activity reset done");
}

// ── SCORES ─────────────────────────────────────────────────────────────────
async function exportScores() {
  const data = await postRequest("/instructor/export-scores", {
    ...inst(), course_id: courseId(), activity_no: activityNo()
  });

  const display = document.getElementById("scoreDisplay");

  if (!data.ok || !data.data) {
    display.innerHTML = `<pre>${niceMessage(data, "")}</pre>`;
    return;
  }

  const scores = Array.isArray(data.data) ? data.data : [];

  if (scores.length === 0) {
    display.innerHTML = `<pre style="margin-top:12px">No scores found.</pre>`;
    return;
  }

  display.innerHTML = `
    <table class="score-table">
      <thead>
        <tr>
          <th>Student</th>
          <th>Score</th>
          <th>Objective</th>
          <th>Submitted</th>
        </tr>
      </thead>
      <tbody>
        ${scores.map(s => `
          <tr>
            <td>${s.email || s.student_email || "-"}</td>
            <td><strong>${s.score ?? "-"}</strong></td>
            <td>${s.meta || s.objective || "-"}</td>
            <td>${s.created_at ? new Date(s.created_at).toLocaleString() : "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>`;
}

async function leaderboard() {
  const data = await postRequest("/instructor/leaderboard", {
    ...inst(), course_id: courseId()
  });

  const display = document.getElementById("scoreDisplay");

  if (!data.ok || !data.data) {
    display.innerHTML = `<pre>${niceMessage(data, "")}</pre>`;
    return;
  }

  const entries = Array.isArray(data.data) ? data.data : [];

  function rankClass(i) {
    if (i === 0) return "rank-1";
    if (i === 1) return "rank-2";
    if (i === 2) return "rank-3";
    return "rank-n";
  }

  display.innerHTML = `
    <table class="score-table">
      <thead>
        <tr><th>Rank</th><th>Student</th><th>Total Score</th></tr>
      </thead>
      <tbody>
        ${entries.map((e, i) => `
          <tr>
            <td><span class="rank-badge ${rankClass(i)}">${i + 1}</span></td>
            <td>${e.email || e.student_email || e.name || "-"}</td>
            <td><strong>${e.total_score ?? e.score ?? "-"}</strong></td>
          </tr>
        `).join("")}
      </tbody>
    </table>`;
}

async function stats() {
  const data = await postRequest("/instructor/activity-stats", {
    ...inst(), course_id: courseId(), activity_no: activityNo()
  });

  const display = document.getElementById("scoreDisplay");

  if (!data.ok || !data.data) {
    display.innerHTML = `<pre>${niceMessage(data, "")}</pre>`;
    return;
  }

  const s = data.data;

  display.innerHTML = `
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">${s.total_submissions ?? s.submissions ?? "-"}</div>
        <div class="stat-label">Submissions</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${s.average_score !== undefined ? Number(s.average_score).toFixed(1) : "-"}</div>
        <div class="stat-label">Average Score</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${s.max_score ?? s.highest_score ?? "-"}</div>
        <div class="stat-label">Highest Score</div>
      </div>
    </div>`;
}
