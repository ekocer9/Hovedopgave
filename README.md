# Merchiverse - Anime Merchandise Affiliate Platform

Welcome to **Merchiverse**, an anime merchandise affiliate platform that connects otaku fans with the best merchandise across various stores. This platform offers a seamless shopping experience, showcasing products from small businesses and established stores, all in one place.

## Features

### 1. **Crawling and Scraping**
- Automated crawling of product links from anime merchandise stores.
- Dynamic scraping of product details using Selenium and BeautifulSoup.
- Categorization of products into predefined categories based on keywords.

### 2. **Backend**
- Node.js and SQLite3-powered backend for efficient data storage.
- RESTful APIs to handle products, users, and authentication.
- Secure user authentication with JWT tokens.

### 3. **Frontend**
- Responsive user interface built with HTML, CSS, and JavaScript.
- Dynamic product listing and searching capabilities.
- User profiles with editing options.

### 4. **Affiliate Links**
- Redirection system that tracks user clicks on affiliate links.
- Support for logging product redirects in the database.

---

## Directory Structure

```
├── components/           # Shared HTML components
├── database/             # SQLite database and schema
├── pages/                # Frontend pages (HTML files)
├── public/               # Static files (CSS, JS, images)
├── routes/               # Backend API routes
├── scripts/              # Web crawling and scraping scripts
├── styles/               # CSS files
└── utils/                # Utility functions
```

---

## Installation

### Prerequisites
- Node.js (>= 16.x)
- Python 3.x
- SQLite3

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/merchiverse.git
   cd merchiverse
   ```

2. **Backend Setup**
   - Navigate to the `Backend` folder.
   - Install dependencies:
     ```bash
     npm install
     ```
   - Create a `.env` file:
     ```
     JWT_SECRET=your_secret_key
     JWT_EXPIRATION=1h
     BCRYPT_SALT_ROUNDS=10
     ```
   - Start the backend server:
     ```bash
     npm start
     ```

3. **Frontend Setup**
   - Navigate to the `Frontend` folder.
   - Start the frontend server:
     ```bash
     node server.js
     ```

4. **Database Setup**
   - Initialize the SQLite database:
     ```bash
     sqlite3 database/anime_merchandise.db < database/schema.sql
     ```

5. **Run Crawlers and Scrapers**
   - Ensure all dependencies are installed:
     ```bash
     pip install -r requirements.txt
     ```
   - Execute the crawlers and scrapers:
     ```bash
     python web_crawler.py
     python web_scraper.py
     ```

---

## Usage

### Access the Platform
- Open your browser and navigate to:
  - **Frontend**: [http://localhost:4000](http://localhost:4000)
  - **Backend API**: [http://localhost:3000](http://localhost:3000)

### Features Overview
- **Browse Products**: View all available products from various stores.
- **Search Products**: Use the search bar to find specific merchandise.
- **Sign Up/Login**: Create an account or log in to access personalized features.
- **Profile Management**: Edit your profile information securely.
- **Affiliate Links**: Click on products to visit the seller's website.

---

## API Endpoints

### Products
- `GET /products` - Fetch all products.
- `GET /products/search` - Search for products by name.
- `GET /products/:id` - Get details of a specific product.
- `POST /products` - Add a new product (Admin only).

### Users
- `POST /users/signup` - Create a new user.
- `POST /users/login` - Log in a user.
- `GET /users/profile` - Fetch user profile (Authenticated users).
- `PUT /users/profile` - Update user profile (Authenticated users).

---