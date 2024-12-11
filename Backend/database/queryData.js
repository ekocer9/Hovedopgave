const db = require('./db');

// Query all products with shop and category details
function getAllProducts() {
  const query = `
  SELECT 
      products.name AS product_name, 
      products.price, 
      products.collection_name,  -- Include collection name in the query
      shops.name AS shop_name, 
      categories.name AS category_name
  FROM 
      products
  LEFT JOIN 
      shops ON products.shop_id = shops.id
  LEFT JOIN 
      categories ON products.category_id = categories.id;
`;
  db.all(query, [], (err, rows) => {
    if (err) {
      console.error('Error fetching products:', err.message);
    } else {
      rows.forEach((row) => {
        console.log(`${row.product_name} - $${row.price} (Shop: ${row.shop_name}, Category: ${row.category_name})`);
      });
    }
  });
}

// Example usage
getAllProducts();
