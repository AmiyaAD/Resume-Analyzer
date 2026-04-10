const chatbox = document.getElementById("chatbox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const resumeFile = document.getElementById("resumeFile");

// Memory: keep track of last uploaded resume
let lastResumeFile = null;

function addMessage(text, sender) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.textContent = text;
  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  const file = resumeFile.files[0];

  if (!text && !file && !lastResumeFile) {
    alert("Please type a message or upload a resume file.");
    return;
  }

  if (text) addMessage(text, "user");
  if (file) {
    addMessage(`Uploaded file: ${file.name}`, "user");
    lastResumeFile = file; // update memory
  }

  userInput.value = "";
  resumeFile.value = "";

  try {
    const formData = new FormData();

    // Use new file if uploaded, otherwise reuse last file
    if (file) {
      formData.append("file", file);
    } else if (lastResumeFile) {
      formData.append("file", lastResumeFile);
    } else {
      formData.append("file", new Blob(["Dummy resume text"], { type: "text/plain" }), "resume.txt");
    }

    formData.append("job_keywords", text);

    const response = await fetch("http://127.0.0.1:8001/analyze_resume/", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    const reply = `ATS Score: ${data.ats_score}
Matched: ${data.matched_keywords.join(", ")}
Missing: ${data.missing_keywords.join(", ")}
Corrections: ${data.corrections}
Suggestions: ${data.suggestions}`;

    addMessage(reply, "bot");
  } catch (err) {
    addMessage("Error contacting backend.", "bot");
    console.error(err);
  }
});
