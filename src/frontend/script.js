function updateTime() {
    const timerElement = document.getElementById('timer');
    const now = new Date();
    timerElement.textContent = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime(); // Initial call to display time immediately