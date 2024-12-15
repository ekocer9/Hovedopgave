async function loadComponent(id, path) {
  try {
    const response = await fetch(`/src/components/${path}?v=${new Date().getTime()}`); // Prevent caching
    const html = await response.text();
    document.getElementById(id).innerHTML = html;
  } catch (error) {
    console.error(`Failed to load component: ${id}`, error);
    document.getElementById(id).innerHTML = `<p class="text-red-500">Failed to load ${id}.</p>`;
  }
}

async function loadSingleComponent() {
  try {
    const response = await fetch('/src/components/navbar.html');
    console.log('Navbar fetch response status:', response.status); // Debugging log
    if (!response.ok) throw new Error(`Failed to fetch component: ${response.statusText}`);
    
    const html = await response.text();
    document.getElementById('navbar').innerHTML = html;
    console.log('Navbar successfully loaded!');
  } catch (error) {
    console.error('Error fetching navbar:', error);
    document.getElementById('navbar').innerHTML = `<p class="text-red-500">Failed to load navbar.</p>`;
  }
}

async function loadProducts() {
  const productContainer = document.getElementById('product-container');
  try {
    const response = await fetch('http://localhost:3000/products'); // Ensure correct URL
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
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
  console.log('Image URL:', product.image); // Debugging log

  return `
    <div class="border p-4 rounded-md shadow-lg">
      <img src="${product.image_url}" alt="${product.name}" class="w-full h-48 object-cover" />
      <h3 class="text-lg font-bold mt-2">${product.name}</h3>
      <p class="text-gray-600">${product.price}</p>
      <a href="/product/${product.id}" class="text-blue-500 hover:underline">View Details</a>
    </div>
  `;
}

async function loadPage() {
  loadComponent('navbar', 'navbar.html');
  loadComponent('header', 'header.html');
  loadComponent('footer', 'footer.html');
  await loadProducts();
}

// Call the function
loadSingleComponent();

loadPage();
