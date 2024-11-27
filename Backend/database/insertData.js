const db = require('./db');

// Insert a shop
function insertShop(name, website_url, description) {
  const query = `
    INSERT INTO shops (name, website_url, description)
    VALUES (?, ?, ?)
  `;
  db.run(query, [name, website_url, description], function (err) {
    if (err) {
      console.error('Error inserting shop:', err.message);
    } else {
      console.log(`Inserted shop with ID: ${this.lastID}`);
    }
  });
}

// Insert a product
function insertProduct(name, price, description, product_url, image_url, delivery_options, shop_id, category_id) {
  const query = `
    INSERT INTO products (name, price, description, product_url, image_url, delivery_options, shop_id, category_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;
  db.run(query, [name, price, description, product_url, image_url, delivery_options, shop_id, category_id], function (err) {
    if (err) {
      console.error('Error inserting product:', err.message);
    } else {
      console.log(`Inserted product with ID: ${this.lastID}`);
    }
  });
}

// Example usage
insertShop('Example Anime Shop', 'https://example.com', 'A shop selling anime merchandise.');
insertProduct(
  'Naruto Hoodie',
  49.99,
  'High-quality Naruto-themed hoodie.',
  'https://example.com/naruto-hoodie',
  'https://example.com/naruto-hoodie.jpg',
  'Ships Worldwide',
  1,
  1
);
