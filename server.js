const express = require("express");
const path = require("path");

const app = express();

// Serve static files from "public"
app.use(express.static(path.join(__dirname, "public")));

// Default route → serve index.html
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Chatbot frontend running at http://localhost:${port}`);
});
