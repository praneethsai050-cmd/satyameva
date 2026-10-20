/**
 * blockchain3d.js — Interactive 3D WebGL Blockchain Ledger Explorer
 *
 * Implements a high-fidelity 3D crystalline blockchain ledger explorer:
 * - Raycast hover inspection with floating 3D HUD metadata tooltips
 * - Smooth camera navigation and block inspection
 * - Interactive "Simulate Live Block Mining" feature with particle convergence & laser lock-in
 * - Dynamic cryptographic data packets streaming along laser connections
 * - Backward-compatible `window.lockInBlock3D(blockIndex)` with vertical target lock beam
 * - 60fps performance optimization: mobile DPR clamping & IntersectionObserver culling
 */
(function() {
  'use strict';

  var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent || ''
  );

  window.initBlockchain3D = function(containerId) {
    var container = document.getElementById(containerId);
    if (!container || !window.THREE) return;

    // Clear existing canvas and controls if re-initializing
    var existingCanvas = container.querySelector('.blockchain-3d-canvas');
    if (existingCanvas) existingCanvas.remove();
    var existingHud = container.querySelector('.blockchain-3d-hud-card');
    if (existingHud) existingHud.remove();
    var existingControls = container.querySelector('.blockchain-3d-controls');
    if (existingControls) existingControls.remove();

    // Canvas creation
    var canvas = document.createElement('canvas');
    canvas.className = 'blockchain-3d-canvas';
    container.appendChild(canvas);

    var width = container.clientWidth || 800;
    var height = container.clientHeight || 380;

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(48, width / height, 0.1, 1000);
    var defaultCameraPos = new THREE.Vector3(0, 16, 68);
    var defaultCameraLook = new THREE.Vector3(0, 0, 0);
    camera.position.copy(defaultCameraPos);

    var targetCameraPos = defaultCameraPos.clone();
    var targetCameraLook = defaultCameraLook.clone();
    var currentCameraLook = defaultCameraLook.clone();

    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: !isMobile,
        powerPreference: 'low-power'
      });
    } catch (e) {
      return;
    }

    renderer.setSize(width, height);
    renderer.setPixelRatio(isMobile ? 1 : Math.min(window.devicePixelRatio || 1, 2));

    // Lighting
    var ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    var pointLight = new THREE.PointLight(0x00f2fe, 2.8, 180);
    pointLight.position.set(20, 35, 45);
    scene.add(pointLight);

    var fillLight = new THREE.PointLight(0x2f6bed, 1.8, 140);
    fillLight.position.set(-25, -15, 30);
    scene.add(fillLight);

    // Campus theming
    var campus = (document.body.getAttribute('data-campus') || 'jiit').toLowerCase();
    var blockColor = 0x2f6bed;
    var blockGlow  = 0x00f2fe;
    var themeHex   = '#00f2fe';

    if (campus === 'juit') {
      blockColor = 0x059669;
      blockGlow  = 0x34d399;
      themeHex   = '#34d399';
    } else if (campus === 'juet') {
      blockColor = 0xd97706;
      blockGlow  = 0xfbbf24;
      themeHex   = '#fbbf24';
    }

    var group = new THREE.Group();
    scene.add(group);

    var blockMeshes = [];
    var laserLines  = [];
    var streamPackets = [];
    var lockInBeamMesh = null;
    var shockwaveMesh = null;
    var miningParticles = null;

    var SPACING = 16;
    var chainData = [];

    // Floating 3D HUD Tooltip Card attached to container
    var hudCard = document.createElement('div');
    hudCard.className = 'blockchain-3d-hud-card';
    hudCard.style.position = 'absolute';
    hudCard.style.top = '1rem';
    hudCard.style.right = '1rem';
    hudCard.style.background = 'rgba(10, 16, 32, 0.92)';
    hudCard.style.border = '1px solid ' + themeHex;
    hudCard.style.borderRadius = '10px';
    hudCard.style.padding = '0.65rem 0.95rem';
    hudCard.style.fontFamily = 'var(--mono, monospace)';
    hudCard.style.fontSize = '0.72rem';
    hudCard.style.color = '#fff';
    hudCard.style.boxShadow = '0 8px 30px rgba(0,0,0,0.5), 0 0 15px rgba(0,242,254,0.2)';
    hudCard.style.backdropFilter = 'blur(10px)';
    hudCard.style.pointerEvents = 'none';
    hudCard.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    hudCard.style.opacity = '0';
    hudCard.style.zIndex = '15';
    container.appendChild(hudCard);

    // Interactive Floating Controls Toolbar
    var controlsDiv = document.createElement('div');
    controlsDiv.className = 'blockchain-3d-controls';
    controlsDiv.style.position = 'absolute';
    controlsDiv.style.bottom = '0.85rem';
    controlsDiv.style.left = '1rem';
    controlsDiv.style.display = 'flex';
    controlsDiv.style.gap = '0.5rem';
    controlsDiv.style.zIndex = '15';
    controlsDiv.innerHTML = [
      '<button class="btn btn-ghost btn-sm" id="btn-3d-mine" style="background:rgba(15,23,42,0.85);font-size:.72rem;padding:.3rem .65rem;border:1px solid ' + themeHex + '">⚡ Simulate POW Mining</button>',
      '<button class="btn btn-ghost btn-sm" id="btn-3d-focus" style="background:rgba(15,23,42,0.85);font-size:.72rem;padding:.3rem .65rem">🎯 Focus Head</button>',
      '<button class="btn btn-ghost btn-sm" id="btn-3d-reset" style="background:rgba(15,23,42,0.85);font-size:.72rem;padding:.3rem .65rem">🔄 Reset View</button>'
    ].join('');
    container.appendChild(controlsDiv);

    // Fetch live chain or fallback
    fetch('/blockchain/chain')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        var rawChain = (data && data.chain) ? data.chain : [];
        chainData = rawChain.length ? rawChain : [
          { index: 0, hash: '000000000019d6689c085ae165831e934ff763ae', proof: 100, timestamp: Date.now() / 1000 - 86400 },
          { index: 1, hash: '8f4a2b9015c9284d720b05b637d7a1286c91e32b', proof: 4082, timestamp: Date.now() / 1000 - 43200 },
          { index: 2, hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4', proof: 12903, timestamp: Date.now() / 1000 - 12000 },
          { index: 3, hash: '00000000000000000005a7690da0175b331ff3d8', proof: 98144, timestamp: Date.now() / 1000 }
        ];
        build3DChain(chainData);
      })
      .catch(function() {
        chainData = [
          { index: 0, hash: 'genesis_block_0', proof: 100, timestamp: Date.now() / 1000 }
        ];
        build3DChain(chainData);
      });

    var cubeGeo = new THREE.BoxGeometry(6, 6, 6);
    var edgeGeo = new THREE.EdgesGeometry(cubeGeo);
    var packetGeo = new THREE.SphereGeometry(0.5, 8, 8);

    function createBlockMesh(b, i, count) {
      var isGenesis = (i === 0);
      var isHead = (i === count - 1 && count > 1);

      var color = isGenesis ? 0x8b5cf6 : (isHead ? 0x10b981 : blockColor);
      var emissive = isGenesis ? 0x4c1d95 : (isHead ? 0x059669 : blockColor);

      var cubeMat = new THREE.MeshStandardMaterial({
        color: color,
        metalness: 0.85,
        roughness: 0.2,
        emissive: emissive,
        emissiveIntensity: isHead ? 0.75 : 0.38,
        transparent: true,
        opacity: 0.92
      });

      var cube = new THREE.Mesh(cubeGeo, cubeMat);
      var startX = -((count - 1) * SPACING) / 2;
      cube.position.set(startX + i * SPACING, Math.sin(i * 0.7) * 2, 0);

      cube.userData = {
        index: b.index !== undefined ? b.index : i,
        hash: b.hash || 'hash_block_' + i,
        proof: b.proof || Math.floor(Math.random() * 50000),
        timestamp: b.timestamp || (Date.now() / 1000),
        isGenesis: isGenesis,
        isHead: isHead,
        baseScale: 1.0,
        targetScale: 1.0
      };

      // Wireframe neon cage
      var edgeMat = new THREE.LineBasicMaterial({
        color: isGenesis ? 0xc084fc : (isHead ? 0x34d399 : blockGlow),
        linewidth: 2,
        transparent: true,
        opacity: 0.9
      });
      var wire = new THREE.LineSegments(edgeGeo, edgeMat);
      cube.add(wire);

      return cube;
    }

    function addLaserLink(prevCube, cube) {
      var points = [prevCube.position, cube.position];
      var lineGeo = new THREE.BufferGeometry().setFromPoints(points);
      var lineMat = new THREE.LineBasicMaterial({
        color: 0x00f2fe,
        transparent: true,
        opacity: 0.8,
        linewidth: 2
      });
      var laserLine = new THREE.Line(lineGeo, lineMat);
      group.add(laserLine);
      laserLines.push(laserLine);

      // Data pulse sphere on the laser
      var pMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95 });
      var packet = new THREE.Mesh(packetGeo, pMat);
      group.add(packet);
      streamPackets.push({
        mesh: packet,
        source: prevCube,
        target: cube,
        progress: Math.random()
      });
    }

    function build3DChain(chain) {
      // Clear existing block meshes & laser lines
      for (var m = 0; m < blockMeshes.length; m++) group.remove(blockMeshes[m]);
      for (var l = 0; l < laserLines.length; l++) group.remove(laserLines[l]);
      for (var p = 0; p < streamPackets.length; p++) group.remove(streamPackets[p].mesh);
      blockMeshes = [];
      laserLines = [];
      streamPackets = [];

      var count = Math.min(chain.length, 12);
      for (var i = 0; i < count; i++) {
        var b = chain[i] || { index: i, hash: 'block_' + i };
        var cube = createBlockMesh(b, i, count);
        group.add(cube);
        blockMeshes.push(cube);

        if (i > 0) {
          addLaserLink(blockMeshes[i - 1], cube);
        }
      }

      // Update badge text
      var badge = container.querySelector('.blockchain-3d-badge span:last-child');
      if (badge) {
        badge.textContent = 'Live Chain Verified: ' + count + ' Mined Blocks (' + campus.toUpperCase() + ')';
      }
    }

    // ── 3D Block Lock-In Functionality (Backward Compatible) ─────────────────────
    window.lockInBlock3D = function(blockIndex) {
      var idx = parseInt(blockIndex, 10);
      var target = null;
      for (var i = 0; i < blockMeshes.length; i++) {
        if (blockMeshes[i].userData.index === idx) {
          target = blockMeshes[i];
          break;
        }
      }
      if (!target && blockMeshes.length > 0) target = blockMeshes[0];
      if (!target) return;

      // Vertical lock-in laser beam
      if (lockInBeamMesh) group.remove(lockInBeamMesh);

      var beamGeo = new THREE.CylinderGeometry(0.35, 0.35, 70, 16);
      var beamMat = new THREE.MeshBasicMaterial({
        color: 0x00f2fe,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending
      });
      lockInBeamMesh = new THREE.Mesh(beamGeo, beamMat);
      lockInBeamMesh.position.copy(target.position);
      lockInBeamMesh.position.y += 35;
      group.add(lockInBeamMesh);

      // Expanding Shockwave ring
      if (shockwaveMesh) group.remove(shockwaveMesh);
      var ringGeo = new THREE.RingGeometry(0.5, 1.2, 32);
      var ringMat = new THREE.MeshBasicMaterial({
        color: 0x00f2fe,
        transparent: true,
        opacity: 1.0,
        side: THREE.DoubleSide
      });
      shockwaveMesh = new THREE.Mesh(ringGeo, ringMat);
      shockwaveMesh.rotation.x = Math.PI / 2;
      shockwaveMesh.position.copy(target.position);
      group.add(shockwaveMesh);

      // Emissive burst
      target.material.emissiveIntensity = 1.3;
      target.userData.targetScale = 1.3;
      setTimeout(function() {
        if (target && target.material) target.material.emissiveIntensity = 0.55;
        if (target) target.userData.targetScale = 1.0;
      }, 1400);

      // Glide camera smoothly to target
      focusBlock(target);

      var badge = container.querySelector('.blockchain-3d-badge span:last-child');
      if (badge) {
        badge.textContent = 'Locked-In: Block #' + target.userData.index + ' (SHA-256 Verified)';
      }
    };

    function focusBlock(cube) {
      if (!cube) return;
      var worldPos = new THREE.Vector3();
      cube.getWorldPosition(worldPos);

      targetCameraPos.set(worldPos.x, worldPos.y + 6, worldPos.z + 26);
      targetCameraLook.copy(worldPos);
    }

    function resetCamera() {
      targetCameraPos.copy(defaultCameraPos);
      targetCameraLook.copy(defaultCameraLook);
    }

    // ── Live "Simulate Live Block Mining" Feature ────────────────────────────────
    function simulateMining() {
      var btn = document.getElementById('btn-3d-mine');
      if (btn) btn.disabled = true;

      var badge = container.querySelector('.blockchain-3d-badge span:last-child');
      if (badge) badge.textContent = '⚡ Proof-of-Work Mining: Hashing Nonces...';

      // Spawn converging particle cloud
      var particleCount = 80;
      var pGeo = new THREE.BufferGeometry();
      var pPos = new Float32Array(particleCount * 3);
      var lastBlock = blockMeshes[blockMeshes.length - 1];
      var nextX = lastBlock ? lastBlock.position.x + SPACING : 0;
      var nextY = 0;

      for (var k = 0; k < particleCount; k++) {
        pPos[k * 3]     = nextX + (Math.random() - 0.5) * 24;
        pPos[k * 3 + 1] = nextY + (Math.random() - 0.5) * 24;
        pPos[k * 3 + 2] = (Math.random() - 0.5) * 24;
      }
      pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
      var pMat = new THREE.PointsMaterial({
        color: 0x00f2fe,
        size: 0.65,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending
      });
      var pCloud = new THREE.Points(pGeo, pMat);
      group.add(pCloud);

      var miningStep = 0;
      var miningTimer = setInterval(function() {
        miningStep++;
        var pos = pCloud.geometry.attributes.position.array;
        // Converge particles to center
        for (var i = 0; i < particleCount; i++) {
          pos[i * 3]     += (nextX - pos[i * 3]) * 0.12;
          pos[i * 3 + 1] += (nextY - pos[i * 3 + 1]) * 0.12;
          pos[i * 3 + 2] += (0 - pos[i * 3 + 2]) * 0.12;
        }
        pCloud.geometry.attributes.position.needsUpdate = true;

        if (badge) {
          var mockNonce = Math.floor(Math.random() * 999999);
          badge.textContent = '⛏️ PoW Nonce ' + mockNonce + ' | Diff: 4';
        }

        if (miningStep >= 18) {
          clearInterval(miningTimer);
          group.remove(pCloud);

          // Add brand new mined block
          var newIdx = chainData.length;
          var newBlock = {
            index: newIdx,
            hash: '0000' + Math.random().toString(16).slice(2, 10) + Math.random().toString(16).slice(2, 10) + 'pow',
            proof: Math.floor(Math.random() * 80000) + 10000,
            timestamp: Date.now() / 1000
          };
          chainData.push(newBlock);
          build3DChain(chainData);

          // Lock into new block
          window.lockInBlock3D(newIdx);

          if (btn) btn.disabled = false;
          if (window.showToast) {
            window.showToast('success', '⛓️ Block #' + newIdx + ' mined & verified on-chain!');
          }
        }
      }, 70);
    }

    // Attach button listeners
    var btnMine = document.getElementById('btn-3d-mine');
    if (btnMine) btnMine.addEventListener('click', simulateMining);

    var btnFocus = document.getElementById('btn-3d-focus');
    if (btnFocus) {
      btnFocus.addEventListener('click', function() {
        if (blockMeshes.length > 0) focusBlock(blockMeshes[blockMeshes.length - 1]);
      });
    }

    var btnReset = document.getElementById('btn-3d-reset');
    if (btnReset) btnReset.addEventListener('click', resetCamera);

    // ── Raycasting Hover & Interaction ──────────────────────────────────────────
    var raycaster = new THREE.Raycaster();
    var mouseNDC = new THREE.Vector2(-999, -999);
    var hoveredCube = null;

    function getPointerPos(e) {
      var rect = container.getBoundingClientRect();
      return {
        x: ((e.clientX - rect.left) / rect.width) * 2 - 1,
        y: -((e.clientY - rect.top) / rect.height) * 2 + 1
      };
    }

    container.addEventListener('mousemove', function(e) {
      var p = getPointerPos(e);
      mouseNDC.x = p.x;
      mouseNDC.y = p.y;
    });

    container.addEventListener('mouseleave', function() {
      mouseNDC.set(-999, -999);
      hudCard.style.opacity = '0';
      hudCard.style.transform = 'translateY(6px)';
    });

    // Orbit Dragging
    var isDragging = false;
    var prevMouseX = 0;
    var prevMouseY = 0;

    container.addEventListener('mousedown', function(e) {
      if (e.target.tagName === 'BUTTON') return;
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    });

    window.addEventListener('mouseup', function() {
      isDragging = false;
    });

    container.addEventListener('mousemove', function(e) {
      if (!isDragging) return;
      var deltaX = e.clientX - prevMouseX;
      var deltaY = e.clientY - prevMouseY;

      group.rotation.y += deltaX * 0.007;
      group.rotation.x += deltaY * 0.007;

      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    });

    // Touch support (passive to keep vertical scroll smooth)
    var touchStartX = 0;
    container.addEventListener('touchstart', function(e) {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
      }
    }, { passive: true });

    container.addEventListener('touchmove', function(e) {
      if (e.touches.length === 1) {
        var deltaX = e.touches[0].clientX - touchStartX;
        group.rotation.y += deltaX * 0.009;
        touchStartX = e.touches[0].clientX;
      }
    }, { passive: true });

    // Block Click -> Focus
    container.addEventListener('click', function(e) {
      if (e.target.tagName === 'BUTTON') return;
      if (hoveredCube) {
        focusBlock(hoveredCube);
        hoveredCube.userData.targetScale = 1.25;
        setTimeout(function() {
          if (hoveredCube) hoveredCube.userData.targetScale = 1.0;
        }, 300);
      }
    });

    // Resize Handler
    function onResize() {
      var w = container.clientWidth || 800;
      var h = container.clientHeight || 380;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener('resize', onResize);

    // ── Animation Loop & IntersectionObserver ───────────────────────────────────
    var running = true;
    var inView = true;
    var frameId = null;

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function(entries) {
        inView = entries[0].isIntersecting;
        if (inView && running && !frameId) {
          animate();
        } else if (!inView && frameId) {
          cancelAnimationFrame(frameId);
          frameId = null;
        }
      }, { threshold: 0.1 });
      observer.observe(container);
    }

    document.addEventListener('visibilitychange', function() {
      running = !document.hidden;
      if (running && inView && !frameId) animate();
    });

    function animate() {
      if (!running || !inView) {
        frameId = null;
        return;
      }
      frameId = requestAnimationFrame(animate);

      // Idle spin when not dragging and camera at default
      if (!isDragging && targetCameraPos.equals(defaultCameraPos)) {
        group.rotation.y += 0.0025;
      }

      // Smooth camera interpolation
      camera.position.lerp(targetCameraPos, 0.055);
      currentCameraLook.lerp(targetCameraLook, 0.055);
      camera.lookAt(currentCameraLook);

      // Raycasting hover check
      raycaster.setFromCamera(mouseNDC, camera);
      var intersects = raycaster.intersectObjects(blockMeshes, false);
      if (intersects.length > 0) {
        hoveredCube = intersects[0].object;
        container.style.cursor = 'pointer';

        // Update floating HUD card
        var ud = hoveredCube.userData;
        var dateStr = new Date(ud.timestamp * 1000).toLocaleTimeString();
        hudCard.innerHTML = [
          '<div style="font-weight:700;color:' + themeHex + ';margin-bottom:.2rem">⛓️ BLOCK #' + ud.index + ' ' + (ud.isGenesis ? '(GENESIS)' : (ud.isHead ? '(VERIFIED HEAD)' : '')) + '</div>',
          '<div>Hash: <span style="color:#93c5fd">' + ud.hash.slice(0, 10) + '…' + ud.hash.slice(-8) + '</span></div>',
          '<div>Nonce: <span style="color:#fde047">' + ud.proof + '</span> · ' + dateStr + '</div>',
          '<div style="margin-top:.25rem;color:#34d399">● IMMUTABLE · CONSENSUS OK</div>'
        ].join('');
        hudCard.style.opacity = '1';
        hudCard.style.transform = 'translateY(0)';
      } else {
        hoveredCube = null;
        container.style.cursor = 'default';
        if (!lockInBeamMesh) {
          hudCard.style.opacity = '0';
          hudCard.style.transform = 'translateY(6px)';
        }
      }

      // Rotate blocks & apply scale lerp
      for (var b = 0; b < blockMeshes.length; b++) {
        var mesh = blockMeshes[b];
        mesh.rotation.x += 0.004;
        mesh.rotation.y += 0.006;

        var targetScale = (mesh === hoveredCube) ? 1.15 : (mesh.userData.targetScale || 1.0);
        mesh.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
      }

      // Animate laser streaming packets
      for (var sp = 0; sp < streamPackets.length; sp++) {
        var pkt = streamPackets[sp];
        pkt.progress = (pkt.progress + 0.012) % 1;
        pkt.mesh.position.lerpVectors(pkt.source.position, pkt.target.position, pkt.progress);
        var s = 0.6 + Math.sin(pkt.progress * Math.PI) * 0.4;
        pkt.mesh.scale.set(s, s, s);
      }

      // Animate lock-in beam
      if (lockInBeamMesh) {
        lockInBeamMesh.rotation.y += 0.05;
      }

      // Animate shockwave ring
      if (shockwaveMesh) {
        shockwaveMesh.scale.x += 0.18;
        shockwaveMesh.scale.y += 0.18;
        shockwaveMesh.material.opacity *= 0.94;
        if (shockwaveMesh.material.opacity < 0.02) {
          group.remove(shockwaveMesh);
          shockwaveMesh = null;
        }
      }

      renderer.render(scene, camera);
    }

    animate();
  };

  // Auto-init on page load if container exists
  document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('blockchain-3d-container')) {
      window.initBlockchain3D('blockchain-3d-container');
    }
  });
})();
