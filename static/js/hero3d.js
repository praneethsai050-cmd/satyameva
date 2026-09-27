/* ============================================================================
   hero3d.js — the rotating 3D blockchain
   ============================================================================
   Renders a chain of linked blocks into any [data-hero3d] canvas.

   Everything here is optional decoration: if the CDN is blocked, Three.js
   never defines window.THREE, this module bails out early and the CSS-3D
   `.chain-fallback` chain that is already in the markup stays visible. The
   page is never broken by a missing script.
   ========================================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function init(canvas) {
    var THREE = window.THREE;
    if (!THREE || !canvas) return null;

    var host = canvas.parentElement || canvas;
    var width = host.clientWidth || 640;
    var height = host.clientHeight || 320;

    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas, alpha: true, antialias: true, powerPreference: 'low-power'
      });
    } catch (err) {
      // No WebGL (locked-down machine, software rendering disabled) — fall back.
      return null;
    }

    // Cap the device pixel ratio: a 3x retina buffer costs a lot of GPU for a
    // decorative background.
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height, false);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(0, 0.9, 11);
    camera.lookAt(0, 0, 0);

    // ---- Campus Palette & Lighting ----
    var campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();
    var primaryColor = 0x2f6bed; // JIIT Cyber Blue
    var secondaryColor = 0x00f2fe; // Cyan
    var edgeColor = 0x60a5fa;

    if (campus === 'juit') {
      primaryColor = 0x059669; // JUIT Pine Green
      secondaryColor = 0x34d399;
      edgeColor = 0x10b981;
    } else if (campus === 'juet') {
      primaryColor = 0xd97706; // JUET Amber Gold
      secondaryColor = 0xfbbf24;
      edgeColor = 0xf59e0b;
    }

    scene.add(new THREE.AmbientLight(0xffffff, 0.95));

    var key = new THREE.PointLight(secondaryColor, 2.2, 45);
    key.position.set(-3, 6, 8);
    scene.add(key);

    var rim = new THREE.PointLight(primaryColor, 1.8, 45);
    rim.position.set(8, -2, 6);
    scene.add(rim);

    var accent = new THREE.PointLight(0xffffff, 1.2, 35);
    accent.position.set(2, -4, 7);
    scene.add(accent);

    // ---- The chain (Side-aligned in foreground) ----
    var group = new THREE.Group();
    group.position.set(2.6, 0.2, 0.8); // Shifted right and forward into foreground
    scene.add(group);

    var COUNT = 5;
    var SPACING = 2.45;
    var blocks = [];

    var geometry = new THREE.BoxGeometry(1.55, 1.55, 1.55);
    var edgeGeometry = new THREE.EdgesGeometry(geometry);
    var innerGeometry = new THREE.BoxGeometry(0.72, 0.72, 0.72);

    for (var i = 0; i < COUNT; i++) {
      var t = i / (COUNT - 1);

      // Gradient transition across the blockchain sequence
      var blockColor = new THREE.Color(primaryColor).lerp(new THREE.Color(secondaryColor), t);

      // Glowing Crystalline Glass Material
      var material = new THREE.MeshStandardMaterial({
        color: blockColor,
        metalness: 0.15,
        roughness: 0.12,
        transparent: true,
        opacity: 0.76,
        emissive: blockColor,
        emissiveIntensity: 0.25
      });

      var mesh = new THREE.Mesh(geometry, material);
      mesh.position.x = (i - (COUNT - 1) / 2) * SPACING;
      mesh.position.y = Math.sin(i * 1.1) * 0.28;
      mesh.rotation.set(0.34, 0.62, 0.1);

      // Outer glowing edges
      var edges = new THREE.LineSegments(
        edgeGeometry,
        new THREE.LineBasicMaterial({ color: edgeColor, transparent: true, opacity: 0.85 })
      );
      mesh.add(edges);

      // Pulsing inner core wireframe cube
      var innerMaterial = new THREE.MeshBasicMaterial({
        color: secondaryColor,
        wireframe: true,
        transparent: true,
        opacity: 0.6
      });
      var innerMesh = new THREE.Mesh(innerGeometry, innerMaterial);
      mesh.add(innerMesh);

      // The verified head block glows in crisp emerald/cyan
      if (i === COUNT - 1) {
        material.color = new THREE.Color(0x34d399);
        material.emissive = new THREE.Color(0x059669);
        material.emissiveIntensity = 0.75;
      }

      group.add(mesh);
      blocks.push({ mesh: mesh, inner: innerMesh, phase: i * 0.85, baseY: mesh.position.y });
    }

    // ---- Links between blocks ----
    var links = [];
    for (var j = 0; j < COUNT - 1; j++) {
      var link = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, SPACING - 1.55, 8),
        new THREE.MeshBasicMaterial({ color: edgeColor, transparent: true, opacity: 0.75 })
      );
      link.rotation.z = Math.PI / 2;
      link.position.x = (j - (COUNT - 1) / 2 + 0.5) * SPACING;
      group.add(link);
      links.push({ mesh: link, a: j, b: j + 1 });
    }

    // ---- Dust motes for depth parallax ----
    var motes = null;
    var moteCount = 130;
    var positions = new Float32Array(moteCount * 3);
    for (var k = 0; k < moteCount; k++) {
      positions[k * 3]     = (Math.random() - 0.5) * 22;
      positions[k * 3 + 1] = (Math.random() - 0.5) * 12;
      positions[k * 3 + 2] = (Math.random() - 0.5) * 14 - 2;
    }
    var moteGeometry = new THREE.BufferGeometry();
    moteGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    motes = new THREE.Points(moteGeometry, new THREE.PointsMaterial({
      color: 0xaab4ff, size: 0.075, transparent: true, opacity: 0.5,
      sizeAttenuation: true
    }));
    scene.add(motes);

    // ---- Pointer parallax ----
    var pointer = { x: 0, y: 0 };
    var target = { x: 0, y: 0 };

    function onPointerMove(event) {
      var rect = host.getBoundingClientRect();
      target.x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
      target.y = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
    }
    function onPointerLeave() { target.x = 0; target.y = 0; }

    host.addEventListener('pointermove', onPointerMove);
    host.addEventListener('pointerleave', onPointerLeave);

    // ---- Resize ----
    var resizeTimer = null;
    function resize() {
      var w = host.clientWidth, h = host.clientHeight;
      if (!w || !h) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    function onResize() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 120);
    }
    window.addEventListener('resize', onResize);

    // ---- Loop ----
    var running = true;
    var frame = null;
    var start = performance.now();

    function render(now) {
      if (!running) return;
      var t = (now - start) / 1000;

      // Ease the pointer towards its target so motion never snaps.
      pointer.x += (target.x - pointer.x) * 0.055;
      pointer.y += (target.y - pointer.y) * 0.055;

      group.rotation.y = Math.sin(t * 0.22) * 0.4 + pointer.x * 0.36;
      group.rotation.x = -0.08 + pointer.y * 0.22;

      for (var i = 0; i < blocks.length; i++) {
        var b = blocks[i];
        b.mesh.position.y = b.baseY + Math.sin(t * 0.95 + b.phase) * 0.24;
        b.mesh.rotation.y += 0.0042;
        b.mesh.rotation.x += 0.0016;
        if (b.inner) {
          b.inner.rotation.y -= 0.012;
          b.inner.rotation.x += 0.008;
        }
      }

      // Links follow the two blocks they connect, so the chain never breaks.
      for (var j = 0; j < links.length; j++) {
        var l = links[j];
        l.mesh.position.y = (blocks[l.a].mesh.position.y + blocks[l.b].mesh.position.y) / 2;
      }

      motes.rotation.y = t * 0.018;
      motes.position.y = Math.sin(t * 0.28) * 0.35;

      renderer.render(scene, camera);
      frame = requestAnimationFrame(render);
    }

    // Pause when the tab is hidden — no point burning GPU on an unseen canvas.
    function onVisibility() {
      if (document.hidden) {
        running = false;
        if (frame) cancelAnimationFrame(frame);
      } else if (!running) {
        running = true;
        start = performance.now();
        frame = requestAnimationFrame(render);
      }
    }
    document.addEventListener('visibilitychange', onVisibility);

    resize();

    if (reduceMotion) {
      // Draw one static frame and stop: the visual is still there, the motion is not.
      renderer.render(scene, camera);
    } else {
      frame = requestAnimationFrame(render);
    }

    canvas.classList.add('is-ready');
    return { renderer: renderer };
  }

  function boot() {
    var canvases = document.querySelectorAll('[data-hero3d]');
    if (!canvases.length) return;
    for (var i = 0; i < canvases.length; i++) init(canvases[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
