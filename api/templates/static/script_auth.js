const authKeyInput = document.getElementById('authKeyInput');
const authButton = document.getElementById('authButton');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const authContainer = document.getElementById('auth-container');


// Проверка наличия ключа в localStorage при загрузке страницы
let apiKey = localStorage.getItem('apiKey');

// Инициализируем и сразу обновляем вид
// updateView(apiKey);


// Обработчик кнопки авторизации
authButton.addEventListener('click', async () => {
    apiKey = authKeyInput.value;
    localStorage.setItem('apiKey', apiKey);
    try {
        const response = await fetch(`/main`, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + apiKey
            },
        });
        if (response.ok) {
            const data = ''
        } else {
            const errorData = await response.json();
            resultDiv.textContent = errorData.detail;
        }
    } catch (error) {
        resultDiv.textContent = 'Ошибка: ' + error;
        }
});

// // Функция для обновления вида страницы
// function updateView(apiKey) {
//     if (apiKey) {
//         mainContent.style.display = 'block';
//        authContainer.style.display = 'none';
//    } else {
//       mainContent.style.display = 'none';
//         authContainer.style.display = 'block';
//     }
// }
