/**
 * ambient3d.js — Deep Space Cryptographic Constellation for Satyameva
 *
 * Implements an immersive, high-performance 3D interstellar space environment:
 * - 3 distinct depth layers of twinkling starfield particles
 * - Interstellar cosmic dust clouds
 * - Cryptographic constellation lines connecting nearby nodes
 * - Magnetic & gravitational physics interacting with cursor motion
 * - Dynamic color adaptation matching the active Jaypee university campus
 */
(function() {
  'use strict';

  if (!window.THREE) return;

  // Remove existing canvas if present
  const oldCanvas = document.getElementById('ambient3d-canvas');
  if (oldCanvas) oldCanvas.remove();

  const canvas = document.createElement('canvas');
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

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 2000);
  camera.position.z = 350;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

  // Determine campus theme color palette
  const campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();
  let primaryColor = 0x2f6bed;   // Electric Blue
  let accentColor  = 0x00f2fe;   // Cyber Cyan
  let dustColor    = 0x1e3a8a;   // Deep Navy

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
  const starCount = 650;
  const starGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(starCount * 3);
  const starColors = new Float32Array(starCount * 3);

  const cPrim = new THREE.Color(primaryColor);
  const cAcc = new THREE.Color(accentColor);
  const cWhite = new THREE.Color(0xffffff);

  for (let i = 0; i < starCount; i++) {
    starPos[i * 3]     = (Math.random() - 0.5) * 1400;
    starPos[i * 3 + 1] = (Math.random() - 0.5) * 1000;
    starPos[i * 3 + 2] = (Math.random() - 0.5) * 600 - 150;

    const pick = Math.random();
    const color = pick > 0.6 ? cAcc : (pick > 0.3 ? cPrim : cWhite);
    starColors[i * 3]     = color.r;
    starColors[i * 3 + 1] = color.g;
    starColors[i * 3 + 2] = color.b;
  }

  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

  const starMat = new THREE.PointsMaterial({
    size: 2.8,
    vertexColors: true,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
  });

  const starSystem = new THREE.Points(starGeo, starMat);
  scene.add(starSystem);

  // ── Layer 2: Interactive Cryptographic Node Network ─────────────────────────
  const nodeCount = 65;
  const nodes = [];
  const nodePositions = [];

  for (let i = 0; i < nodeCount; i++) {
    const x = (Math.random() - 0.5) * 700;
    const y = (Math.random() - 0.5) * 500;
    const z = (Math.random() - 0.5) * 250;
    nodes.push({
      x: x, y: y, z: z,
      originX: x, originY: y,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
    });
    nodePositions.push(x, y, z);
  }

  const nodeGeo = new THREE.BufferGeometry();
  nodeGeo.setAttribute('position', new THREE.Float32BufferAttribute(nodePositions, 3));

  const nodeMat = new THREE.PointsMaterial({
    color: accentColor,
    size: 6.5,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
  });

  const nodeSystem = new THREE.Points(nodeGeo, nodeMat);
  scene.add(nodeSystem);

  // Dynamic constellation laser lines between close nodes
  const maxLines = 110;
  const linePositions = new Float32Array(maxLines * 6);
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));

  const lineMat = new THREE.LineBasicMaterial({
    color: primaryColor,
    transparent: true,
    opacity: 0.28,
    blending: THREE.AdditiveBlending,
  });

  const lineMesh = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lineMesh);

  // ── Layer 3: Floating Cosmic Dust Nebula ─────────────────────────────────────
  const dustCount = 80;
  const dustGeo = new THREE.BufferGeometry();
  const dustPos = new Float32Array(dustCount * 3);

  for (let i = 0; i < dustCount; i++) {
    dustPos[i * 3]     = (Math.random() - 0.5) * 800;
    dustPos[i * 3 + 1] = (Math.random() - 0.5) * 600;
    dustPos[i * 3 + 2] = (Math.random() - 0.5) * 200 - 80;
  }

  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    color: dustColor,
    size: 18,
    transparent: true,
    opacity: 0.22,
    blending: THREE.AdditiveBlending,
  });
  const dustMesh = new THREE.Points(dustGeo, dustMat);
  scene.add(dustMesh);

  // ── Physics & Magnetic Cursor Tracking ──────────────────────────────────────
  let mouseWorldX = 0;
  let mouseWorldY = 0;
  let cursorActive = false;

  window.addEventListener('mousemove', function(e) {
    const normX = (e.clientX / window.innerWidth) * 2 - 1;
    const normY = -(e.clientY / window.innerHeight) * 2 + 1;
    mouseWorldX = normX * 320;
    mouseWorldY = normY * 240;
    cursorActive = true;
  }, { passive: true });

  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  let isVisible = true;
  document.addEventListener('visibilitychange', function() {
    isVisible = !document.hidden;
  });

  // ── Animation Loop ──────────────────────────────────────────────────────────
  function animate() {
    requestAnimationFrame(animate);
    if (!isVisible) return;

    // Slow orbital rotation of the deep starfield
    starSystem.rotation.y += 0.0004;
    starSystem.rotation.x += 0.00015;
    dustMesh.rotation.y   -= 0.0002;

    const nodePosArr = nodeGeo.attributes.position.array;
    let lineIdx = 0;
    const linePosArr = lineMesh.geometry.attributes.position.array;

    for (let i = 0; i < nodeCount; i++) {
      const n = nodes[i];

      // Drift physics
      n.x += n.vx;
      n.y += n.vy;

      // Gentle bounds bounce
      if (Math.abs(n.x - n.originX) > 40) n.vx *= -1;
      if (Math.abs(n.y - n.originY) > 40) n.vy *= -1;

      // Magnetic cursor attraction & dispersion
      if (cursorActive) {
        const dx = mouseWorldX - n.x;
        const dy = mouseWorldY - n.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 180 && dist > 10) {
          const force = (180 - dist) / 180;
          n.x += (dx / dist) * force * 1.6;
          n.y += (dy / dist) * force * 1.6;
        }
      }

      nodePosArr[i * 3]     = n.x;
      nodePosArr[i * 3 + 1] = n.y;
      nodePosArr[i * 3 + 2] = n.z;

      // Build dynamic constellation links
      for (let j = i + 1; j < nodeCount; j++) {
        if (lineIdx >= maxLines) break;
        const n2 = nodes[j];
        const ddx = n.x - n2.x;
        const ddy = n.y - n2.y;
        const dist2 = ddx * ddx + ddy * ddy;

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
    for (let k = lineIdx; k < maxLines; k++) {
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
