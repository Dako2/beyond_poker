// Define 'card' globally to ensure it is accessible within the 'animate' function
let card;

// Scene, camera, and renderer setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('webgl-output').appendChild(renderer.domElement);
renderer.setClearColor(0x222222);
camera.position.z = 5;

// Remove or disable any previous light setups if they conflict

// Light coming from the left
const lightLeft = new THREE.DirectionalLight(0xffffff, 0.55); // White light, 75% intensity
lightLeft.position.set(-3, -1, 5); // Position left of the scene
scene.add(lightLeft);

// Light coming from the right
const lightRight = new THREE.DirectionalLight(0xffffff, 0.55); // White light, 75% intensity
lightRight.position.set(3, 1, 5); // Position right of the scene
scene.add(lightRight);

const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
scene.add(ambientLight);

// Load both front and back card face textures
const loader = new THREE.TextureLoader();
const frontTexture = loader.load('QH.png'); // Front image
const backTexture = loader.load('BACK.png'); // Back image (replace 'back.png' with your actual file)
// Function to handle mousewheel events for zooming
function onMouseWheel(event) {
    // Adjust camera position based on scroll direction
    const delta = event.deltaY;
    camera.position.z += delta * 0.01; // Adjust zoom speed here
}

// Add event listener for mousewheel events
document.addEventListener('mousewheel', onMouseWheel, false);
document.addEventListener('DOMMouseScroll', onMouseWheel, false); // For Firefox


const cardGeometry = new THREE.BoxGeometry(2, 3, 0.01);
const materials = [
    new THREE.MeshStandardMaterial({color: 0xffd700, metalness: 0.2, roughness: 0.4}), // Side
    new THREE.MeshStandardMaterial({color: 0xffd700, metalness: 0.2, roughness: 0.4}), // Side
    new THREE.MeshStandardMaterial({color: 0xffd700, metalness: 0.2, roughness: 0.4}), // Top
    new THREE.MeshStandardMaterial({color: 0xffd700, metalness: 0.2, roughness: 0.4}), // Bottom
    new THREE.MeshStandardMaterial({map: frontTexture, color: 0xffd700, metalness: 0.5, roughness: 0.1}), // Front
    new THREE.MeshStandardMaterial({map: backTexture, color: 0xffd700, metalness: 0.5, roughness: 0.1})  // Back
];

// Create a mesh with the geometry and materials array
card = new THREE.Mesh(cardGeometry, materials);
card.position.set(0, 0, 0);
scene.add(card);

// Particle system setup
const particleCount = 2000;
const particles = new THREE.BufferGeometry();
const positions = [];
const color = new THREE.Color(0xFFC0CB);

for (let i = 0; i < particleCount; i++) {
    const x = Math.random() * 500 - 250;
    const y = Math.random() * 500 - 250;
    const z = Math.random() * 500 - 250;
    positions.push(x, y, z);
}

particles.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));

const pMaterial = new THREE.PointsMaterial({
    size: 0.4,
    color: color,
    depthWrite: false
});

const particleSystem = new THREE.Points(particles, pMaterial);
scene.add(particleSystem);

// Define variables to track mouse movement
let prevMouseX = 0;

// Function to update rotation speed based on mouse movements
function updateRotationSpeedWithMouseMovement(mouseX) {
    const deltaX = mouseX - prevMouseX;
    cardRotationSpeed = deltaX * 0.001; // Adjust rotation speed based on mouse movement
    prevMouseX = mouseX;
}

// Add event listeners for mouse movement
document.addEventListener('mousemove', (event) => {
    updateRotationSpeedWithMouseMovement(event.clientX);
});

// Animation function
function animate() {
    requestAnimationFrame(animate);

    // Rotate the card based on the current rotation speed
    card.rotation.y -= cardRotationSpeed; // 0.015

    particleSystem.rotation.y += 0.001; // Swirling effect for particles

    renderer.render(scene, camera);
}

animate();
