const authKeyInput = document.getElementById('authKeyInput');
const authButton = document.getElementById('authButton');
const artikulInput = document.getElementById('imeiInput');
const infoButton = document.getElementById('infoButton');
// const subscribeButton = document.getElementById('subscribeButton');
// const unsubscribeButton = document.getElementById('unsubscribeButton');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const authContainer = document.getElementById('auth-container');
const mainContent = document.getElementById('main-content');

// Проверка наличия ключа в localStorage при загрузке страницы
let apiKey = localStorage.getItem('apiKey');

if (apiKey) {
    updateView(apiKey)
}

// Обработчик кнопки авторизации
authButton.addEventListener('click', async () => {
    apiKey = authKeyInput.value;
    localStorage.setItem('apiKey', apiKey);
    try {
        if (apiKey) {
            updateView(apiKey)
        } else {
            const errorData = await response.json();
            resultDiv.textContent = errorData.detail;
        }
    } catch (error) {
        resultDiv.textContent = 'Ошибка: ' + error;
        }
});

// Функция для обновления вида страницы
function updateView(apiKey) {
    if (apiKey) {
        mainContent.style.display = 'block';
        authContainer.style.display = 'none';
    } else {
        mainContent.style.display = 'none';
        authContainer.style.display = 'block';
    }
}
infoButton.addEventListener('click', async () => {
    errorDiv.textContent = '';
    const imei = imeiInput.value;
    if (!imei) {
        errorDiv.textContent = 'Пожалуйста, введите IMEI.';
        return;
    }
    window.location.href = `imei_info.html?imei=${imei}`;
});
