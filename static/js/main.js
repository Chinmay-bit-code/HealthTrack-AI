// HealthTrack AI — Main JavaScript

// ---- Sidebar Toggle ----
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (sidebar) {
    const isOpen = sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('visible', isOpen);
  }
}

// ---- Theme Toggle ----
function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('ht-theme', next);
  updateThemeIcon(next);
  updateChartsTheme();
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

// ---- Initialize Theme ----
function initTheme() {
  const saved = localStorage.getItem('ht-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

// ---- Auto-dismiss Alerts ----
function initAlerts() {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s, transform 0.4s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
}

// ---- Animate Progress Bars ----
function animateProgressBars() {
  document.querySelectorAll('.mc-progress-fill, .progress-bar').forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = target; }, 100);
    });
  });
}

// ---- Counter Animation ----
function animateCounter(el) {
  const text = el.textContent.trim();
  if (text === '—' || text === '') return;
  const num = parseFloat(text.replace(/,/g, ''));
  if (isNaN(num)) return;
  const small = el.querySelector('small');
  const suffix = small ? small.outerHTML : '';
  const isDecimal = text.includes('.');
  const duration = 900;
  const startTime = performance.now();
  const update = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const val = num * ease;
    const formatted = isDecimal ? val.toFixed(1) : Math.round(val).toLocaleString();
    el.innerHTML = formatted + (suffix || '');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

function initCounters() {
  document.querySelectorAll('.mc-value').forEach(el => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { animateCounter(el); observer.unobserve(el); } });
    }, { threshold: 0.5 });
    observer.observe(el);
  });
}

// ---- Chart Theme Update ----
function updateChartsTheme() {
  if (typeof Chart === 'undefined') return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gc = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.06)';
  const tc = isDark ? '#475569' : '#94a3b8';
  Object.values(Chart.instances).forEach(chart => {
    if (!chart.options.scales) return;
    Object.values(chart.options.scales).forEach(scale => {
      if (scale.grid) scale.grid.color = gc;
      if (scale.ticks) scale.ticks.color = tc;
    });
    chart.update('none');
  });
}

// ---- Responsive: close sidebar on resize ----
function handleResize() {
  if (window.innerWidth > 768) {
    const s = document.getElementById('sidebar');
    const o = document.getElementById('sidebarOverlay');
    if (s) s.classList.remove('open');
    if (o) o.classList.remove('visible');
  }
}

// ---- Animated Particle / Starfield Background ----
function initParticles() {
  const canvas = document.getElementById('bgCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H;
  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const COUNT = 200;
  const particles = [];

  function isDark() {
    return document.documentElement.getAttribute('data-theme') !== 'light';
  }

  function Particle(randomY) {
    this.reset = function(init) {
      this.x  = Math.random() * W;
      this.y  = init ? Math.random() * H : H + 8;
      this.r  = Math.random() * 1.6 + 0.3;          // radius 0.3–1.9
      this.vx = (Math.random() - 0.5) * 0.28;
      this.vy = -(Math.random() * 0.22 + 0.04);     // drift upward slowly
      this.baseAlpha = Math.random() * 0.55 + 0.25;
      this.alpha     = this.baseAlpha;
      this.twinkleSpeed = Math.random() * 0.007 + 0.002;
      this.twinkleDir   = Math.random() > 0.5 ? 1 : -1;
      this.glowMult = Math.random() > 0.85 ? 4.5 : 2.8; // occasional brighter star
    };
    this.reset(randomY);
  }

  Particle.prototype.update = function() {
    this.x += this.vx;
    this.y += this.vy;
    // twinkle
    this.alpha += this.twinkleDir * this.twinkleSpeed;
    if (this.alpha > this.baseAlpha + 0.3 || this.alpha < 0.05) this.twinkleDir *= -1;
    // wrap horizontal
    if (this.x < -4) this.x = W + 4;
    if (this.x > W + 4) this.x = -4;
    // recycle when off top
    if (this.y < -8) this.reset(false);
  };

  Particle.prototype.draw = function() {
    const dark = isDark();
    // Dark mode: bright white stars; light mode: soft indigo dots
    const rgb = dark ? '220,235,255' : '30,40,120';
    const gr  = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * this.glowMult);
    gr.addColorStop(0,   `rgba(${rgb},${Math.min(this.alpha * 0.85, 1)})`);
    gr.addColorStop(0.4, `rgba(${rgb},${Math.min(this.alpha * 0.35, 1)})`);
    gr.addColorStop(1,   `rgba(${rgb},0)`);
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r * this.glowMult, 0, Math.PI * 2);
    ctx.fillStyle = gr;
    ctx.fill();
    // hard core
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${rgb},${Math.min(this.alpha, 1)})`;
    ctx.fill();
  };

  for (let i = 0; i < COUNT; i++) particles.push(new Particle(true));

  (function loop() {
    ctx.clearRect(0, 0, W, H);
    // very faint nebula wash in dark mode
    if (isDark()) {
      const nb = ctx.createRadialGradient(W * 0.3, H * 0.4, 0, W * 0.3, H * 0.4, W * 0.6);
      nb.addColorStop(0,   'rgba(16,185,129,0.04)');
      nb.addColorStop(0.5, 'rgba(99,102,241,0.03)');
      nb.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.fillStyle = nb;
      ctx.fillRect(0, 0, W, H);
    }
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(loop);
  })();
}

// ---- Ripple effect on buttons ----
function addRipple(e) {
  const btn = e.currentTarget;
  const ripple = document.createElement('span');
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  ripple.style.cssText = `
    position:absolute;width:${size}px;height:${size}px;
    border-radius:50%;transform:scale(0);
    background:rgba(255,255,255,0.25);pointer-events:none;
    left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px;
    animation:ripple 0.5s ease-out;
  `;
  btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 500);
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initParticles();
  initAlerts();
  animateProgressBars();
  initCounters();
  window.addEventListener('resize', handleResize);

  // Ripple on primary buttons
  document.querySelectorAll('.btn-primary, .btn-auth, .btn-log-now, .btn-topbar-log').forEach(btn => {
    btn.addEventListener('click', addRipple);
  });

  // Watch for theme attr changes to update charts
  new MutationObserver(mutations => {
    mutations.forEach(m => { if (m.attributeName === 'data-theme') updateChartsTheme(); });
  }).observe(document.documentElement, { attributes: true });

  // Chart.js global defaults
  if (typeof Chart !== 'undefined') {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = isDark ? '#1e293b' : '#0f172a';
    Chart.defaults.plugins.tooltip.titleColor = '#f1f5f9';
    Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8';
    Chart.defaults.plugins.tooltip.borderColor = isDark ? '#334155' : '#1e293b';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }
});

// Add ripple keyframe
const style = document.createElement('style');
style.textContent = `@keyframes ripple { to { transform:scale(2.5); opacity:0; } }`;
document.head.appendChild(style);
