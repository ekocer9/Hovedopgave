const express = require('express');
const path = require('path');

const app = express();
const PORT = 4000;

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Handle requests for components dynamically
app.get('/src/components/:component', (req, res) => {
  const { component } = req.params;
  const filePath = path.join(__dirname, 'src', 'components', component);
  
  console.log(`Serving component: ${component}`);
  console.log(`Resolved file path: ${filePath}`);
  
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error(`Failed to load component: ${component}`, err);
      res.status(404).send('Component not found');
    }
  });
});


// Fallback to index.html for other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Frontend server is running on http://localhost:${PORT}`);
});