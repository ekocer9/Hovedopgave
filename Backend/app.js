const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
app.use(express.static('public'));


// Middleware
app.use(cors());
app.use(bodyParser.json());

// Routes
app.use('/products', require('./routes/products'));
app.use('/users', require('./routes/users'));


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
