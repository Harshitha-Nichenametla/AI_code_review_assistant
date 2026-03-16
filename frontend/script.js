async function reviewCode() {

  const code = document.getElementById("code").value;

  if (!code.trim()) {
    document.getElementById("result").innerHTML = "<p>Please paste some code first.</p>";
    return;
  }

  document.getElementById("result").innerHTML = "<p>Analyzing...</p>";

  try {
    const response = await fetch("http://127.0.0.1:8000/review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ code: code })
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "Server error: " + response.status);
    }

    const data = await response.json();

    let html = `<h2>Score: ${data.score}/100</h2>`;
    html += "<h3>Issues:</h3>";

    data.issues.forEach(issue => {
      html += `<p>${issue}</p>`;
    });

    const resultEl = document.getElementById("result");
    resultEl.innerHTML = html;
    resultEl.style.display = "block";

  } catch (err) {
    if (err.message.includes("Failed to fetch")) {
      document.getElementById("result").innerHTML =
        "<p>Cannot reach the server. Make sure the FastAPI server is running on port 8000.</p>";
    } else {
      document.getElementById("result").innerHTML = `<p>Error: ${err.message}</p>`;
    }
  }

}