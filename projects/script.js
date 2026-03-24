async function searchWeather() {
    const city = document.getElementById('city-search').value;
    try {
        const response = await fetch(`/forecast/${city}`);
        const forecast = await response.json();
        displayForecast(forecast);
    } catch (error) {
        console.error('Error fetching weather data:', error);
    }
}

function displayForecast(forecast) {
    const tableBody = document.getElementById('forecast-table');
    tableBody.innerHTML = '';
    forecast.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.date}</td>
            <td>${item.temperature}°C</td>
            <td>${item.humidity}%</td>
            <td>${item.description}</td>
        `;
        tableBody.appendChild(row);
    });
}
