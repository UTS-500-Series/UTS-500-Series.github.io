// 3D board viewer. A figure holding <div class="view3d" data-src="model.glb"> shows its poster
// image until the reader asks for the 3D view; only then are three.js and the model fetched.
// Drag to turn, scroll or pinch to zoom, right-drag (or two fingers) to pan.
import * as THREE from 'three';
import { GLTFLoader } from './vendor/three/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from './vendor/three/jsm/controls/OrbitControls.js';
import { MeshoptDecoder } from './vendor/three/jsm/libs/meshopt_decoder.module.js';

// KiCad exports a board body in a pale green; show it in the solder-mask green of its renders.
// glTF colours are linear: KiCad's sRGB (0.313, 0.485, 0.41) arrives as about (0.08, 0.2, 0.14).
const BODY = new THREE.Color().setRGB(0.075, 0.20, 0.12, THREE.SRGBColorSpace);
const isBody = c => Math.abs(c.r - 0.080) < 0.015 && Math.abs(c.g - 0.200) < 0.015 && Math.abs(c.b - 0.140) < 0.015;

function start(box) {
  const btn = box.querySelector('button.v3-open');
  btn.disabled = true;
  btn.textContent = 'Loading the 3D model…';

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2.2));
  const key = new THREE.DirectionalLight(0xffffff, 2.0);
  key.position.set(-1, 2, 1.5);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.8);
  fill.position.set(1, -0.5, -1);
  scene.add(fill);
  const camera = new THREE.PerspectiveCamera(35, 1, 0.001, 10);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  let home = null;

  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  loader.load(box.dataset.src, gltf => {
    const model = gltf.scene;
    model.traverse(o => {
      if (o.isMesh && o.material && o.material.color && isBody(o.material.color)) {
        o.material = o.material.clone();
        o.material.color.copy(BODY);
      }
    });
    scene.add(model);
    const bb = new THREE.Box3().setFromObject(model);
    const centre = bb.getCenter(new THREE.Vector3());
    const size = bb.getSize(new THREE.Vector3()).length();
    // KiCad's frame in glTF: x along the card (front edge at -x), y up, z across the card
    const dir = new THREE.Vector3(...(box.dataset.view || '-1,0.9,1.1').split(',').map(Number)).normalize();
    home = { target: centre.clone(), position: centre.clone().add(dir.multiplyScalar(size * 0.95)) };
    camera.near = size / 200; camera.far = size * 20; camera.updateProjectionMatrix();
    reset();
    box.querySelector('img').replaceWith(renderer.domElement);
    box.classList.add('live');
    btn.textContent = 'Reset view';
    btn.disabled = false;
    btn.onclick = reset;
    resize();
    renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
  }, undefined, err => {
    btn.textContent = 'The 3D model could not be loaded';
    console.error(err);
  });

  function reset() {
    if (!home) return;
    controls.target.copy(home.target);
    camera.position.copy(home.position);
    controls.update();
  }
  function resize() {
    const w = box.clientWidth, h = Math.round(w * 0.62);
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(box);
}

for (const box of document.querySelectorAll('.view3d')) {
  box.querySelector('button.v3-open').addEventListener('click', () => start(box), { once: true });
}
