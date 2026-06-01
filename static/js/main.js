/* KRS Online — Jujutsu Kaisen Edition */

// ── Cursed energy particle system ─────────────────────────────
(function() {
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:0.35';
  document.body.prepend(canvas);

  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x  = Math.random() * W;
      this.y  = Math.random() * H + H;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = -(Math.random() * 0.8 + 0.3);
      this.life = 0;
      this.maxLife = Math.random() * 200 + 100;
      this.size = Math.random() * 2 + 0.5;
      const r = Math.random();
      this.color = r < 0.6 ? '#c1121f' : r < 0.85 ? '#f4a261' : '#7b2d8b';
    }
    update() {
      this.x += this.vx + Math.sin(this.life * 0.05) * 0.3;
      this.y += this.vy;
      this.life++;
      if (this.life > this.maxLife || this.y < -20) this.reset();
    }
    draw() {
      const alpha = Math.sin((this.life / this.maxLife) * Math.PI) * 0.6;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  for (let i = 0; i < 60; i++) {
    const p = new Particle();
    p.y = Math.random() * H;
    p.life = Math.random() * p.maxLife;
    particles.push(p);
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(); });
    ctx.globalAlpha = 1;
    requestAnimationFrame(animate);
  }
  animate();
})();

// ── Navbar scroll ───────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.navbar');
  if (nav) nav.style.borderBottomColor = window.scrollY > 20 ? 'rgba(193,18,31,0.4)' : 'rgba(193,18,31,0.2)';
});

// ── Card entrance animation ─────────────────────────────────────
const obs = new IntersectionObserver(entries => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      obs.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.feat-card, .kelas-card, .ag-card, .stat-card').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(16px)';
  el.style.transition = `opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s`;
  obs.observe(el);
});

// ── Counter animation ───────────────────────────────────────────
document.querySelectorAll('.ag-num, .sc-num').forEach(el => {
  const target = parseInt(el.textContent);
  if (isNaN(target) || target === 0) return;
  let cur = 0;
  const dur = 800, step = 16;
  const inc = target / (dur / step);
  const timer = setInterval(() => {
    cur = Math.min(cur + inc, target);
    el.textContent = Math.round(cur);
    if (cur >= target) clearInterval(timer);
  }, step);
});

// ── Cursed energy hover on kelas cards ─────────────────────────
document.querySelectorAll('.kelas-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width * 100).toFixed(1);
    const y = ((e.clientY - rect.top) / rect.height * 100).toFixed(1);
    card.style.setProperty('--mx', x + '%');
    card.style.setProperty('--my', y + '%');
  });
});

// ── Auto-dismiss alerts ─────────────────────────────────────────
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

document.addEventListener("DOMContentLoaded", function() {
    // Ambil semua link di navigasi
    const navLinks = document.querySelectorAll('.nav-links a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        // Jika URL cocok, tambahkan class active
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
        
        // Opsional: Klik untuk memindahkan aktif
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});