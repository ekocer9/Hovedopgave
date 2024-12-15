const sqlite3 = require('sqlite3').verbose();

// Initialize the SQLite database
const path = require('path');
const db = new sqlite3.Database(path.join(__dirname, 'anime_merchandise.db'), (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to SQLite database.');

    // Create the tables if they don't exist
    db.run(`
      CREATE TABLE IF NOT EXISTS shops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        website_url TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS crawled (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          url TEXT UNIQUE NOT NULL,
          collection_name TEXT,
          status TEXT DEFAULT 'pending',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    db.run(`
      CREATE TABLE IF NOT EXISTS products (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          price REAL,
          description TEXT,
          product_url TEXT UNIQUE NOT NULL,
          image_url TEXT,
          delivery_options TEXT,
          source_id INTEGER,
          shop_id INTEGER, -- Add shop_id column
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (source_id) REFERENCES crawled (id),
          FOREIGN KEY (shop_id) REFERENCES shops (id) -- Set sop_id as foreign key
      )
    `);
  }
});

module.exports = db;
