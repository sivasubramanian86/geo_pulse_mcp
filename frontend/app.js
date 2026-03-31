document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const userInput = document.getElementById('userInput').value;
    if (!userInput) return alert('Please enter a location!');

    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const reportContent = document.getElementById('reportContent');

    loading.classList.remove('hidden');
    results.classList.add('hidden');

    try {
        // --- Local Testing Configuration ---
        // During final deployment, this would be your Cloud Run URL.
        // For local testing, we target the GeoPulse-Agent proxy running on port 8081.
        const AGENT_URL = window.location.hostname === 'localhost' ? 'http://localhost:8081/api/analyze' : '/api/analyze';

        const response = await fetch(AGENT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: userInput })
        });

        const data = await response.json();
        const rawReport = data.analysis || "Analysis complete. See logs for details.";
        reportContent.innerHTML = marked.parse(rawReport);
        results.classList.remove('hidden');
    } catch (error) {
        console.error('Error fetching analysis:', error);
        reportContent.innerText = "Error: GeoPulse Agent is currently unreachable. Check Cloud Run status.";
        results.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
});
