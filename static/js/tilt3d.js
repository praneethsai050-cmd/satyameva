/**
 * tilt3d.js — Silky-smooth 3D Parallax Tilt with Dynamic Specular Glare
 *
 * Automatically applies 3D perspective tilt to cards across all Satyameva pages:
 * student dashboard document cards, verifier stats, and admin KPI grids.
 */
(function() {
  'use strict';

  // Check if device supports hover/fine pointer
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!window.matchMedia('(hover: hover)').matches) return;

  function initTiltCard(card) {
    if (card._hasTilt) return;
    card._hasTilt = true;

    card.classList.add('tilt-card-3d');

    // Add specular glare layer if not present
    let glare = card.querySelector('.tilt-glare');
    if (!glare) {
      glare = document.createElement('div');
      glare.className = 'tilt-glare';
      card.appendChild(glare);
    }

    let rect = null;
    let width = 0;
    let height = 0;

    card.addEventListener('mouseenter', function() {
      rect = card.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
    });

    card.addEventListener('mousemove', function(e) {
      if (!rect) {
        rect = card.getBoundingClientRect();
        width = rect.width;
        height = rect.height;
      }

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const px = (x / width) * 100;
      const py = (y / height) * 100;

      // Max tilt angle: 8 degrees
      const rotY = ((x - width / 2) / (width / 2)) * 7.5;
      const rotX = -((y - height / 2) / (height / 2)) * 7.5;

      card.style.transform = `perspective(850px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateZ(6px)`;
      card.style.setProperty('--glare-x', `${px.toFixed(1)}%`);
      card.style.setProperty('--glare-y', `${py.toFixed(1)}%`);
    });

    card.addEventListener('mouseleave', function() {
      card.style.transform = 'perspective(850px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
      rect = null;
    });
  }

  function applyTiltToAll() {
    const targets = document.querySelectorAll('.card, .card3d, .doc, .doc-card, .stat, [data-tilt-3d]');
    targets.forEach(initTiltCard);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyTiltToAll);
  } else {
    applyTiltToAll();
  }

  // Observe dynamically added cards
  const observer = new MutationObserver(function(mutations) {
    applyTiltToAll();
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
