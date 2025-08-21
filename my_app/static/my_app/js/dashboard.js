// ===== THEME PERSISTENCE =====
const root = document.documentElement;
const savedTheme = localStorage.getItem('theme');
if (savedTheme) root.setAttribute('data-theme', savedTheme);
document.getElementById('themeToggle').addEventListener('click', () => {
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  drawChart(lastSeries);
});

// ===== DATE =====
const d = new Date();
const pad = (n) => n.toString().padStart(2, '0');
document.getElementById('today').textContent = `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;

// ===== DUMMY DATA + HOOKS =====
// Bạn có thể thay thế phần này bằng API Django (fetch('/api/...'))
function fetchDashboardData() {
  // Ví dụ dữ liệu theo giờ từ 06h → 21h
  const hours = Array.from({ length: 16 }, (_, i) => i + 6);
  const values = hours.map(() => Math.floor(Math.random() * 6));
  const events = Array.from({ length: 6 }, (_, i) => ({
    time: `${pad(14 - Math.floor(i / 2))}:${pad((i % 2) * 30)}:${pad(Math.floor(Math.random() * 60))}`,
    loc: `(${(10.77 + Math.random() * 0.02).toFixed(5)}, ${(106.67 + Math.random() * 0.02).toFixed(5)})`,
    cam: `CAM-${100 + i}`,
    conf: (70 + Math.floor(Math.random() * 30)) + '%'
  }));
  return Promise.resolve({
    potholesToday: values.reduce((a, b) => a + b, 0),
    activeCameras: 12 + Math.floor(Math.random() * 4),
    acc: (89 + Math.floor(Math.random() * 4)),
    series: { labels: hours, values },
    events
  });
}

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

// ===== SIMPLE CANVAS BAR CHART (no external lib) =====
const canvas = document.getElementById('chart');
const ctx = canvas.getContext('2d');
let lastSeries = { labels: [], values: [] };

function resizeCanvas() {
  const ratio = window.devicePixelRatio || 1;
  canvas.width = canvas.clientWidth * ratio;
  canvas.height = canvas.clientHeight * ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function drawChart(series) {
  if (!series) return; lastSeries = series;
  resizeCanvas();
  const { labels, values } = series;
  const W = canvas.clientWidth; const H = canvas.clientHeight;
  ctx.clearRect(0, 0, W, H);

  // Theme aware colors
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const grid = isDark ? 'rgba(255,255,255,.08)' : 'rgba(0,0,0,.08)';
  const bar = getComputedStyle(document.documentElement).getPropertyValue('--primary') || '#74bbee';
  const axis = isDark ? '#b6c3d1' : '#64748b';

  // Padding
  const padL = 36, padR = 12, padT = 16, padB = 28;
  const chartW = W - padL - padR, chartH = H - padT - padB;

  const maxV = Math.max(5, Math.max(...values));
  const step = Math.ceil(maxV / 5);
  const yMax = step * 5;

  // Grid + Y labels
  ctx.font = '12px system-ui';
  ctx.fillStyle = axis;
  ctx.strokeStyle = grid; ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = padT + chartH - (i / 5) * chartH;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(padL + chartW, y); ctx.stroke();
    ctx.fillText(String(i * step), 4, y + 4);
  }

  // Bars
  const n = values.length;
  const gap = 6; // gap between bars
  const barW = (chartW - gap * (n - 1)) / n;
  ctx.fillStyle = bar;
  values.forEach((v, i) => {
    const x = padL + i * (barW + gap);
    const h = (v / yMax) * chartH;
    const y = padT + chartH - h;
    const radius = 6;
    // rounded rect
    roundRect(ctx, x, y, barW, h, radius);
    ctx.fill();
    // x labels
    ctx.fillStyle = axis; ctx.textAlign = 'center';
    ctx.fillText(labels[i] + "h", x + barW / 2, H - 8);
    ctx.fillStyle = bar;
  });
}

function roundRect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

window.addEventListener('resize', () => drawChart(lastSeries));

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