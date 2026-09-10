async function checkHealth() {
  const target = document.getElementById('connection');
  if (!target) return;
  try {
    const response = await fetch('/api/health');
    if (!response.ok) throw new Error('Backend unavailable');
    const data = await response.json();
    if (data.status !== 'ok') throw new Error('Unexpected health response');
    target.textContent = 'Flask backend connected';
  } catch {
    target.textContent = 'Backend unavailable. Check that Flask is running.';
  }
}
checkHealth();
