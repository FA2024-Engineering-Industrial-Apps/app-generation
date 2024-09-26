document.addEventListener("DOMContentLoaded", function() {
    const transistorCountEl = document.getElementById("transistorCount");
    const capacitorCountEl = document.getElementById("capacitorCount");
    const resistorCountEl = document.getElementById("resistorCount");

    function fetchComponentCounts() {
        fetch('/components')
            .then(response => response.json())
            .then(data => {
                transistorCountEl.textContent = data.transistor;
                capacitorCountEl.textContent = data.capacitor;
                resistorCountEl.textContent = data.resistor;
            })
            .catch(error => {
                console.error("Error fetching component counts:", error);
            });
    }

    // Fetch counts immediately on load
    fetchComponentCounts();

    // Fetch counts every 5 seconds
    setInterval(fetchComponentCounts, 5000);
});