/* ============================================================================
   hero3d.js — Next-Gen Interactive 3D Blockchain Hero Experience
   ============================================================================
   Renders a chain of crystalline linked blocks into any [data-hero3d] canvas.
   Built with Three.js WebGL:
   - Dynamic campus theme adaptation (JIIT Blue/Cyan, JUIT Green/Emerald, JUET Gold)
   - Dynamic data packet energy pulses traveling between block nodes
   - Floating holographic 3D cryptographic HUD badges (Genesis, Merkle, PoW, Verified)
   - Raycasting hover & click-to-copy block hash with elastic recoil animation
   - 60fps performance optimization: IntersectionObserver culling & mobile DPR clamp
   - Full graceful degradation: keeps .chain-fallback active if WebGL is unavailable
   ========================================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent || ''
  );

  function createTextSprite(text, colorHex) {
    var canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.clearRect(0, 0, 256, 64);

    // Pill background
    ctx.fillStyle = 'rgba(10, 15, 30, 0.75)';
    ctx.strokeStyle = colorHex || '#00f2fe';
    ctx.lineWidth = 2;
    var r = 14;
    var x = 8, y = 8, w = 240, h = 48;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Text label
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 18px "SF Mono", "Fira Code", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 128, 32);

    var texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    var spriteMat = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      opacity: 0.88,
      depthTest: false
    });
    var sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(1.5, 0.38, 1);
    return sprite;
  }

  function init(canvas) {
    var THREE = window.THREE;
    if (!THREE || !canvas) return null;

    var host = canvas.parentElement || canvas;
    var width = host.clientWidth || 640;
    var height = host.clientHeight || 320;

    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: !isMobile,
        powerPreference: 'low-power'
      });
    } catch (err) {
      return null;
    }

    // Performance target: mobile DPR capped to 1, desktop capped to 2
    var dpr = isMobile ? 1 : Math.min(window.devicePixelRatio || 1, 2);
    renderer.setPixelRatio(dpr);
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
    var textBadgeHex = '#00f2fe';

    if (campus === 'juit') {
      primaryColor = 0x059669; // JUIT Pine Green
      secondaryColor = 0x34d399; // Emerald Aurora
      edgeColor = 0x10b981;
      textBadgeHex = '#34d399';
    } else if (campus === 'juet') {
      primaryColor = 0xd97706; // JUET Amber Gold
      secondaryColor = 0xfbbf24; // Solar Flare
      edgeColor = 0xf59e0b;
      textBadgeHex = '#fbbf24';
    }

    scene.add(new THREE.AmbientLight(0xffffff, 0.95));

    var key = new THREE.PointLight(secondaryColor, 2.4, 45);
    key.position.set(-3, 6, 8);
    scene.add(key);

    var rim = new THREE.PointLight(primaryColor, 1.9, 45);
    rim.position.set(8, -2, 6);
    scene.add(rim);

    var accent = new THREE.PointLight(0xffffff, 1.3, 35);
    accent.position.set(2, -4, 7);
    scene.add(accent);

    // ---- The blockchain group ----
    var group = new THREE.Group();
    group.position.set(2.6, 0.2, 0.8);
    scene.add(group);

    var COUNT = 5;
    var SPACING = 2.45;
    var blocks = [];
    var blockMeshes = [];

    var geometry = new THREE.BoxGeometry(1.55, 1.55, 1.55);
    var edgeGeometry = new THREE.EdgesGeometry(geometry);
    var innerGeometry = new THREE.BoxGeometry(0.72, 0.72, 0.72);

    var blockLabels = [
      'GENESIS #0',
      'MERKLE #1',
      'POW-PROVED #2',
      'IMMUTABLE #3',
      'VERIFIED HEAD'
    ];

    var blockHashes = [
      '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f',
      '8f4a2b9015c9284d720b05b637d7a1286c91e32ba305a468d6c757f7d1b32e18',
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b',
      '00000000000000000005a7690da0175b331ff3d8b5a0462caec12a9c36294a28'
    ];

    for (var i = 0; i < COUNT; i++) {
      var t = i / (COUNT - 1);
      var blockColor = new THREE.Color(primaryColor).lerp(new THREE.Color(secondaryColor), t);

      var material = new THREE.MeshStandardMaterial({
        color: blockColor,
        metalness: 0.25,
        roughness: 0.12,
        transparent: true,
        opacity: 0.82,
        emissive: blockColor,
        emissiveIntensity: 0.28
      });

      var mesh = new THREE.Mesh(geometry, material);
      mesh.position.x = (i - (COUNT - 1) / 2) * SPACING;
      mesh.position.y = Math.sin(i * 1.1) * 0.28;
      mesh.rotation.set(0.34, 0.62, 0.1);

      mesh.userData = {
        index: i,
        label: blockLabels[i],
        hash: blockHashes[i],
        initialScale: 1.0,
        currentScale: 1.0,
        targetScale: 1.0,
        emissiveBoost: 0
      };

      // Outer glowing neon wireframe edges
      var edges = new THREE.LineSegments(
        edgeGeometry,
        new THREE.LineBasicMaterial({
          color: edgeColor,
          transparent: true,
          opacity: 0.9,
          linewidth: 2
        })
      );
      mesh.add(edges);

      // Inner counter-rotating core
      var innerMaterial = new THREE.MeshBasicMaterial({
        color: secondaryColor,
        wireframe: true,
        transparent: true,
        opacity: 0.65
      });
      var innerMesh = new THREE.Mesh(innerGeometry, innerMaterial);
      mesh.add(innerMesh);

      // Verified Head Block distinction
      if (i === COUNT - 1) {
        material.color = new THREE.Color(0x34d399);
        material.emissive = new THREE.Color(0x059669);
        material.emissiveIntensity = 0.8;
      }

      // Floating 3D HUD label sprite
      var sprite = createTextSprite(blockLabels[i], textBadgeHex);
      if (sprite) {
        sprite.position.set(0, 1.45, 0);
        mesh.add(sprite);
      }

      group.add(mesh);
      blocks.push({
        mesh: mesh,
        inner: innerMesh,
        phase: i * 0.85,
        baseY: mesh.position.y,
        sprite: sprite,
        userData: mesh.userData
      });
      blockMeshes.push(mesh);
    }

    // ---- Laser Links between blocks ----
    var links = [];
    var packets = [];
    var packetGeo = new THREE.SphereGeometry(0.12, 12, 12);
    var packetMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.95
    });

    for (var j = 0; j < COUNT - 1; j++) {
      var linkLength = SPACING - 1.55;
      var link = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, linkLength, 12),
        new THREE.MeshBasicMaterial({ color: edgeColor, transparent: true, opacity: 0.78 })
      );
      link.rotation.z = Math.PI / 2;
      link.position.x = (j - (COUNT - 1) / 2 + 0.5) * SPACING;
      group.add(link);
      links.push({ mesh: link, a: j, b: j + 1, baseX: link.position.x });

      // Dynamic cryptographic packet traveling along this link
      var packet = new THREE.Mesh(packetGeo, packetMat.clone());
      packet.material.color = new THREE.Color(secondaryColor);
      group.add(packet);
      packets.push({
        mesh: packet,
        linkIdx: j,
        progress: (j * 0.25) % 1,
        speed: 0.65 + (j % 2) * 0.2
      });
    }

    // ---- Dust motes for depth parallax ----
    var moteCount = isMobile ? 60 : 140;
    var positions = new Float32Array(moteCount * 3);
    for (var k = 0; k < moteCount; k++) {
      positions[k * 3]     = (Math.random() - 0.5) * 22;
      positions[k * 3 + 1] = (Math.random() - 0.5) * 12;
      positions[k * 3 + 2] = (Math.random() - 0.5) * 14 - 2;
    }
    var moteGeometry = new THREE.BufferGeometry();
    moteGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    var motes = new THREE.Points(moteGeometry, new THREE.PointsMaterial({
      color: 0xaab4ff,
      size: 0.08,
      transparent: true,
      opacity: 0.5,
      sizeAttenuation: true
    }));
    scene.add(motes);

    // ---- Pointer parallax & Raycasting Interactivity ----
    var pointer = { x: 0, y: 0 };
    var target = { x: 0, y: 0 };
    var mouseNDC = new THREE.Vector2(-999, -999);
    var raycaster = new THREE.Raycaster();
    var hoveredBlock = null;

    function onPointerMove(event) {
      var rect = host.getBoundingClientRect();
      target.x = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
      target.y = ((event.clientY - rect.top) / rect.height - 0.5) * 2;

      mouseNDC.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouseNDC.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }

    function onPointerLeave() {
      target.x = 0;
      target.y = 0;
      mouseNDC.set(-999, -999);
    }

    function triggerBlockFeedback(block) {
      if (!block) return;
      block.userData.targetScale = 1.35;
      block.userData.emissiveBoost = 1.0;

      // Copy hash to clipboard and show toast
      var hashText = block.userData.hash;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(hashText).catch(function () {});
      }

      if (window.showToast) {
        window.showToast('success', '⛓️ Block #' + block.userData.index + ' Hash: ' + hashText.slice(0, 16) + '… copied!');
      } else {
        var toast = document.createElement('div');
        toast.className = 'toast toast-success';
        toast.textContent = '⛓️ ' + block.userData.label + ' Hash Copied!';
        document.body.appendChild(toast);
        setTimeout(function () { toast.remove(); }, 2500);
      }
    }

    function onPointerDown(event) {
      if (mouseNDC.x === -999) return;
      raycaster.setFromCamera(mouseNDC, camera);
      var intersects = raycaster.intersectObjects(blockMeshes, false);
      if (intersects.length > 0) {
        var hitMesh = intersects[0].object;
        triggerBlockFeedback(hitMesh);
      }
    }

    host.addEventListener('pointermove', onPointerMove, { passive: true });
    host.addEventListener('pointerleave', onPointerLeave, { passive: true });
    host.addEventListener('pointerdown', onPointerDown);

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

    // ---- Loop & Performance Visibility Culling ----
    var running = true;
    var isInViewport = true;
    var frame = null;
    var start = performance.now();

    function render(now) {
      if (!running || !isInViewport) return;
      var t = (now - start) / 1000;

      // Smooth pointer easing
      pointer.x += (target.x - pointer.x) * 0.055;
      pointer.y += (target.y - pointer.y) * 0.055;

      group.rotation.y = Math.sin(t * 0.22) * 0.4 + pointer.x * 0.36;
      group.rotation.x = -0.08 + pointer.y * 0.22;

      // Raycasting hover check
      raycaster.setFromCamera(mouseNDC, camera);
      var intersects = raycaster.intersectObjects(blockMeshes, false);
      if (intersects.length > 0) {
        hoveredBlock = intersects[0].object;
        host.style.cursor = 'pointer';
      } else {
        hoveredBlock = null;
        host.style.cursor = 'default';
      }

      // Update blocks
      for (var i = 0; i < blocks.length; i++) {
        var b = blocks[i];
        b.mesh.position.y = b.baseY + Math.sin(t * 0.95 + b.phase) * 0.24;
        b.mesh.rotation.y += 0.0042;
        b.mesh.rotation.x += 0.0016;

        if (b.inner) {
          b.inner.rotation.y -= 0.012;
          b.inner.rotation.x += 0.008;
        }

        // Floating label hover bobbing
        if (b.sprite) {
          b.sprite.position.y = 1.45 + Math.sin(t * 2.0 + b.phase) * 0.08;
        }

        // Hover & recoil scale lerp
        var ud = b.userData;
        if (b.mesh === hoveredBlock && ud.targetScale === 1.0) {
          ud.targetScale = 1.15;
        } else if (b.mesh !== hoveredBlock && ud.targetScale === 1.15) {
          ud.targetScale = 1.0;
        }

        ud.currentScale += (ud.targetScale - ud.currentScale) * 0.12;
        b.mesh.scale.set(ud.currentScale, ud.currentScale, ud.currentScale);

        // Decay recoil scale back to 1.0
        if (ud.targetScale > 1.15) {
          ud.targetScale += (1.0 - ud.targetScale) * 0.06;
        }

        // Emissive light boost decay
        if (ud.emissiveBoost > 0) {
          ud.emissiveBoost *= 0.92;
          if (b.mesh.material && b.mesh.material.emissiveIntensity !== undefined) {
            b.mesh.material.emissiveIntensity = 0.28 + ud.emissiveBoost * 1.5;
          }
        }
      }

      // Links follow connected blocks
      for (var j = 0; j < links.length; j++) {
        var l = links[j];
        l.mesh.position.y = (blocks[l.a].mesh.position.y + blocks[l.b].mesh.position.y) / 2;
      }

      // Cryptographic packet animation
      for (var p = 0; p < packets.length; p++) {
        var pkt = packets[p];
        pkt.progress = (pkt.progress + 0.006 * pkt.speed) % 1;
        var bA = blocks[pkt.linkIdx].mesh;
        var bB = blocks[pkt.linkIdx + 1].mesh;

        // Linear interpolation between the two connected blocks
        pkt.mesh.position.x = THREE.MathUtils.lerp(bA.position.x, bB.position.x, pkt.progress);
        pkt.mesh.position.y = THREE.MathUtils.lerp(bA.position.y, bB.position.y, pkt.progress);
        pkt.mesh.position.z = THREE.MathUtils.lerp(bA.position.z, bB.position.z, pkt.progress);

        // Pulse size
        var pScale = 0.8 + Math.sin(pkt.progress * Math.PI) * 0.5;
        pkt.mesh.scale.set(pScale, pScale, pScale);
      }

      motes.rotation.y = t * 0.018;
      motes.position.y = Math.sin(t * 0.28) * 0.35;

      renderer.render(scene, camera);
      frame = requestAnimationFrame(render);
    }

    // ---- IntersectionObserver to pause loop when scrolled out of view ----
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        var entry = entries[0];
        isInViewport = entry.isIntersecting;
        if (isInViewport && running && !frame) {
          start = performance.now();
          frame = requestAnimationFrame(render);
        } else if (!isInViewport && frame) {
          cancelAnimationFrame(frame);
          frame = null;
        }
      }, { threshold: 0.05 });
      observer.observe(canvas);
    }

    // Pause on background tab
    function onVisibility() {
      if (document.hidden) {
        running = false;
        if (frame) {
          cancelAnimationFrame(frame);
          frame = null;
        }
      } else if (!running) {
        running = true;
        if (isInViewport) {
          start = performance.now();
          frame = requestAnimationFrame(render);
        }
      }
    }
    document.addEventListener('visibilitychange', onVisibility);

    // WebGL Context Loss / Restoration
    canvas.addEventListener('webglcontextlost', function (e) {
      e.preventDefault();
      if (frame) cancelAnimationFrame(frame);
      frame = null;
      running = false;
    }, false);

    canvas.addEventListener('webglcontextrestored', function () {
      running = true;
      start = performance.now();
      frame = requestAnimationFrame(render);
    }, false);

    resize();

    if (reduceMotion) {
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
