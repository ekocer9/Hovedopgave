const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Routes
app.use('/products', require('./routes/products'));
app.use('/shops', require('./routes/shops'));
//app.use('/categories', require('./routes/categories')); // For categories
//app.use('/collections', require('./routes/collections')); // For collections
//app.use('/crawled', require('./routes/crawled')); // For crawled URLs

// Serve static files (e.g., frontend files, if any)
app.use(express.static(path.join(__dirname, 'frontend')));

// Test route
app.get('/', (req, res) => {
  res.send('Backend is running!');
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
