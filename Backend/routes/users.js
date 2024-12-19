const express = require('express');
const path = require('path');
const db = require('../database/db.js'); // Use the existing database connection

const router = express.Router();

// Login Route
router.post('/login', (req, res) => {
    const { email, password } = req.body;
  
    // Validation
    if (!email || !password) {
      return res.status(400).json({ error: 'Both email and password are required.' });
    }
  
    // Query the database to check if the user exists and the password matches
    const query = `SELECT * FROM users WHERE email = ? AND password = ?`;
    db.get(query, [email, password], (err, user) => {
      if (err) {
        console.error('Database error:', err.message);
        return res.status(500).json({ error: 'An error occurred. Please try again later.' });
      }
  
      if (!user) {
        // No matching user found
        return res.status(401).json({ error: 'Invalid email or password.' });
      }
  
      // Successful login
      res.status(200).json({ message: 'Login successful!', user: { id: user.id, username: user.username, email: user.email } });
    });
  });

// Handle user sign-up
router.post('/signup', (req, res) => {
  const { username, email, password } = req.body;

  // Validation
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  // Insert user into the database
  const query = `INSERT INTO users (username, email, password) VALUES (?, ?, ?)`;
  db.run(query, [username, email, password], function (err) {
    if (err) {
      console.error('Database error:', err.message);
      return res.status(500).json({ error: 'Failed to sign up. Username or email may already be in use.' });
    }
    res.status(201).json({ message: 'User signed up successfully!', userId: this.lastID });
  });
});

module.exports = router;
