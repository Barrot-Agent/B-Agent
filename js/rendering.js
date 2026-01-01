// 3D Rendering functionality for Barrot website

let scene, camera, renderer, currentMesh;
let rotationSpeedValue = 0.01;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize 3D rendering
    init3DRendering();
    animate3D();
    
    // Event listeners
    const shapeSelector = document.getElementById('shapeSelector');
    const rotationSpeed = document.getElementById('rotationSpeed');
    const colorPicker = document.getElementById('colorPicker');
    const resetRender = document.getElementById('resetRender');
    const exportRender = document.getElementById('exportRender');
    
    if (shapeSelector) {
        shapeSelector.addEventListener('change', changeShape);
    }
    
    if (rotationSpeed) {
        rotationSpeed.addEventListener('input', updateRotationSpeed);
    }
    
    if (colorPicker) {
        colorPicker.addEventListener('input', changeColor);
    }
    
    if (resetRender) {
        resetRender.addEventListener('click', resetRendering);
    }
    
    if (exportRender) {
        exportRender.addEventListener('click', exportRendering);
    }
});

function init3DRendering() {
    const canvas = document.getElementById('renderCanvas');
    if (!canvas) return;
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    
    // Create camera
    camera = new THREE.PerspectiveCamera(
        75,
        canvas.offsetWidth / canvas.offsetHeight,
        0.1,
        1000
    );
    camera.position.z = 5;
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ 
        canvas: canvas,
        antialias: true,
        preserveDrawingBuffer: true // Needed for export
    });
    renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);
    
    const pointLight2 = new THREE.PointLight(0x00ff88, 0.5);
    pointLight2.position.set(-5, -5, 5);
    scene.add(pointLight2);
    
    // Create initial shape (cube)
    createShape('cube');
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

function createShape(shapeType) {
    // Remove existing mesh
    if (currentMesh) {
        scene.remove(currentMesh);
        if (currentMesh.geometry) currentMesh.geometry.dispose();
        if (currentMesh.material) currentMesh.material.dispose();
    }
    
    // Get color
    const colorPicker = document.getElementById('colorPicker');
    const color = colorPicker ? colorPicker.value : '#00ff88';
    
    // Create geometry based on type
    let geometry;
    switch(shapeType) {
        case 'cube':
            geometry = new THREE.BoxGeometry(2, 2, 2);
            break;
        case 'sphere':
            geometry = new THREE.SphereGeometry(1.5, 32, 32);
            break;
        case 'torus':
            geometry = new THREE.TorusGeometry(1.2, 0.5, 16, 100);
            break;
        case 'cone':
            geometry = new THREE.ConeGeometry(1.5, 3, 32);
            break;
        default:
            geometry = new THREE.BoxGeometry(2, 2, 2);
    }
    
    // Create material
    const material = new THREE.MeshPhongMaterial({
        color: color,
        shininess: 100,
        specular: 0x444444
    });
    
    // Create mesh
    currentMesh = new THREE.Mesh(geometry, material);
    scene.add(currentMesh);
}

function animate3D() {
    requestAnimationFrame(animate3D);
    
    // Rotate mesh
    if (currentMesh) {
        currentMesh.rotation.x += rotationSpeedValue;
        currentMesh.rotation.y += rotationSpeedValue * 1.5;
    }
    
    renderer.render(scene, camera);
}

function changeShape() {
    const shapeSelector = document.getElementById('shapeSelector');
    if (shapeSelector) {
        createShape(shapeSelector.value);
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification(`Shape changed to ${shapeSelector.value}`, 'success');
        }
    }
}

function updateRotationSpeed() {
    const rotationSpeed = document.getElementById('rotationSpeed');
    if (rotationSpeed) {
        rotationSpeedValue = (rotationSpeed.value / 100) * 0.02;
    }
}

function changeColor() {
    const colorPicker = document.getElementById('colorPicker');
    if (colorPicker && currentMesh) {
        currentMesh.material.color.set(colorPicker.value);
    }
}

function resetRendering() {
    // Reset to default values
    const shapeSelector = document.getElementById('shapeSelector');
    const rotationSpeed = document.getElementById('rotationSpeed');
    const colorPicker = document.getElementById('colorPicker');
    
    if (shapeSelector) {
        shapeSelector.value = 'cube';
    }
    
    if (rotationSpeed) {
        rotationSpeed.value = 50;
        rotationSpeedValue = 0.01;
    }
    
    if (colorPicker) {
        colorPicker.value = '#00ff88';
    }
    
    // Reset camera position
    camera.position.set(0, 0, 5);
    camera.lookAt(0, 0, 0);
    
    // Recreate shape
    createShape('cube');
    
    if (window.BarrotApp) {
        window.BarrotApp.showNotification('Rendering reset to defaults', 'info');
    }
}

function exportRendering() {
    if (!renderer) return;
    
    try {
        // Render current frame
        renderer.render(scene, camera);
        
        // Get canvas data
        const canvas = renderer.domElement;
        const dataURL = canvas.toDataURL('image/png');
        
        // Create download link
        const link = document.createElement('a');
        link.download = `barrot-render-${Date.now()}.png`;
        link.href = dataURL;
        link.click();
        
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Rendering exported successfully!', 'success');
        }
    } catch (error) {
        console.error('Error exporting render:', error);
        if (window.BarrotApp) {
            window.BarrotApp.showNotification('Failed to export rendering', 'error');
        }
    }
}

function onWindowResize() {
    const canvas = document.getElementById('renderCanvas');
    if (!canvas || !camera || !renderer) return;
    
    camera.aspect = canvas.offsetWidth / canvas.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
}

// Add mouse controls for rotating the object
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };

const canvas = document.getElementById('renderCanvas');
if (canvas) {
    canvas.addEventListener('mousedown', function(e) {
        isDragging = true;
    });
    
    canvas.addEventListener('mousemove', function(e) {
        if (isDragging && currentMesh) {
            const deltaMove = {
                x: e.offsetX - previousMousePosition.x,
                y: e.offsetY - previousMousePosition.y
            };
            
            currentMesh.rotation.y += deltaMove.x * 0.01;
            currentMesh.rotation.x += deltaMove.y * 0.01;
        }
        
        previousMousePosition = {
            x: e.offsetX,
            y: e.offsetY
        };
    });
    
    canvas.addEventListener('mouseup', function(e) {
        isDragging = false;
    });
    
    canvas.addEventListener('mouseleave', function(e) {
        isDragging = false;
    });
    
    // Touch support for mobile
    canvas.addEventListener('touchstart', function(e) {
        isDragging = true;
        const touch = e.touches[0];
        previousMousePosition = {
            x: touch.clientX,
            y: touch.clientY
        };
    });
    
    canvas.addEventListener('touchmove', function(e) {
        if (isDragging && currentMesh) {
            const touch = e.touches[0];
            const deltaMove = {
                x: touch.clientX - previousMousePosition.x,
                y: touch.clientY - previousMousePosition.y
            };
            
            currentMesh.rotation.y += deltaMove.x * 0.01;
            currentMesh.rotation.x += deltaMove.y * 0.01;
            
            previousMousePosition = {
                x: touch.clientX,
                y: touch.clientY
            };
        }
    });
    
    canvas.addEventListener('touchend', function(e) {
        isDragging = false;
    });
}
