async function loadComponent(id, path) {
  try {
    const element = document.getElementById(id);
    if (!element) {
      throw new Error(`Element with ID "${id}" not found in the DOM.`);
    }
    const response = await fetch(`/components/${path}?v=${new Date().getTime()}`);
    const html = await response.text();
    element.innerHTML = html;
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
      <!-- Fixed Image Container -->
      <div class="w-full h-60 bg-gray-200 flex items-center justify-center overflow-hidden">
        <img src="${product.image_url}" alt="${product.name}" class="object-cover w-full h-full" />
      </div>
      <!-- Product Details -->
      <div class="p-4">
        <h3 class="text-lg font-bold">${product.name}</h3>
        <p class="text-gray-600">${product.price}</p>
        <a href="/product/${product.id}" class="text-blue-500 hover:underline">View Details</a>
      </div>
    </div>
  `;
}

async function loadPage() {
  // Conditionally load navbar
  if (document.getElementById('navbar')) {
    await loadComponent('navbar', 'navbar.html');
  }

  // Conditionally load header
  if (document.getElementById('header')) {
    await loadComponent('header', 'header.html');
  }

  // Conditionally load footer
  if (document.getElementById('footer')) {
    await loadComponent('footer', 'footer.html');
  }

  // Conditionally load products only on pages with 'product-container'
  if (document.getElementById('product-container')) {
    await loadProducts();
  }
}


loadPage();