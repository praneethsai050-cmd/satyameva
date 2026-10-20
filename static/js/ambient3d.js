/**
 * ambient3d.js — Deep Space Cryptographic Constellation for Satyameva
 *
 * Implements an immersive, high-performance 3D interstellar space environment:
 * - 3 distinct depth layers of twinkling starfield particles
 * - Interstellar cosmic dust clouds
 * - Cryptographic constellation lines connecting nearby nodes
 * - Magnetic & gravitational physics interacting with cursor motion
 * - Dynamic color adaptation matching active Jaypee university campus
 * - 60fps performance optimization: mobile particle throttling & visibility culling
 */
(function() {
  'use strict';

  if (!window.THREE) return;

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent || ''
  );

  // Remove existing canvas if present
  var oldCanvas = document.getElementById('ambient3d-canvas');
  if (oldCanvas) oldCanvas.remove();

  var canvas = document.createElement('canvas');
  canvas.id = 'ambient3d-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '0';
  canvas.style.opacity = '0.75';

  document.body.insertBefore(canvas, document.body.firstChild);

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 2000);
  camera.position.z = 350;

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: !isMobile,
      powerPreference: 'low-power'
    });
  } catch (err) {
    return;
  }

  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(isMobile ? 1 : Math.min(window.devicePixelRatio || 1, 1.5));

  // Determine campus theme color palette
  var campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();
  var primaryColor = 0x2f6bed;   // Electric Blue
  var accentColor  = 0x00f2fe;   // Cyber Cyan
  var dustColor    = 0x1e3a8a;   // Deep Navy

  if (campus === 'juit') {
    primaryColor = 0x059669;     // JUIT Pine Green
    accentColor  = 0x10b981;     // Emerald Aurora
    dustColor    = 0x064e3b;     // Deep Forest
  } else if (campus === 'juet') {
    primaryColor = 0xd97706;     // JUET Amber Gold
    accentColor  = 0xfbbf24;     // Solar Flare
    dustColor    = 0x78350f;     // Deep Bronze
  }

  // ── Layer 1: Distant Twinkling Starfield ─────────────────────────────────────
  var starCount = isMobile ? 220 : 650;
  var starGeo = new THREE.BufferGeometry();
  var starPos = new Float32Array(starCount * 3);
  var starColors = new Float32Array(starCount * 3);

  var cPrim = new THREE.Color(primaryColor);
  var cAcc = new THREE.Color(accentColor);
  var cWhite = new THREE.Color(0xffffff);

  for (var i = 0; i < starCount; i++) {
    starPos[i * 3]     = (Math.random() - 0.5) * 1400;
    starPos[i * 3 + 1] = (Math.random() - 0.5) * 1000;
    starPos[i * 3 + 2] = (Math.random() - 0.5) * 600 - 150;

    var pick = Math.random();
    var color = pick > 0.6 ? cAcc : (pick > 0.3 ? cPrim : cWhite);
    starColors[i * 3]     = color.r;
    starColors[i * 3 + 1] = color.g;
    starColors[i * 3 + 2] = color.b;
  }

  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

  var starMat = new THREE.PointsMaterial({
    size: 2.8,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
  });

  var starSystem = new THREE.Points(starGeo, starMat);
  scene.add(starSystem);

  // ── Layer 2: Interactive Cryptographic Node Network ─────────────────────────
  var nodeCount = isMobile ? 28 : 65;
  var nodes = [];
  var nodePositions = [];

  for (var nIdx = 0; nIdx < nodeCount; nIdx++) {
    var x = (Math.random() - 0.5) * 700;
    var y = (Math.random() - 0.5) * 500;
    var z = (Math.random() - 0.5) * 250;
    nodes.push({
      x: x, y: y, z: z,
      originX: x, originY: y,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
    });
    nodePositions.push(x, y, z);
  }

  var nodeGeo = new THREE.BufferGeometry();
  nodeGeo.setAttribute('position', new THREE.Float32BufferAttribute(nodePositions, 3));

  var nodeMat = new THREE.PointsMaterial({
    color: accentColor,
    size: 6.5,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
  });

  var nodeSystem = new THREE.Points(nodeGeo, nodeMat);
  scene.add(nodeSystem);

  // Dynamic constellation laser lines between close nodes
  var maxLines = isMobile ? 45 : 110;
  var linePositions = new Float32Array(maxLines * 6);
  var lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));

  var lineMat = new THREE.LineBasicMaterial({
    color: primaryColor,
    transparent: true,
    opacity: 0.28,
    blending: THREE.AdditiveBlending,
  });

  var lineMesh = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lineMesh);

  // ── Layer 3: Floating Cosmic Dust Nebula ─────────────────────────────────────
  var dustCount = isMobile ? 25 : 80;
  var dustGeo = new THREE.BufferGeometry();
  var dustPos = new Float32Array(dustCount * 3);

  for (var dIdx = 0; dIdx < dustCount; dIdx++) {
    dustPos[dIdx * 3]     = (Math.random() - 0.5) * 800;
    dustPos[dIdx * 3 + 1] = (Math.random() - 0.5) * 600;
    dustPos[dIdx * 3 + 2] = (Math.random() - 0.5) * 200 - 80;
  }

  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  var dustMat = new THREE.PointsMaterial({
    color: dustColor,
    size: 18,
    transparent: true,
    opacity: 0.22,
    blending: THREE.AdditiveBlending,
  });
  var dustMesh = new THREE.Points(dustGeo, dustMat);
  scene.add(dustMesh);

  // ── Physics & Magnetic Cursor Tracking ──────────────────────────────────────
  var mouseWorldX = 0;
  var mouseWorldY = 0;
  var cursorActive = false;

  window.addEventListener('mousemove', function(e) {
    var normX = (e.clientX / window.innerWidth) * 2 - 1;
    var normY = -(e.clientY / window.innerHeight) * 2 + 1;
    mouseWorldX = normX * 320;
    mouseWorldY = normY * 240;
    cursorActive = true;
  }, { passive: true });

  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  var isVisible = true;
  var frameId = null;

  document.addEventListener('visibilitychange', function() {
    isVisible = !document.hidden;
    if (isVisible && !frameId) animate();
  });

  // ── Animation Loop ──────────────────────────────────────────────────────────
  function animate() {
    if (!isVisible) {
      frameId = null;
      return;
    }
    frameId = requestAnimationFrame(animate);

    // Slow orbital rotation of the deep starfield
    starSystem.rotation.y += 0.0004;
    starSystem.rotation.x += 0.00015;
    dustMesh.rotation.y   -= 0.0002;

    var nodePosArr = nodeGeo.attributes.position.array;
    var lineIdx = 0;
    var linePosArr = lineMesh.geometry.attributes.position.array;

    for (var i = 0; i < nodeCount; i++) {
      var n = nodes[i];

      // Drift physics
      n.x += n.vx;
      n.y += n.vy;

      // Gentle bounds bounce
      if (Math.abs(n.x - n.originX) > 40) n.vx *= -1;
      if (Math.abs(n.y - n.originY) > 40) n.vy *= -1;

      // Magnetic cursor attraction & dispersion
      if (cursorActive) {
        var dx = mouseWorldX - n.x;
        var dy = mouseWorldY - n.y;
        var dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 180 && dist > 10) {
          var force = (180 - dist) / 180;
          n.x += (dx / dist) * force * 1.6;
          n.y += (dy / dist) * force * 1.6;
        }
      }

      nodePosArr[i * 3]     = n.x;
      nodePosArr[i * 3 + 1] = n.y;
      nodePosArr[i * 3 + 2] = n.z;

      // Build dynamic constellation links
      for (var j = i + 1; j < nodeCount; j++) {
        if (lineIdx >= maxLines) break;
        var n2 = nodes[j];
        var ddx = n.x - n2.x;
        var ddy = n.y - n2.y;
        var dist2 = ddx * ddx + ddy * ddy;

        if (dist2 < 12500) { // ~110px distance
          linePosArr[lineIdx * 6]     = n.x;
          linePosArr[lineIdx * 6 + 1] = n.y;
          linePosArr[lineIdx * 6 + 2] = n.z;
          linePosArr[lineIdx * 6 + 3] = n2.x;
          linePosArr[lineIdx * 6 + 4] = n2.y;
          linePosArr[lineIdx * 6 + 5] = n2.z;
          lineIdx++;
        }
      }
    }

    // Zero out remaining line segments
    for (var k = lineIdx; k < maxLines; k++) {
      linePosArr[k * 6]     = 0;
      linePosArr[k * 6 + 1] = 0;
      linePosArr[k * 6 + 2] = 0;
      linePosArr[k * 6 + 3] = 0;
      linePosArr[k * 6 + 4] = 0;
      linePosArr[k * 6 + 5] = 0;
    }

    nodeGeo.attributes.position.needsUpdate = true;
    lineMesh.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  animate();
})();
