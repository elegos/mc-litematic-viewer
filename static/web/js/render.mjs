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


function createBlock(from, to, texturePath, uv, face, position) {
    const geometry = new THREE.BoxGeometry(
        to[0] - from[0],
        to[1] - from[1],
        to[2] - from[2]
    );

    const texture = textureLoader.load(texturePath);
    const material = new THREE.MeshBasicMaterial({ map: texture });

    const block = new THREE.Mesh(geometry, material);
    block.position.set(
        position[0] * 16,  // Scale is based on 16x16
        position[1] * 16,
        position[2] * 16
    );

    // Check whether there are custom UV coordinates and a specific face.
    if (face && uv) {
        // Get the UV geometry attribute
        const uvAttribute = geometry.getAttribute('uv');

        // Normalize the UV coordinates for a 16x16 texture
        const faceUvs = [
            new THREE.Vector2(uv[0] / 16, uv[1] / 16),
            new THREE.Vector2(uv[2] / 16, uv[1] / 16),
            new THREE.Vector2(uv[0] / 16, uv[3] / 16),
            new THREE.Vector2(uv[2] / 16, uv[3] / 16)
        ];

        // Define the face geometry indexes
        const faceIndexMap = {
            'east': [8, 9],    // Est
            'west': [4, 5],    // West
            'up': [0, 1],      // Up
            'down': [6, 7],    // Down
            'north': [10, 11], // North
            'south': [2, 3]    // South
        };

        // Obtain the specified face indexes
        const faceIndices = faceIndexMap[face];

        if (faceIndices) {
            // Apply the personalized UV coordinates to the specified faces
            for (let i = 0; i < faceIndices.length; i++) {
                const idx = faceIndices[i] * 2;

                // Set the UV coordinate to the face's vertexes
                uvAttribute.setXY(idx, faceUvs[0].x, faceUvs[0].y);
                uvAttribute.setXY(idx + 1, faceUvs[1].x, faceUvs[1].y);
                uvAttribute.setXY(idx + 2, faceUvs[2].x, faceUvs[2].y);
                uvAttribute.setXY(idx + 3, faceUvs[3].x, faceUvs[3].y);
            }
        }

        // Ensure that Three.js updates the UV mappings
        uvAttribute.needsUpdate = true;
    }

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
                const uv = block.uv ?? null;
                const face = block.face ?? null;
                
                block.positions.forEach(position => {
                    const blockMesh = createBlock(from, to, texturePath, uv, face, position);
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
