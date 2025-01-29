const urlParams = new URLSearchParams(window.location.search);
const loaderContainer = document.getElementById('loader-container');
const productDetailsDiv = document.getElementById("product-details");
const artikul = urlParams.get('artikul');

function showLoader() {
    productDetailsDiv.style.display = 'none';
    loaderContainer.style.display = 'block';
  }
  
  function hideLoader() {
    loaderContainer.style.display = 'none';
    productDetailsDiv.style.display = 'block';
  }

// let apiKey = localStorage.getItem('apiKey');
async function fetchProductData() {
    showLoader()
    try{
        const apiKey = localStorage.getItem('apiKey')
        const response = await fetch('/api/v1/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            },
            body: JSON.stringify({artikul: artikul})
        });
        if (response.ok) {
            hideLoader()
            const product_data = await response.json();
            
            // const productDetailsDiv = document.getElementById('product-details');
            productDetailsDiv.innerHTML = `
                <h2>${product_data.name}</h2>
                <p><b>Артикул:</b> ${product_data.artikul}</p>
                <p><b>Цена:</b> ${product_data.price}</p>
                <p><b>Рейтинг:</b> ${product_data.rating}</p>
                <p><b>Количество:</b> ${product_data.total_quantity}</p>
            `;
        } else {
            document.getElementById('product-details').innerHTML = 'Ошибка при загрузке данных';
        }
    } catch(error) {
        hideLoader()
        document.getElementById('product-details').innerHTML = 'Ошибка: ' + error;
    }
}
fetchProductData();