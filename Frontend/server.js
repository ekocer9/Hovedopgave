const express = require('express');
const path = require('path');

const app = express();
const PORT = 4000;

// Middleware to parse JSON data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (CSS, JS, images) from 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

// Serve components dynamically from 'components' folder
app.use('/components', express.static(path.join(__dirname, 'components')));

// Routes for pages
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'index.html'));
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/signup', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'signup.html'));
});

// Catch-all route for unmatched routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Frontend server is running at http://localhost:${PORT}`);
});
