/* ============================================================================
   app.js — interaction layer
   ============================================================================
   Progressive enhancement only. Every behaviour here decorates markup that
   already works without it: filters submit as a plain form, the QR is rendered
   server-side, downloads are real links. If this file fails to load the portal
   is duller, not broken.
   ========================================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Toasts ─────────────────────────────────────────────────────────── */
  var ICONS = { success: '✅', error: '⛔', warning: '⚠️', info: 'ℹ️' };

  function toast(message, kind, ttl) {
    var host = document.querySelector('[data-toasts]');
    if (!host) return;

    kind = kind || 'info';
    var el = document.createElement('div');
    el.className = 'toast toast-' + kind;
    el.setAttribute('role', kind === 'error' ? 'alert' : 'status');

    var icon = document.createElement('span');
    icon.className = 'toast-icon';
    icon.textContent = ICONS[kind] || ICONS.info;

    var body = document.createElement('span');
    body.textContent = message;

    el.appendChild(icon);
    el.appendChild(body);
    host.appendChild(el);

    setTimeout(function () {
      el.classList.add('is-out');
      el.addEventListener('animationend', function () { el.remove(); });
      // Belt and braces: if animationend never fires, drop it anyway.
      setTimeout(function () { el.remove(); }, 600);
    }, ttl || 3600);
  }
  window.satyToast = toast;

  // Server-side flashes are rendered into the DOM as data payloads, then
  // replayed as toasts — one notification system instead of two.
  function replayFlashes() {
    var seeds = document.querySelectorAll('[data-flash]');
    for (var i = 0; i < seeds.length; i++) {
      var seed = seeds[i];
      toast(seed.getAttribute('data-flash'),
            seed.getAttribute('data-flash-kind') || 'info',
            5200);
      seed.remove();
    }
  }

  /* ── 3D pointer tilt ────────────────────────────────────────────────── */
  /* Writes --rx/--ry/--mx/--my on the card. The transform itself lives in
     CSS, so the same class works with JS disabled (just flat). */
  function bindTilt() {
    if (reduceMotion) return;
    // Pointer tilt on a touch screen fires once on tap and sticks — skip it.
    if (window.matchMedia && window.matchMedia('(hover: none)').matches) return;

    var cards = document.querySelectorAll('[data-tilt]');

    Array.prototype.forEach.call(cards, function (card) {
      var max = parseFloat(card.getAttribute('data-tilt')) || 7;
      var lift = card.getAttribute('data-tilt-lift');
      lift = lift === null ? 14 : parseFloat(lift);
      var frame = null;

      function apply(event) {
        var rect = card.getBoundingClientRect();
        var px = (event.clientX - rect.left) / rect.width;
        var py = (event.clientY - rect.top) / rect.height;

        card.style.setProperty('--ry', ((px - 0.5) * 2 * max).toFixed(2) + 'deg');
        card.style.setProperty('--rx', ((0.5 - py) * 2 * max).toFixed(2) + 'deg');
        card.style.setProperty('--mx', (px * 100).toFixed(1) + '%');
        card.style.setProperty('--my', (py * 100).toFixed(1) + '%');
      }

      card.addEventListener('pointermove', function (event) {
        if (frame) return;                       // one update per animation frame
        frame = requestAnimationFrame(function () {
          frame = null;
          apply(event);
        });
      });

      card.addEventListener('pointerenter', function () {
        card.classList.add('is-tilting');
        card.style.setProperty('--lift', lift + 'px');
      });

      card.addEventListener('pointerleave', function () {
        card.classList.remove('is-tilting');
        card.style.setProperty('--rx', '0deg');
        card.style.setProperty('--ry', '0deg');
        card.style.setProperty('--lift', '0px');
      });
    });
  }

  /* ── QR parallax ────────────────────────────────────────────────────── */
  function bindQrParallax() {
    if (reduceMotion) return;
    var stages = document.querySelectorAll('[data-qr-stage]');

    Array.prototype.forEach.call(stages, function (stage) {
      var card = stage.querySelector('.qr-float');
      if (!card) return;

      stage.addEventListener('pointermove', function (event) {
        var rect = stage.getBoundingClientRect();
        var px = (event.clientX - rect.left) / rect.width - 0.5;
        var py = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty('--qy', (px * 26).toFixed(2) + 'deg');
        card.style.setProperty('--qx', (-py * 20).toFixed(2) + 'deg');
      });

      stage.addEventListener('pointerleave', function () {
        card.style.setProperty('--qx', '0deg');
        card.style.setProperty('--qy', '0deg');
      });
    });
  }

  /* ── Odometer counters ──────────────────────────────────────────────── */
  /* Builds a digit strip per column and slides each one to its target, so the
     numbers roll up like a mechanical counter rather than just appearing. */
  function bindCounters() {
    var nodes = document.querySelectorAll('[data-count]');

    Array.prototype.forEach.call(nodes, function (node) {
      var target = parseInt(node.getAttribute('data-count'), 10);
      if (isNaN(target)) return;

      if (reduceMotion) { node.textContent = String(target); return; }

      var digits = String(target).split('');
      node.textContent = '';
      var wrap = document.createElement('span');
      wrap.className = 'odo';

      digits.forEach(function (digit, index) {
        var col = document.createElement('span');
        col.className = 'odo-col';

        var strip = document.createElement('span');
        strip.className = 'odo-strip';
        // 0-9 stacked vertically, plus a lead-in run so single digits still move.
        strip.textContent = '0123456789'.split('').join('\n');
        strip.style.whiteSpace = 'pre';
        strip.style.lineHeight = '1';

        col.appendChild(strip);
        wrap.appendChild(col);

        // Stagger the columns so the roll cascades left to right.
        setTimeout(function () {
          strip.style.setProperty('--to', '-' + (parseInt(digit, 10) * 1) + 'em');
        }, 90 + index * 110);
      });

      node.appendChild(wrap);
    });
  }

  /* ── Validity bars ──────────────────────────────────────────────────── */
  function bindLifeBars() {
    var bars = document.querySelectorAll('[data-life]');
    Array.prototype.forEach.call(bars, function (bar) {
      var pct = Math.max(0, Math.min(100, parseFloat(bar.getAttribute('data-life')) || 0));
      var fill = bar.querySelector('i');
      if (!fill) return;
      // Next frame, so the transition has a 0 -> pct change to animate.
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { fill.style.width = pct + '%'; });
      });
    });
  }

  /* ── Copy to clipboard ──────────────────────────────────────────────── */
  function bindCopy() {
    document.addEventListener('click', function (event) {
      var trigger = event.target.closest('[data-copy]');
      if (!trigger) return;
      event.preventDefault();

      var text = trigger.getAttribute('data-copy');
      var label = trigger.getAttribute('data-copy-label') || 'Copied to clipboard';

      function done() { toast(label, 'success', 2400); }
      function fail() { toast('Could not copy — select the text manually.', 'error'); }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, fail);
        return;
      }

      // http://localhost has no clipboard API in some browsers; fall back.
      try {
        var scratch = document.createElement('textarea');
        scratch.value = text;
        scratch.setAttribute('readonly', '');
        scratch.style.position = 'fixed';
        scratch.style.opacity = '0';
        document.body.appendChild(scratch);
        scratch.select();
        document.execCommand('copy');
        scratch.remove();
        done();
      } catch (err) {
        fail();
      }
    });
  }

  /* ── Flip cards ─────────────────────────────────────────────────────── */
  function bindFlip() {
    document.addEventListener('click', function (event) {
      var trigger = event.target.closest('[data-flip]');
      if (!trigger) return;

      var card = document.querySelector(trigger.getAttribute('data-flip'));
      if (!card) return;

      event.preventDefault();
      var open = card.classList.toggle('is-flipped');
      trigger.setAttribute('aria-pressed', open ? 'true' : 'false');

      var swap = trigger.getAttribute('data-flip-label');
      if (swap) {
        var current = trigger.querySelector('[data-flip-text]');
        if (current) {
          var previous = current.textContent;
          current.textContent = swap;
          trigger.setAttribute('data-flip-label', previous);
        }
      }
    });
  }

  /* ── Modal ──────────────────────────────────────────────────────────── */
  function bindModal() {
    function close(modal) {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
    }

    document.addEventListener('click', function (event) {
      var opener = event.target.closest('[data-modal-open]');
      if (opener) {
        var modal = document.querySelector(opener.getAttribute('data-modal-open'));
        if (modal) {
          event.preventDefault();
          modal.classList.add('is-open');
          modal.setAttribute('aria-hidden', 'false');
          var focusable = modal.querySelector('[data-modal-focus], .modal-close');
          if (focusable) focusable.focus();
        }
        return;
      }

      var closer = event.target.closest('[data-modal-close]');
      if (closer) {
        var owner = closer.closest('.modal');
        if (owner) { event.preventDefault(); close(owner); }
        return;
      }

      // Backdrop click.
      if (event.target.classList && event.target.classList.contains('modal')) {
        close(event.target);
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      var open = document.querySelector('.modal.is-open');
      if (open) close(open);
    });
  }

  /* ── Dynamic QR refresh ─────────────────────────────────────────────── */
  /* The token dies after 60s. Rather than let an employer scan a dead code,
     the page counts down and pulls a fresh payload just before expiry. */
  function bindQrRefresh() {
    var stage = document.querySelector('[data-qr-refresh]');
    if (!stage || stage.hasAttribute('data-qr-permanent') || !stage.getAttribute('data-qr-refresh')) return;

    var endpoint = stage.getAttribute('data-qr-refresh');
    var ttl = parseInt(stage.getAttribute('data-qr-ttl'), 10) || 60;
    // Page-wide: the enlarged QR inside the modal has to stay live too.
    var images = document.querySelectorAll('[data-qr-image]');
    var pill = document.querySelector('[data-qr-ttl-label]');
    var bar = document.querySelector('[data-qr-bar]');
    var linkTargets = document.querySelectorAll('[data-qr-link]');

    var remaining = ttl;
    var fetching = false;

    function paint() {
      if (pill) {
        pill.textContent = remaining > 0 ? remaining + 's' : 'refreshing…';
        var owner = pill.closest('.qr-ttl');
        if (owner) {
          owner.classList.toggle('is-low', remaining <= 15 && remaining > 0);
          owner.classList.toggle('is-dead', remaining <= 0);
        }
      }
      if (bar) {
        var fill = bar.querySelector('i');
        if (fill) fill.style.width = Math.max(0, (remaining / ttl) * 100) + '%';
        bar.classList.toggle('is-low', remaining <= 15);
      }
    }

    function refresh() {
      if (fetching) return;
      fetching = true;

      fetch(endpoint, { headers: { 'Accept': 'application/json' }, credentials: 'same-origin' })
        .then(function (response) {
          if (!response.ok) throw new Error('HTTP ' + response.status);
          return response.json();
        })
        .then(function (data) {
          if (data.image) {
            Array.prototype.forEach.call(images, function (img) { img.src = data.image; });
          }
          if (data.url) {
            Array.prototype.forEach.call(linkTargets, function (node) {
              if (node.tagName === 'A') node.href = data.url;
              if (node.hasAttribute('data-copy')) node.setAttribute('data-copy', data.url);
              if (node.hasAttribute('value')) node.value = data.url;
            });
          }
          ttl = data.ttl || ttl;
          remaining = ttl;
          fetching = false;
          paint();

          // Re-trigger the sweep so the code visibly "re-arms".
          var scan = stage.querySelector('.qr-scan');
          if (scan) {
            scan.style.animation = 'none';
            void scan.offsetWidth;              // force reflow
            scan.style.animation = '';
          }
        })
        .catch(function () {
          // A refresh failure is not fatal: the session may have timed out, in
          // which case the next navigation lands on the login page anyway.
          fetching = false;
          remaining = ttl;
          paint();
          if (pill) pill.textContent = 'stale';
        });
    }

    paint();

    setInterval(function () {
      remaining -= 1;
      // Pull the new code a beat early so there is never a dead window.
      if (remaining <= 2) refresh();
      else paint();
    }, 1000);

    // Manual re-roll.
    var button = document.querySelector('[data-qr-now]');
    if (button) {
      button.addEventListener('click', function (event) {
        event.preventDefault();
        refresh();
        toast('Fresh QR code generated — valid for ' + ttl + ' seconds.', 'success', 2600);
      });
    }
  }

  /* ── Session countdown ──────────────────────────────────────────────── */
  /* Mirrors the server's sliding idle timeout. Purely informational — the
     server is what actually enforces it. */
  function bindSessionClock() {
    var pill = document.querySelector('[data-session]');
    if (!pill) return;

    var remaining = parseInt(pill.getAttribute('data-session'), 10);
    if (isNaN(remaining)) return;

    var label = pill.querySelector('[data-session-label]');
    var warned = false;

    function paint() {
      var minutes = Math.floor(Math.max(0, remaining) / 60);
      var seconds = Math.max(0, remaining) % 60;
      if (label) label.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;

      var low = remaining <= 60;
      pill.classList.toggle('is-warning', low);
      if (low && !warned) {
        warned = true;
        toast('Session expires in a minute — any click keeps you signed in.', 'warning', 6000);
      }
    }

    paint();
    setInterval(function () {
      remaining -= 1;
      paint();
      if (remaining <= -2) window.location.reload();   // let the server log us out
    }, 1000);
  }

  /* ── Chain integrity probe ──────────────────────────────────────────── */
  function bindChainCheck() {
    var button = document.querySelector('[data-chain-check]');
    if (!button) return;

    button.addEventListener('click', function (event) {
      event.preventDefault();
      var original = button.textContent;
      button.textContent = 'Verifying…';
      button.classList.add('is-disabled');

      fetch(button.getAttribute('data-chain-check'), { credentials: 'same-origin' })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          toast(data.ok
            ? 'Chain intact — ' + data.blocks + ' blocks verified.'
            : 'Chain problem: ' + data.message, data.ok ? 'success' : 'error', 5000);
        })
        .catch(function () { toast('Could not reach the ledger.', 'error'); })
        .finally(function () {
          button.textContent = original;
          button.classList.remove('is-disabled');
        });
    });
  }

  /* ── Filter auto-submit ─────────────────────────────────────────────── */
  function bindFilters() {
    var form = document.querySelector('[data-filter-form]');
    if (!form) return;

    // Selects apply immediately; the text search waits for a pause in typing.
    Array.prototype.forEach.call(form.querySelectorAll('select'), function (select) {
      select.addEventListener('change', function () { form.submit(); });
    });

    var search = form.querySelector('input[type="search"], input[name="q"]');
    if (search) {
      var timer = null;
      search.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () { form.submit(); }, 480);
      });
    }
  }

  /* ── Nav toggle ─────────────────────────────────────────────────────── */
  function bindNav() {
    var toggle = document.querySelector('[data-nav-toggle]');
    var links = document.querySelector('[data-nav-links]');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ── Stagger entrance ───────────────────────────────────────────────── */
  function bindStagger() {
    var groups = document.querySelectorAll('[data-stagger]');
    Array.prototype.forEach.call(groups, function (group) {
      var children = group.children;
      for (var i = 0; i < children.length; i++) {
        children[i].classList.add('rise');
        children[i].style.setProperty('--i', i);
      }
    });
  }

  /* ── Demo credential autofill ───────────────────────────────────────── */
  function bindDemoFill() {
    document.addEventListener('click', function (event) {
      var row = event.target.closest('[data-fill]');
      if (!row) return;
      event.preventDefault();

      var form = document.querySelector('[data-login-form]');
      if (!form) return;

      var identifier = form.querySelector('[name="identifier"]');
      var password = form.querySelector('[name="password"]');
      if (!identifier || !password) return;

      identifier.value = row.getAttribute('data-fill');
      password.value = row.getAttribute('data-fill-password') || '';
      identifier.focus();
      toast('Filled in — press Sign in.', 'info', 2200);
    });
  }

  /* ── Stamp plate fit ────────────────────────────────────────────────── */
  /* Only the browser knows the rendered box of a `object-fit: contain` image,
     so hand the plate the image's intrinsic ratio and let CSS letterbox it the
     same way. Without this the stamp is anchored to the frame and drifts onto
     the mat beside the page whenever the two boxes differ — most visibly on
     narrow screens. No JS means no ratio, no `.is-fitted`, frame anchoring. */
  function bindPlateFit() {
    var plates = document.querySelectorAll('[data-plate]');

    Array.prototype.forEach.call(plates, function (plate) {
      var image = plate.querySelector('[data-plate-image]');
      if (!image) return;

      function fit() {
        if (!image.naturalWidth || !image.naturalHeight) return;
        plate.style.setProperty('--plate-ar',
                                image.naturalWidth + ' / ' + image.naturalHeight);
        plate.classList.add('is-fitted');
      }

      if (image.complete) fit();
      else image.addEventListener('load', fit);
    });
  }

  /* ── Boot ───────────────────────────────────────────────────────────── */
  function boot() {
    replayFlashes();
    bindTilt();
    bindQrParallax();
    bindCounters();
    bindLifeBars();
    bindCopy();
    bindFlip();
    bindModal();
    bindQrRefresh();
    bindSessionClock();
    bindChainCheck();
    bindFilters();
    bindNav();
    bindStagger();
    bindDemoFill();
    bindPlateFit();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
