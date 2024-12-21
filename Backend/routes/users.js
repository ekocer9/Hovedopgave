const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const db = require('../database/db.js');
const { authorizeUser } = require('../middleware/middleware.js');
const { generateAccessToken } = require('../utils/tokenUtils.js');

const router = express.Router();

router.get('/profile', authorizeUser, async (req, res) => {
  const userId = req.user.id;

  try {
    const query = `SELECT username, email, created_at FROM users WHERE id = ?`;
    db.get(query, [userId], (err, user) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to fetch user profile' });
      }

      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json(user);
    });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Login Route
router.post('/login', (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required.' });
  }

  console.log('Login request received:', email);

  const query = `SELECT id, username, email, password FROM users WHERE email = ?`;
  db.get(query, [email], async (err, user) => {
    if (err) {
      console.error('Database error:', err.message);
      return res.status(500).json({ error: 'Internal server error during database query.' });
    }

    if (!user) {
      console.warn('No user found for email:', email);
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    try {
      console.log('User found:', user.username);

      const isPasswordValid = await bcrypt.compare(password, user.password);
      if (!isPasswordValid) {
        console.warn('Invalid password for user:', email);
        return res.status(401).json({ error: 'Invalid email or password.' });
      }

      const token = generateAccessToken({ id: user.id, username: user.username, email: user.email });

      console.log('JWT generated:', token);
      res.status(200).json({ message: 'Login successful', token });
    } catch (err) {
      console.error('Error during password validation or token generation:', err.message);
      res.status(500).json({ error: 'Internal server error during authentication.' });
    }
  });
});

// User Profile Route
router.put('/profile', authorizeUser, async (req, res) => {
  const userId = req.user.id;
  const { username, email, password } = req.body;

  try {
    // Prepare the SQL query dynamically based on provided fields
    const fields = [];
    const values = [];

    if (username) {
      fields.push('username = ?');
      values.push(username);
    }

    if (email) {
      fields.push('email = ?');
      values.push(email);
    }

    if (password) {
      const saltRounds = parseInt(process.env.BCRYPT_SALT_ROUNDS, 10);
      const hashedPassword = await bcrypt.hash(password, saltRounds);
      fields.push('password = ?');
      values.push(hashedPassword);
    }

    // If no fields are provided, return an error
    if (fields.length === 0) {
      return res.status(400).json({ error: 'No fields provided for update' });
    }

    // Construct the SQL query dynamically
    const query = `UPDATE users SET ${fields.join(', ')} WHERE id = ?`;
    values.push(userId);

    db.run(query, values, function (err) {
      if (err) {
        console.error('Error updating profile:', err.message);
        return res.status(500).json({ error: 'Failed to update profile' });
      }

      res.json({ message: 'Profile updated successfully' });
    });
  } catch (err) {
    console.error('Error updating profile:', err.message);
    res.status(500).json({ error: 'Failed to update profile' });
  }
});

// Signup Route
router.post('/signup', async (req, res) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  try {
    const saltRounds = parseInt(process.env.BCRYPT_SALT_ROUNDS, 10);
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    const query = `INSERT INTO users (username, email, password) VALUES (?, ?, ?)`;
    db.run(query, [username, email, hashedPassword], function (err) {
      if (err) {
        console.error('Error during user registration:', err.message);
        return res.status(500).json({ error: 'Username or email may already be in use.' });
      }
      res.status(201).json({ message: 'User signed up successfully!', userId: this.lastID });
    });
  } catch (err) {
    console.error('Error during signup:', err.message);
    res.status(500).json({ error: 'Internal server error.' });
  }
});

module.exports = router;