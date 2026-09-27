/**
 * matrix_rain.js — Cryptographic Matrix Code Rain for Satyameva
 *
 * Renders falling cryptographic streams of SHA-256 hex characters (0-9, a-f)
 * and blockchain symbols with campus-tinted glowing heads and fading trails.
 */
(function() {
  'use strict';

  window.initMatrixRain = function(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = canvas.offsetWidth || window.innerWidth || 1920);
    let height = (canvas.height = canvas.offsetHeight || window.innerHeight || 1080);

    const campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();
    let headColor = '#ffffff';
    let trailColor = '#00f2fe';

    if (campus === 'juit') {
      trailColor = '#10b981'; // emerald
    } else if (campus === 'juet') {
      trailColor = '#fbbf24'; // amber gold
    }

    const characters = '0123456789ABCDEFabcdefλ§⬡⚡🔒01';
    const fontSize = 14;
    let columns = Math.floor(width / fontSize);
    let drops = [];

    function resetDrops() {
      columns = Math.floor(width / fontSize);
      drops = [];
      for (let i = 0; i < columns; i++) {
        drops[i] = Math.floor(Math.random() * -120);
      }
    }
    resetDrops();

    window.addEventListener('resize', function() {
      width = canvas.width = canvas.offsetWidth || window.innerWidth;
      height = canvas.height = canvas.offsetHeight || window.innerHeight;
      resetDrops();
    });

    let isVisible = true;
    document.addEventListener('visibilitychange', function() {
      isVisible = !document.hidden;
    });

    function draw() {
      if (!isVisible) return;

      // Alpha decay using destination-out to keep background 100% transparent
      // so the card and text underneath are never darkened or obscured
      ctx.globalCompositeOperation = 'destination-out';
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.fillRect(0, 0, width, height);

      // Render glowing characters in foreground
      ctx.globalCompositeOperation = 'source-over';
      ctx.font = `bold ${fontSize}px 'JetBrains Mono', monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = characters.charAt(Math.floor(Math.random() * characters.length));
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        // Bright white/cyan lead character
        ctx.fillStyle = headColor;
        ctx.shadowColor = trailColor;
        ctx.shadowBlur = 10;
        ctx.fillText(char, x, y);

        // Glowing neon trail
        if (drops[i] > 1) {
          ctx.fillStyle = trailColor;
          ctx.shadowBlur = 6;
          ctx.fillText(char, x, y - fontSize);
          ctx.shadowBlur = 0;
        }

        if (y > height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        drops[i]++;
      }
    }

    let interval = setInterval(draw, 45);
    canvas._matrixInterval = interval;
  };

  // Auto-init for any elements marked with data-matrix-rain
  document.addEventListener('DOMContentLoaded', function() {
    const canvases = document.querySelectorAll('[data-matrix-rain]');
    canvases.forEach(function(c) {
      if (c.id) window.initMatrixRain(c.id);
    });
  });
})();
