const express = require('express');
const router = express.Router();
const db = require('../database/db.js');
const { authorizeUser } = require('../middleware/middleware.js');

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
      products.product_type,
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
      res.json(rows);
    }
  });
});

// Search for products by name
router.get('/search', (req, res) => {
  const { query } = req.query; // Extract the search query from the request's query parameters
  console.log('Received search query:', query);

  if (!query) {
    return res.status(400).json({ error: 'Search query is required' });
  }

  const sqlQuery = `
    SELECT 
      products.id, 
      products.name, 
      products.price, 
      products.description, 
      products.product_url, 
      products.image_url,
      products.product_type,
      shops.name AS shop_name,
      shops.website_url AS shop_website
    FROM products
    LEFT JOIN shops ON products.shop_id = shops.id
    WHERE products.name LIKE ?
  `;

  db.all(sqlQuery, [`%${query}%`], (err, rows) => {
    if (err) {
      console.error('Database error in /products/search:', err.message);
      return res.status(500).json({ error: 'Failed to perform search' });
    }
    console.log('Search results:', rows);
    res.json(rows);
  });
});

// Get a specific product by ID
router.get('/:id', (req, res) => {
  console.log(`Fetching product with ID: ${req.params.id}`);

  const query = `
    SELECT 
      products.id, 
      products.name, 
      products.price, 
      products.description, 
      products.product_url, 
      products.image_url,
      products.product_type,
      shops.name AS shop_name,
      shops.website_url AS shop_website
    FROM products
    LEFT JOIN shops ON products.shop_id = shops.id
    WHERE products.id = ?
  `;

  db.get(query, [req.params.id], (err, row) => {
    if (err) {
      console.error('Database error in /products/:id:', err.message);
      res.status(500).json({ error: 'Failed to fetch product' });
    } else if (!row) {
      console.warn(`Product with ID ${req.params.id} not found.`);
      res.status(404).json({ error: 'Product not found' });
    } else {
      res.json(row);
    }
  });
});

// Add a new product
router.post('/', (req, res) => {
  const { name, price, description, product_url, image_url, product_type, shop_id } = req.body;

  // Basic validation
  if (!name || !price || !description || !product_url || !shop_id) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const query = `
    INSERT INTO products (name, price, description, product_url, image_url, product_type, shop_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `;

  db.run(query, [name, price, description, product_url, image_url, product_type, shop_id], function (err) {
    if (err) {
      console.error('Database error in POST /products:', err.message);
      res.status(500).json({ error: 'Failed to add product' });
    } else {
      console.log('Product added successfully with ID:', this.lastID);
      res.status(201).json({ message: 'Product added', productId: this.lastID });
    }
  });
});

// Redirect route for logging clicks
router.get('/redirect/:id', (req, res) => {
  const productId = req.params.id;

  // Fetch product and shop information
  const query = `
      SELECT products.id AS product_id, shops.id AS shop_id, products.product_url
      FROM products
      JOIN shops ON products.shop_id = shops.id
      WHERE products.id = ?
  `;

  db.get(query, [productId], (err, row) => {
    if (err) {
      console.error('Error fetching product details:', err.message);
      return res.status(500).send('Internal server error');
    }

    if (!row) {
      return res.status(404).send('Product not found');
    }

    const { product_id, shop_id, product_url } = row;

    // Log the click in the database
    const insertQuery = `
        INSERT INTO redirects (product_id, shop_id, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    `;
    db.run(insertQuery, [product_id, shop_id], (err) => {
      if (err) {
        console.error('Error logging click:', err.message);
      } else {
        console.log(`Click logged: Product ID ${product_id}, Shop ID ${shop_id}`);
      }
    });

    // Redirect the user to the product's URL
    res.redirect(product_url);
  });
});

module.exports = router;
