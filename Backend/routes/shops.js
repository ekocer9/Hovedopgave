const express = require('express');
const router = express.Router();
const db = require('../database/db');

// Get all shops
router.get('/', (req, res) => {
  const query = `
    SELECT * FROM shops
  `;
  db.all(query, [], (err, rows) => {
    if (err) {
      console.error(err.message);
      res.status(500).json({ error: 'Failed to fetch shops' });
    } else {
      res.json(rows);
    }
  });
});

module.exports = router;
