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

// ===== DUMMY DATA + HOOKS =====
// Bạn có thể thay thế phần này bằng API Django (fetch('/api/...'))
// ===== DUMMY DATA + HOOKS =====
// Dữ liệu tĩnh để test biểu đồ
function fetchDashboardData() {
  const hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
  const values = [2, 1, 0, 3, 4, 2, 5, 6, 2, 3, 1, 0, 4, 2, 1, 3]; // dữ liệu cố định

  const events = [
    { time: "08:15:23", loc: "(10.77001, 106.67890)", cam: "CAM-101", conf: "92%" },
    { time: "10:30:45", loc: "(10.77123, 106.67985)", cam: "CAM-102", conf: "87%" },
    { time: "14:05:12", loc: "(10.77234, 106.67654)", cam: "CAM-103", conf: "95%" },
  ];

  return Promise.resolve({
    potholesToday: values.reduce((a, b) => a + b, 0), // tổng ổ gà
    activeCameras: 14, // số camera hoạt động
    acc: 91,           // độ chính xác %
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