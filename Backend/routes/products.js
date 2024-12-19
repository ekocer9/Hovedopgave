const express = require('express');
const router = express.Router();
const db = require('../database/db.js');

// Get all products
router.get('/', (req, res) => {
  console.log('Fetching all products...');

  const query = `
    SELECT 
      products.id, 
      products.name, 
      products.price, 
      products.description, 
      products.product_url, 
      products.image_url,
      product_type TEXT,
      products.created_at, 
      shops.name AS shop_name, 
      shops.website_url AS shop_website
    FROM products
    LEFT JOIN shops ON products.shop_id = shops.id
  `;

  db.all(query, [], (err, rows) => {
    if (err) {
      console.error('Database error in /products:', err.message);
      res.status(500).json({ error: 'Failed to fetch products' });
    } else if (!rows.length) {
      console.warn('No products found in the database.');
      res.json([]);
    } else {
      console.log('Products fetched successfully:', rows);
      res.json(rows);
    }
  });
});


// Get a specific product by ID
router.get('/:id', (req, res) => {
  const query = `
    SELECT products.id, products.name, products.price, products.description, products.product_url, shops.name AS shop_name
    FROM products
    LEFT JOIN shops ON products.shop_id = shops.id
    WHERE products.id = ?
  `;
  db.get(query, [req.params.id], (err, row) => {
    if (err) {
      console.error(err.message);
      res.status(500).json({ error: 'Failed to fetch product' });
    } else if (!row) {
      res.status(404).json({ error: 'Product not found' });
    } else {
      res.json(row);
    }
  });
});

// Add a new product
router.post('/', (req, res) => {
  const { name, price, description, product_url, shop_id } = req.body;
  const query = `
    INSERT INTO products (name, price, description, product_url, shop_id)
    VALUES (?, ?, ?, ?, ?)
  `;
  db.run(query, [name, price, description, product_url, shop_id], function (err) {
    if (err) {
      console.error(err.message);
      res.status(500).json({ error: 'Failed to add product' });
    } else {
      res.status(201).json({ message: 'Product added', productId: this.lastID });
    }
  });
});

module.exports = router;
