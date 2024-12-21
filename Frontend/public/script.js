async function loadComponent(id, path) {
  try {
    const element = document.getElementById(id);
    if (!element) {
      throw new Error(`Element with ID "${id}" not found in the DOM.`);
    }
    const response = await fetch(`/components/${path}?v=${new Date().getTime()}`);
    const html = await response.text();
    element.innerHTML = html;

    // Attach event listener for the search form if it exists
    if (id === 'navbar') {
      const searchForm = document.querySelector('#search-form');
      if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
        console.log('Search form event listener attached.');
      } else {
        console.warn('Search form with ID "search-form" not found after loading navbar.');
      }
    }
  } catch (error) {
    console.error(`Failed to load component: ${id}`, error);
  }
}

async function loadProducts() {
  const productContainer = document.getElementById('product-container');
  try {
    const response = await fetch('http://localhost:3000/products');
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const products = await response.json();

    if (!products.length) {
      productContainer.innerHTML = `<p>No products available.</p>`;
    } else {
      productContainer.innerHTML = products.map(createProductCard).join('');
    }
  } catch (error) {
    console.error('Error fetching products:', error);
    productContainer.innerHTML = `<p class="text-red-500">Failed to load products. Please try again later.</p>`;
  }
}

function createProductCard(product) {
  return `
    <div class="border rounded-md shadow-lg bg-white overflow-hidden">
      <div class="w-full h-60 bg-gray-200 flex items-center justify-center overflow-hidden">
        <a href="/product/${product.id}" class="block w-full h-full">
          <img src="${product.image_url}" alt="${product.name}" class="object-cover w-full h-full" />
        </a>
      </div>
      <div class="p-4">
        <h3 class="text-lg font-bold">
          <a href="/product/${product.id}" class="hover:underline">${product.name}</a>
        </h3>
        <p class="text-gray-600">$${product.price.toFixed(2)}</p>
        <div class="mt-4 flex space-x-4">
          <!-- View Details Button -->
          <a href="/product/${product.id}" 
             class="px-4 py-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600">
            View Details
          </a>
        </div>
      </div>
    </div>
  `;
}

async function handleSearch(event) {
  event.preventDefault();
  const searchInput = document.querySelector('#search-bar');
  const query = searchInput.value.trim();

  console.log('Search query:', query); // Debugging line

  if (!query) {
    alert('Please enter a search term.');
    return;
  }

  const productContainer = document.getElementById('product-container');
  try {
    const response = await fetch(`http://localhost:3000/products/search?query=${encodeURIComponent(query)}`);
    console.log('Search request sent to:', `http://localhost:3000/products/search?query=${encodeURIComponent(query)}`); // Debugging line
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    const products = await response.json();

    if (!products.length) {
      productContainer.innerHTML = `<p>No products found for "${query}".</p>`;
    } else {
      productContainer.innerHTML = products.map(createProductCard).join('');
    }
  } catch (error) {
    console.error('Error fetching search results:', error);
    productContainer.innerHTML = `<p class="text-red-500">Failed to load search results. Please try again later.</p>`;
  }
}

async function updateNavbar() {
  const navbarButtons = document.getElementById('navbar-buttons');
  const token = sessionStorage.getItem('token');

  if (token) {
    // Decode token to get user information (username)
    const user = JSON.parse(atob(token.split('.')[1]));

    navbarButtons.innerHTML = `
      <a href="/profile" 
         class="text-gray-700 font-medium border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-100 transition duration-200">
        Profile
      </a>
      <button id="logout-btn" 
              class="text-white font-medium bg-red-500 rounded-md px-4 py-2 hover:bg-red-600 transition duration-200">
        Logout
      </button>
    `;

    // Attach logout functionality
    document.getElementById('logout-btn').addEventListener('click', () => {
      sessionStorage.removeItem('token');
      window.location.href = '/';
    });
  } else {
    navbarButtons.innerHTML = `
      <a href="/login" 
         class="text-gray-700 font-medium border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-100 transition duration-200">
        Log in
      </a>
      <a href="/signup" 
         class="text-white font-medium bg-blue-500 rounded-md px-4 py-2 hover:bg-blue-600 transition duration-200">
        Sign Up
      </a>
    `;
  }
}


async function loadProfile() {
  const profileContainer = document.getElementById('profile-data');
  const token = sessionStorage.getItem('token');

  if (!token) {
    alert('You must log in to access your profile.');
    window.location.href = '/login';
    return;
  }

  try {
    const response = await fetch('http://localhost:3000/users/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`, // Include token in the Authorization header
      },
    });

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Forbidden: Invalid or expired token.');
      }
      throw new Error('Failed to fetch profile');
    }

    const user = await response.json();
    profileContainer.innerHTML = `
      <p><strong>Username:</strong> ${user.username}</p>
      <p><strong>Email:</strong> ${user.email}</p>
      <p><strong>Member Since:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
    `;
  } catch (err) {
    console.error('Error loading profile:', err);
    alert(err.message);
    sessionStorage.removeItem('token');
    window.location.href = '/login';
  }
}

async function loadProfileContent() {
  const token = sessionStorage.getItem('token');

  if (!token) {
    alert('You must log in to access your profile.');
    window.location.href = '/login';
    return;
  }

  try {
    const response = await fetch('http://localhost:3000/users/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Access forbidden: You must log in again.');
      }
      throw new Error('Failed to fetch profile');
    }

    const user = await response.json();
    document.getElementById('username').textContent = user.username;
    document.getElementById('user-initials').textContent = user.username[0].toUpperCase();

  } catch (err) {
    console.error('Error loading profile:', err.message);
    alert(err.message);
    sessionStorage.removeItem('token');
    window.location.href = '/login';
  }
}

async function loadPage() {
  if (document.getElementById('navbar')) {
    await loadComponent('navbar', 'navbar.html');
    await updateNavbar();
  }

  if (document.getElementById('profile-container')) {
    const token = sessionStorage.getItem('token');
    if (!token) {
      alert('You must log in to access your profile.');
      window.location.href = '/login';
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/users/profile', {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 403) throw new Error('Access denied');
        throw new Error('Failed to fetch profile');
      }

      const user = await response.json();
      document.getElementById('username').textContent = user.username;
      document.getElementById('user-initials').textContent = user.username[0].toUpperCase();
    } catch (err) {
      console.error('Error loading profile:', err.message);
      sessionStorage.removeItem('token'); // Clear invalid token
      window.location.href = '/login';
    }
  }

  // Conditionally load header
  if (document.getElementById('header')) {
    await loadComponent('header', 'header.html');
  }

  // Conditionally load footer
  if (document.getElementById('footer')) {
    await loadComponent('footer', 'footer.html');
  }

  if (document.getElementById('product-container')) {
    await loadProducts();
  }

  if (document.getElementById('product-container')) {
    await loadProducts();
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadPage(); // Load page components
});