/**
 * tilt3d.js — Silky-smooth 3D Parallax Tilt with Iridescent Holographic Foil
 *
 * Automatically applies 3D perspective tilt to cards across all Satyameva pages:
 * - Dynamic light angle calculations generating iridescent spectral interference
 * - Mobile gyroscope / deviceorientation tracking for hand-held physical tilt
 * - Multi-layer depth parallax (`.depth-1`, `.depth-2`, `.holo-seal-3d`)
 * - Respects prefers-reduced-motion
 */
(function() {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  function initTiltCard(card) {
    if (card._hasTilt) return;
    card._hasTilt = true;

    card.classList.add('tilt-card-3d');

    // Add specular glare & holographic foil layers if missing
    var glare = card.querySelector('.tilt-glare');
    if (!glare) {
      glare = document.createElement('div');
      glare.className = 'tilt-glare';
      card.appendChild(glare);
    }

    var holoSheen = card.querySelector('.tilt-holo-sheen');
    if (!holoSheen) {
      holoSheen = document.createElement('div');
      holoSheen.className = 'tilt-holo-sheen';
      card.appendChild(holoSheen);
    }

    var rect = null;
    var width = 0;
    var height = 0;
    var targetRotX = 0;
    var targetRotY = 0;
    var currentRotX = 0;
    var currentRotY = 0;
    var animFrame = null;
    var isHovered = false;

    function updateCardTransform() {
      // Smooth lerp
      currentRotX += (targetRotX - currentRotX) * 0.15;
      currentRotY += (targetRotY - currentRotY) * 0.15;

      var absDelta = Math.abs(targetRotX - currentRotX) + Math.abs(targetRotY - currentRotY);

      card.style.transform = 'perspective(900px) rotateX(' + currentRotX.toFixed(2) + 'deg) rotateY(' + currentRotY.toFixed(2) + 'deg) translateZ(' + (isHovered ? 8 : 0) + 'px)';

      if (isHovered || absDelta > 0.05) {
        animFrame = requestAnimationFrame(updateCardTransform);
      } else {
        card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        animFrame = null;
      }
    }

    card.addEventListener('mouseenter', function() {
      rect = card.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      isHovered = true;
      if (!animFrame) animFrame = requestAnimationFrame(updateCardTransform);
    });

    card.addEventListener('mousemove', function(e) {
      if (!rect) {
        rect = card.getBoundingClientRect();
        width = rect.width;
        height = rect.height;
      }

      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;

      var px = (x / width) * 100;
      var py = (y / height) * 100;

      // Max tilt: 8.5 degrees
      targetRotY = ((x - width / 2) / (width / 2)) * 8.5;
      targetRotX = -((y - height / 2) / (height / 2)) * 8.5;

      // Calculate holographic iridescent diffraction angle
      var angle = Math.atan2(y - height / 2, x - width / 2) * (180 / Math.PI) + 180;

      card.style.setProperty('--glare-x', px.toFixed(1) + '%');
      card.style.setProperty('--glare-y', py.toFixed(1) + '%');
      card.style.setProperty('--holo-angle', angle.toFixed(1) + 'deg');
      card.style.setProperty('--holo-x', px.toFixed(1) + '%');
      card.style.setProperty('--holo-y', py.toFixed(1) + '%');
    });

    card.addEventListener('mouseleave', function() {
      isHovered = false;
      targetRotX = 0;
      targetRotY = 0;
      rect = null;
    });
  }

  function applyTiltToAll() {
    var targets = document.querySelectorAll('.card, .card3d, .doc, .doc-card, .stat, [data-tilt-3d]');
    for (var i = 0; i < targets.length; i++) {
      initTiltCard(targets[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyTiltToAll);
  } else {
    applyTiltToAll();
  }

  // Observe dynamically added cards
  if ('MutationObserver' in window) {
    var observer = new MutationObserver(function() {
      applyTiltToAll();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Mobile Device Orientation / Gyroscope Support
  if (window.DeviceOrientationEvent && window.matchMedia('(hover: none)').matches) {
    var cards = [];
    var lastGamma = 0;
    var lastBeta = 0;

    window.addEventListener('deviceorientation', function(e) {
      var gamma = e.gamma; // [-90, 90] left to right
      var beta = e.beta;   // [-180, 180] front to back
      if (gamma === null || beta === null) return;

      // Damped tilt
      var tiltY = Math.max(-10, Math.min(10, gamma * 0.35));
      var tiltX = Math.max(-10, Math.min(10, (beta - 45) * 0.35));

      if (Math.abs(tiltY - lastGamma) > 0.5 || Math.abs(tiltX - lastBeta) > 0.5) {
        lastGamma = tiltY;
        lastBeta = tiltX;

        var visibleCards = document.querySelectorAll('.card3d, .doc-card, .holo-seal-3d');
        for (var c = 0; c < visibleCards.length; c++) {
          var el = visibleCards[c];
          el.style.transform = 'perspective(800px) rotateX(' + tiltX.toFixed(1) + 'deg) rotateY(' + tiltY.toFixed(1) + 'deg)';
        }
      }
    }, { passive: true });
  }
})();
