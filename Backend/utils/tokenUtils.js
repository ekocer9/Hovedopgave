const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'default_secret_key';
const JWT_EXPIRATION = process.env.JWT_EXPIRATION || '1h';

function generateAccessToken(user) {
  return jwt.sign(user, JWT_SECRET, { expiresIn: JWT_EXPIRATION });
}

function verifyToken(token) {
  return jwt.verify(token, JWT_SECRET);
}

module.exports = { generateAccessToken, verifyToken };
