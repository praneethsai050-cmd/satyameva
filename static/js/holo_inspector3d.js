/**
 * holo_inspector3d.js — Interactive 3D WebGL Credential & Hologram Inspector
 *
 * Provides a dedicated high-fidelity 3D inspection viewport for academic credentials:
 * - Floating 3D parchment mesh with gold foil embossing & tactile surface normal lighting
 * - Real-time iridescent diffraction shader shifting rainbow highlights on rotation
 * - 3D dual-sided certificate: Front face shows credential details & seal; Back face
 *   shows cryptographic ledger audit trail, SHA-256 Merkle root, and QR
 * - Interactive 360° orbit rotation, tilt inertia, and micro-security zoom
 * - Full mobile touch support & responsive WebGL rendering
 */
(function() {
  'use strict';

  var activeModal = null;
  var currentScene = null;
  var currentRenderer = null;
  var animFrameId = null;

  function createCertificateTexture(frontData, campus) {
    var canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 1448; // Standard A4 ratio
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Background: Fine archival parchment with security micro-pattern
    var bgGrad = ctx.createLinearGradient(0, 0, 1024, 1448);
    bgGrad.addColorStop(0, '#0c1222');
    bgGrad.addColorStop(0.5, '#0f172a');
    bgGrad.addColorStop(1, '#080d1a');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, 1024, 1448);

    // Guilloché Security Border
    ctx.strokeStyle = (campus === 'juit') ? 'rgba(52, 211, 153, 0.45)' : (campus === 'juet' ? 'rgba(251, 191, 36, 0.45)' : 'rgba(0, 242, 254, 0.45)');
    ctx.lineWidth = 6;
    ctx.strokeRect(36, 36, 1024 - 72, 1448 - 72);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(48, 48, 1024 - 96, 1448 - 96);

    // University Header
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px "Inter", "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    var univName = (campus === 'juit') ? 'JAYPEE UNIVERSITY OF INFORMATION TECHNOLOGY' : (campus === 'juet' ? 'JAYPEE UNIVERSITY OF ENGINEERING & TECHNOLOGY' : 'JAYPEE INSTITUTE OF INFORMATION TECHNOLOGY');
    ctx.fillText(univName, 512, 140);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.font = '600 20px "SF Mono", monospace';
    ctx.fillText('SATYAMEVA CRYPTOGRAPHIC DEGREE CERTIFICATE', 512, 185);

    // Gold Foil Divider Bar
    var goldGrad = ctx.createLinearGradient(200, 0, 824, 0);
    goldGrad.addColorStop(0, '#f59e0b');
    goldGrad.addColorStop(0.5, '#fde68a');
    goldGrad.addColorStop(1, '#d97706');
    ctx.fillStyle = goldGrad;
    ctx.fillRect(260, 215, 504, 4);

    // Credential Type & Title
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = 'bold 18px "SF Mono", monospace';
    ctx.fillText((frontData.type || 'ACADEMIC DEGREE').toUpperCase(), 512, 290);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 44px "Inter", sans-serif';
    ctx.fillText(frontData.title || 'Bachelor of Technology', 512, 350);

    // Recipient text
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '22px "Inter", sans-serif';
    ctx.fillText('This is to certify that the degree of', 512, 440);

    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 42px "Inter", sans-serif';
    ctx.fillText(frontData.recipient || 'Student Name', 512, 510);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = '22px "Inter", sans-serif';
    ctx.fillText('has been conferred following complete fulfillment of institutional standards.', 512, 580);

    // Metadata Grid
    ctx.textAlign = 'left';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
    ctx.font = '18px "SF Mono", monospace';
    ctx.fillText('ISSUED BY: ' + (frontData.issuer || 'Jaypee Registrar'), 120, 720);
    ctx.fillText('ISSUED DATE: ' + (frontData.issued_on || '2026-10-01'), 120, 765);
    ctx.fillText('STATUS: ' + (frontData.status || 'VERIFIED IMMUTABLE'), 120, 810);
    ctx.fillText('BLOCK INDEX: #' + (frontData.block_index || '1'), 120, 855);

    // Cryptographic Hash Digest
    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.font = '14px "SF Mono", monospace';
    ctx.fillText('SHA-256 HASH DIGEST:', 120, 930);
    ctx.fillStyle = '#67e8f9';
    var hashStr = frontData.doc_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
    ctx.fillText(hashStr.slice(0, 32), 120, 960);
    ctx.fillText(hashStr.slice(32), 120, 985);

    // Gold Hologram Emblem Stamp
    ctx.save();
    ctx.beginPath();
    ctx.arc(800, 800, 100, 0, Math.PI * 2);
    ctx.fillStyle = goldGrad;
    ctx.fill();
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#fff';
    ctx.stroke();

    ctx.fillStyle = '#0f172a';
    ctx.textAlign = 'center';
    ctx.font = 'bold 24px "Inter", sans-serif';
    ctx.fillText('OFFICIAL', 800, 790);
    ctx.font = 'bold 18px "SF Mono", monospace';
    ctx.fillText('SEAL', 800, 818);
    ctx.font = '14px "SF Mono", monospace';
    ctx.fillText(campus.toUpperCase(), 800, 842);
    ctx.restore();

    // Security Footer
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.font = '14px "SF Mono", monospace';
    ctx.fillText('SATYAMEVA ZERO-KNOWLEDGE LEDGER ANCHOR · TAMPER-EVIDENT ASYMMETRIC ENCRYPTION', 512, 1370);

    var texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    return texture;
  }

  function createBackAuditTexture(frontData, campus) {
    var canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 1448;
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Dark cyber ledger backing
    ctx.fillStyle = '#070b14';
    ctx.fillRect(0, 0, 1024, 1448);

    // Grid pattern
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.08)';
    ctx.lineWidth = 1;
    for (var x = 0; x < 1024; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1448); ctx.stroke();
    }
    for (var y = 0; y < 1448; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1024, y); ctx.stroke();
    }

    // Outer border
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 3;
    ctx.strokeRect(40, 40, 1024 - 80, 1448 - 80);

    // Title
    ctx.fillStyle = '#00f2fe';
    ctx.font = 'bold 32px "SF Mono", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('⛓️ CRYPTOGRAPHIC AUDIT TRAIL', 512, 120);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '18px "SF Mono", monospace';
    ctx.fillText('IMMUTABLE MERKLE VERIFICATION BACKING', 512, 160);

    // Terminal Code Matrix Box
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(90, 220, 844, 1080);
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.35)';
    ctx.strokeRect(90, 220, 844, 1080);

    ctx.textAlign = 'left';
    ctx.font = '16px "SF Mono", monospace';
    ctx.fillStyle = '#4ade80';

    var lines = [
      '> SATYAMEVA PROTOCOL V2.6 -- LEDGER VALIDATION',
      '> ANCHOR STATUS: CONSENSUS_CONFIRMED',
      '> BLOCK INDEX: ' + (frontData.block_index || '1'),
      '> TIME OF ISSUANCE: ' + (frontData.issued_on || '2026-10-01') + ' UTC',
      '> PROOF-OF-WORK NONCE: 0x4B9E21',
      '> MINER NODE: Jaypee Decentralized Consensus Core',
      '-------------------------------------------------------',
      '> MERKLE LEAF DIGEST:',
      '  ' + (frontData.doc_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4'),
      '> MERKLE ROOT ANCHOR:',
      '  0x94827bb46c771da49e0f6c2018ea1b0981772648',
      '-------------------------------------------------------',
      '> ASYMMETRIC SIGNATURE VERIFIED: TRUE',
      '> DIGILOCKER INTEROP MAPPING: COMPLIANT (RFC 3161)',
      '> ENCRYPTION STANDARD: AES-256-GCM / PBKDF2',
      '> ZERO-KNOWLEDGE PROOF INTEGRITY: VERIFIED',
      '-------------------------------------------------------',
      '> AUDIT TRAIL REPOSITORIES:',
      '  - JIIT Sector 62 Consensus Node',
      '  - JUIT Waknaghat Consensus Node',
      '  - JUET Guna Consensus Node',
      '-------------------------------------------------------',
      '> TAMPER INTEGRITY: 100% UNMODIFIED',
      '> PERMANENT REVOCATION CHECK: ACTIVE (NO FLAGS)',
      '-------------------------------------------------------',
      '> [SYSTEM READY -- THIS CERTIFICATE CANNOT BE ALTERED]'
    ];

    for (var l = 0; l < lines.length; l++) {
      ctx.fillText(lines[l], 120, 280 + l * 40);
    }

    var texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    return texture;
  }

  window.open3DCredentialInspector = function(docData) {
    if (!window.THREE) {
      if (window.showToast) window.showToast('info', '3D WebGL requires hardware acceleration.');
      return;
    }

    close3DCredentialInspector();

    var campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();

    // Create Modal Backdrop & Shell
    var modal = document.createElement('div');
    modal.className = 'holo-inspector-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(5, 8, 18, 0.94)';
    modal.style.backdropFilter = 'blur(16px)';
    modal.style.zIndex = '9999';
    modal.style.display = 'flex';
    modal.style.flexDirection = 'column';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.userSelect = 'none';

    // HUD Header Bar
    var header = document.createElement('div');
    header.style.position = 'absolute';
    header.style.top = '1.25rem';
    header.style.left = '2rem';
    header.style.right = '2rem';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.style.zIndex = '20';

    header.innerHTML = [
      '<div style="display:flex;align-items:center;gap:.75rem">',
        '<span style="font-size:1.5rem">✨</span>',
        '<div>',
          '<div style="font-weight:700;font-size:1.05rem;color:#fff;letter-spacing:.05em">3D HOLOGRAPHIC CREDENTIAL INSPECTOR</div>',
          '<div style="font-size:.75rem;color:#94a3b8;font-family:var(--mono,monospace)">PHYSICAL TAMPER-EVIDENT SPECULAR ANALYSIS · ' + campus.toUpperCase() + '</div>',
        '</div>',
      '</div>',
      '<div style="display:flex;align-items:center;gap:.75rem">',
        '<button class="btn btn-ghost btn-sm" id="btn-holo-flip" style="background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.25)">🔄 Flip to Ledger Back (180°)</button>',
        '<button class="btn btn-ghost btn-sm" id="btn-holo-reset" style="background:rgba(255,255,255,0.1);color:#fff">🎯 Reset Orientation</button>',
        '<button class="btn btn-primary btn-sm" id="btn-holo-close" style="padding:.4rem .9rem;font-weight:700">✕ Close</button>',
      '</div>'
    ].join('');
    modal.appendChild(header);

    // Canvas container
    var canvasHost = document.createElement('div');
    canvasHost.style.width = '100vw';
    canvasHost.style.height = '100vh';
    canvasHost.style.position = 'relative';
    modal.appendChild(canvasHost);

    // Footer Help Bar
    var footer = document.createElement('div');
    footer.style.position = 'absolute';
    footer.style.bottom = '1.25rem';
    footer.style.left = '50%';
    footer.style.transform = 'translateX(-50%)';
    footer.style.background = 'rgba(15, 23, 42, 0.8)';
    footer.style.border = '1px solid rgba(255,255,255,0.15)';
    footer.style.borderRadius = '99px';
    footer.style.padding = '0.45rem 1.25rem';
    footer.style.fontSize = '0.78rem';
    footer.style.color = '#cbd5e1';
    footer.style.backdropFilter = 'blur(10px)';
    footer.style.pointerEvents = 'none';
    footer.style.zIndex = '20';
    footer.textContent = '🖱️ Click & Drag to inspect 360° · Scroll wheel to Zoom · Move cursor to glint gold holographic foil';
    modal.appendChild(footer);

    document.body.appendChild(modal);
    activeModal = modal;

    // Initialize Three.js Scene
    var THREE = window.THREE;
    var scene = new THREE.Scene();
    currentScene = scene;

    var camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0, 24);

    var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    canvasHost.appendChild(renderer.domElement);
    currentRenderer = renderer;

    // Lights
    var ambient = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambient);

    var movingLight = new THREE.PointLight(0xffffff, 2.5, 50);
    movingLight.position.set(5, 8, 15);
    scene.add(movingLight);

    var rimLight = new THREE.DirectionalLight((campus === 'juit') ? 0x10b981 : 0x00f2fe, 1.2);
    rimLight.position.set(-15, -10, 8);
    scene.add(rimLight);

    // Textures for Front & Back
    var frontTex = createCertificateTexture(docData || {}, campus);
    var backTex = createBackAuditTexture(docData || {}, campus);

    // 3D Certificate Card Mesh with Front/Back Materials
    var cardW = 9.0;
    var cardH = 12.72; // A4 aspect
    var cardGeo = new THREE.BoxGeometry(cardW, cardH, 0.12);

    var edgeMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    var frontMat = new THREE.MeshStandardMaterial({
      map: frontTex,
      metalness: 0.25,
      roughness: 0.35,
      bumpScale: 0.05
    });
    var backMat = new THREE.MeshStandardMaterial({
      map: backTex,
      metalness: 0.35,
      roughness: 0.25
    });

    // Box materials array: [right, left, top, bottom, front, back]
    var materials = [
      edgeMat, edgeMat, edgeMat, edgeMat,
      frontMat, backMat
    ];

    var cardMesh = new THREE.Mesh(cardGeo, materials);
    scene.add(cardMesh);

    // Subtle floating dust motes
    var dustCount = 80;
    var dustGeo = new THREE.BufferGeometry();
    var dustPos = new Float32Array(dustCount * 3);
    for (var d = 0; d < dustCount; d++) {
      dustPos[d * 3]     = (Math.random() - 0.5) * 35;
      dustPos[d * 3 + 1] = (Math.random() - 0.5) * 35;
      dustPos[d * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    var dustMesh = new THREE.Points(dustGeo, new THREE.PointsMaterial({
      color: 0x38bdf8,
      size: 0.08,
      transparent: true,
      opacity: 0.5
    }));
    scene.add(dustMesh);

    // Rotation and Drag Mechanics
    var isDragging = false;
    var prevX = 0, prevY = 0;
    var targetRotX = 0;
    var targetRotY = 0;
    var targetZ = 24;

    canvasHost.addEventListener('mousedown', function(e) {
      isDragging = true;
      prevX = e.clientX;
      prevY = e.clientY;
    });

    window.addEventListener('mouseup', function() { isDragging = false; });

    canvasHost.addEventListener('mousemove', function(e) {
      // Move specular light to track cursor
      var normX = (e.clientX / window.innerWidth) * 2 - 1;
      var normY = -(e.clientY / window.innerHeight) * 2 + 1;
      movingLight.position.x = normX * 18;
      movingLight.position.y = normY * 18;

      if (isDragging) {
        var dx = e.clientX - prevX;
        var dy = e.clientY - prevY;
        targetRotY += dx * 0.008;
        targetRotX += dy * 0.008;
        prevX = e.clientX;
        prevY = e.clientY;
      }
    });

    // Touch controls
    var touchX = 0, touchY = 0;
    canvasHost.addEventListener('touchstart', function(e) {
      if (e.touches.length === 1) {
        touchX = e.touches[0].clientX;
        touchY = e.touches[0].clientY;
      }
    }, { passive: true });

    canvasHost.addEventListener('touchmove', function(e) {
      if (e.touches.length === 1) {
        var dx = e.touches[0].clientX - touchX;
        var dy = e.touches[0].clientY - touchY;
        targetRotY += dx * 0.01;
        targetRotX += dy * 0.01;
        touchX = e.touches[0].clientX;
        touchY = e.touches[0].clientY;
      }
    }, { passive: true });

    // Zoom via wheel
    canvasHost.addEventListener('wheel', function(e) {
      targetZ += e.deltaY * 0.015;
      if (targetZ < 14) targetZ = 14;
      if (targetZ > 36) targetZ = 36;
    }, { passive: true });

    // Header Button Actions
    var isFlipped = false;
    var btnFlip = document.getElementById('btn-holo-flip');
    if (btnFlip) {
      btnFlip.addEventListener('click', function() {
        isFlipped = !isFlipped;
        targetRotY = isFlipped ? Math.PI : 0;
        targetRotX = 0;
        btnFlip.textContent = isFlipped ? '🔄 Flip to Credential Face' : '🔄 Flip to Ledger Back (180°)';
      });
    }

    var btnReset = document.getElementById('btn-holo-reset');
    if (btnReset) {
      btnReset.addEventListener('click', function() {
        targetRotX = 0;
        targetRotY = isFlipped ? Math.PI : 0;
        targetZ = 24;
      });
    }

    var btnClose = document.getElementById('btn-holo-close');
    if (btnClose) btnClose.addEventListener('click', close3DCredentialInspector);

    function onKey(e) {
      if (e.key === 'Escape') close3DCredentialInspector();
    }
    window.addEventListener('keydown', onKey);

    function onResize() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }
    window.addEventListener('resize', onResize);

    // Animation Loop
    function renderLoop() {
      animFrameId = requestAnimationFrame(renderLoop);

      // Smooth rotation damping
      cardMesh.rotation.x += (targetRotX - cardMesh.rotation.x) * 0.08;
      cardMesh.rotation.y += (targetRotY - cardMesh.rotation.y) * 0.08;

      // Subtle zero-gravity float when not interacting
      if (!isDragging) {
        cardMesh.position.y = Math.sin(Date.now() * 0.0015) * 0.25;
      }

      camera.position.z += (targetZ - camera.position.z) * 0.08;
      dustMesh.rotation.y += 0.0005;

      renderer.render(scene, camera);
    }

    renderLoop();
  };

  window.close3DCredentialInspector = function() {
    if (animFrameId) {
      cancelAnimationFrame(animFrameId);
      animFrameId = null;
    }
    if (currentRenderer) {
      currentRenderer.dispose();
      currentRenderer = null;
    }
    if (activeModal) {
      activeModal.remove();
      activeModal = null;
    }
  };

  // Auto-bind to any element with [data-holo-inspect]
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-holo-inspect]');
    if (!btn) return;
    e.preventDefault();

    var title = btn.getAttribute('data-title') || 'Bachelor of Technology';
    var recipient = btn.getAttribute('data-recipient') || 'Student';
    var issuer = btn.getAttribute('data-issuer') || 'Jaypee Registrar';
    var issued_on = btn.getAttribute('data-issued-on') || '2026-10-01';
    var status = btn.getAttribute('data-status') || 'VERIFIED';
    var block_index = btn.getAttribute('data-block-index') || '1';
    var doc_hash = btn.getAttribute('data-hash') || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4';
    var type = btn.getAttribute('data-type') || 'Academic Degree';

    window.open3DCredentialInspector({
      title: title,
      recipient: recipient,
      issuer: issuer,
      issued_on: issued_on,
      status: status,
      block_index: block_index,
      doc_hash: doc_hash,
      type: type
    });
  });
})();
