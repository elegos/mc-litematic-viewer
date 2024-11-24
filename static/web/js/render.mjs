import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.getElementById('minecraftCanvas');
const renderer = new THREE.WebGLRenderer({ canvas });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Scene and camera creation
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 30, 50);  // Position the camera at a certain distance from the blocks
const controls = new OrbitControls(camera, renderer.domElement);

// Light
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 10);
scene.add(light);

// Texture loader
const textureLoader = new THREE.TextureLoader();


function createBlock(from, to, texturePath, position) {
    const geometry = new THREE.BoxGeometry(
        to[0] - from[0],
        to[1] - from[1],
        to[2] - from[2]
    );
    
    const texture = textureLoader.load(texturePath);
    const material = new THREE.MeshBasicMaterial({ map: texture });
    
    const block = new THREE.Mesh(geometry, material);
    block.position.set(
        position[0] * 16,  // Scala basata su 16x16
        position[1] * 16,
        position[2] * 16
    );
    
    return block;
}

// Sample data
fetch('/test-model')
    .then(response => response.json())
    .then(data => {
        const regions = data.regions;
        for (const regionName in regions) {
            const region = regions[regionName];
            const textures = region.textures;
            const blocks = region.blocks;
            
            blocks.forEach(block => {
                const from = block.from_coordinate;
                const to = block.to_coordinate;
                const textureUUID = block.texture;
                const texturePath = textures[textureUUID];
                
                block.positions.forEach(position => {
                    const blockMesh = createBlock(from, to, texturePath, position);
                    scene.add(blockMesh);
                });
            });
        }
        
        animate();
    });

// Animation function to update the rendering loop.
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
