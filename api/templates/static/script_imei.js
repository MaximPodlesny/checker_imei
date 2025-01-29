const urlParams = new URLSearchParams(window.location.search);
const loaderContainer = document.getElementById('loader-container');
const imeiDetailsDiv = document.getElementById("imei-details");
const imei = urlParams.get('imei');

function showLoader() {
    productDetailsDiv.style.display = 'none';
    loaderContainer.style.display = 'block';
  }
  
  function hideLoader() {
    loaderContainer.style.display = 'none';
    productDetailsDiv.style.display = 'block';
  }

// let apiKey = localStorage.getItem('apiKey');
async function fetchImeiData() {
    showLoader()
    try{
        const apiKey = localStorage.getItem('apiKey')
        const response = await fetch('/api/v1/imei', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            },
            body: JSON.stringify({imei: imei})
        });
        if (response.ok) {
            hideLoader()
            const imei_data = await response.json();
            
            // const productDetailsDiv = document.getElementById('product-details');
            imeiDetailsDiv.innerHTML = `
                <h2>${imei_data.deviceName}</h2>
                <p><b>Изображение:</b> <img src="${imei_data.image}" alt="${imei_data.deviceName}"></p>
                <p><b>IMEI:</b> ${imei_data.imei}</p>
                <p><b>Предположительная дата покупки:</b> ${new Date(imei_data.estPurchaseDate * 1000).toLocaleDateString()}</p>
                <p><b>Симу-лок:</b> ${imei_data.simLock ? 'Да' : 'Нет'}</p>
                <p><b>Статус гарантии:</b> ${imei_data.warrantyStatus}</p>
                <p><b>Покрытие ремонта:</b> ${imei_data.repairCoverage ? 'Да' : 'Нет'}</p>
                <p><b>Техническая поддержка:</b> ${imei_data.technicalSupport ? 'Да' : 'Нет'}</p>
                <p><b>Описание модели:</b> ${imei_data.modelDesc}</p>
                <p><b>Демо-версия:</b> ${imei_data.demoUnit ? 'Да' : 'Нет'}</p>
                <p><b>Восстановленный:</b> ${imei_data.refurbished ? 'Да' : 'Нет'}</p>
                <p><b>Страна покупки:</b> ${imei_data.purchaseCountry}</p>
                <p><b>Регион Apple:</b> ${imei_data.apple_region}</p>
                <p><b>FMI включен:</b> ${imei_data.fmiOn ? 'Да' : 'Нет'}</p>
                <p><b>Режим "Потеряно":</b> ${imei_data.lostMode ? 'Да' : 'Нет'}</p>
                <p><b>Статус блокировки в США:</b> ${imei_data.usaBlockStatus}</p>
                <p><b>Сеть:</b> ${imei_data.network}</p>
            `;
        } else {
            document.getElementById('imei-details').innerHTML = 'Ошибка при загрузке данных';
        }
    } catch(error) {
        hideLoader()
        document.getElementById('imei-details').innerHTML = 'Ошибка: ' + error;
    }
}
fetchImeiData();