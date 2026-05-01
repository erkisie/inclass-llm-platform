const API_BASE = "http://127.0.0.1:8000";

async function postRequest(endpoint, params = {}, body = null) {
  const url = new URL(API_BASE + endpoint);

  Object.keys(params).forEach(key => {
    if (params[key] !== "" && params[key] !== null && params[key] !== undefined) {
      url.searchParams.append(key, params[key]);
    }
  });

  const options = {
    method: "POST",
    headers: { "accept": "application/json" }
  };

  if (body !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const res = await fetch(url, options);
  return await res.json();
}

function show(id, data) {
  document.getElementById(id).textContent = JSON.stringify(data, null, 2);
}