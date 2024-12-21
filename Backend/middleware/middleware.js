const { verifyToken } = require('../utils/tokenUtils.js');

function authorizeUser(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized: No token provided in the Authorization header' });
  }

  try {
    req.user = verifyToken(token); // Decodes and verifies the token
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      console.error('Authorization failed: Token has expired');
      return res.status(401).json({ error: 'Unauthorized: Token has expired' });
    }
    console.error('Authorization failed:', err.message);
    return res.status(403).json({ error: 'Forbidden: Invalid token' });
  }
}

module.exports = { authorizeUser };
