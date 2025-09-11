// ===== THEME PERSISTENCE =====
const root = document.documentElement;
const savedTheme = localStorage.getItem('theme');
if (savedTheme) root.setAttribute('data-theme', savedTheme);
const themeBtn = document.getElementById('themeToggle');
if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    drawChart(lastSeries);
  });
}

// ===== DATE =====
const d = new Date();
const pad = (n) => n.toString().padStart(2, '0');
document.getElementById('today').textContent = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;


// Hooks để bạn cập nhật từ backend
function updateDashboard({ potholesToday, activeCameras, acc, series, events }) {
  document.getElementById('kpiPotholes').textContent = potholesToday;
  document.getElementById('kpiCameras').textContent = activeCameras;
  document.getElementById('kpiAcc').textContent = acc + '%';
  drawChart(series);
  renderEvents(events);
}

function renderEvents(rows) {
  const tbody = document.querySelector('#eventsTable tbody');
  tbody.innerHTML = '';
  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.time}</td><td>${r.loc}</td><td>${r.cam}</td><td>${r.conf}</td>`;
    tbody.appendChild(tr);
  });
}







// ===== INIT =====
document.getElementById('refreshBtn').addEventListener('click', async () => {
  const data = await fetchDashboardData();
  updateDashboard(data);
});


(async function init() {
  const data = await fetchDashboardData();
  updateDashboard(data);
})();

// Active state demo (for menu)
document.querySelectorAll('#menu a').forEach(a => {
  a.addEventListener('click', () => {
    document.querySelectorAll('#menu a').forEach(el => el.classList.remove('active'));
    a.classList.add('active');
  })
});