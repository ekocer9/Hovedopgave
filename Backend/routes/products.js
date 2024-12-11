// Get all products
app.get('/products', (req, res) => {
    const query = `
      SELECT products.id, products.name, products.price, products.description, products.product_url, shops.name AS shop_name
      FROM products
      LEFT JOIN shops ON products.shop_id = shops.id
    `;
    db.all(query, [], (err, rows) => {
      if (err) {
        console.error(err.message);
        res.status(500).json({ error: 'Failed to fetch products' });
      } else {
        res.json(rows);
      }
    });
  });  

  // Get a specific product by ID
app.get('/products/:id', (req, res) => {
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
app.post('/products', (req, res) => {
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
  