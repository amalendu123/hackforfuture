// Chatbot functionality
document.getElementById('send-btn').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value;
    const chatBox = document.getElementById('chat-box');

    if (userInput.trim() !== "") {
        chatBox.innerHTML += `<div class="user-message"><strong>You:</strong> ${userInput}</div>`;
        document.getElementById('user-input').value = "";

        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: userInput })
        });

        const data = await response.json();
        chatBox.innerHTML += `<div class="bot-message"><strong>Bot:</strong> ${data.response}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

// Material recommender functionality
function getRecommendations() {
    const budget = document.getElementById('budget').value;
    const buildingType = document.getElementById('buildingType').value;

    fetch(`/recommend?budget=${budget}&buildingType=${buildingType}`)
        .then(response => response.json())
        .then(data => {
            let results = document.getElementById('results');
            results.innerHTML = "";

            if (data.recommendations) {
                data.recommendations.forEach(item => {
                    results.innerHTML += `<h3>${item.MaterialName}</h3><p>${item.Description}</p>`;
                });
            } else {
                results.innerHTML = `<p>${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
