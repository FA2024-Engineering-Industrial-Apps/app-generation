/* script.js */

function fetchComponentCounts() {
    fetch('https://api.manufacturing-system.com/api/v1/component-counts')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('transistor-count').innerText = data.transistor_count;
            document.getElementById('capacitor-count').innerText = data.capacitor_count;
            document.getElementById('resistor-count').innerText = data.resistor_count;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

// Fetch component counts every 5 seconds
setInterval(fetchComponentCounts, 5000);

// Initial fetch when page loads
window.onload = fetchComponentCounts;