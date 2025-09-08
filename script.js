// Инициализация Three.js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x87CEEB); // Небесный фон
document.getElementById('gameContainer').appendChild(renderer.domElement);

// Свет
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(10, 20, 10);
scene.add(directionalLight);

// Загрузка текстуры
const textureLoader = new THREE.TextureLoader();
const wallTexture = textureLoader.load('https://avatars.mds.yandex.net/i?id=cd19cdb11d3fdb1ae1927afb09eea85c_l-16409040-images-thumbs&n=13');
wallTexture.wrapS = THREE.RepeatWrapping;
wallTexture.wrapT = THREE.RepeatWrapping;
wallTexture.repeat.set(2, 2); // Повтор текстуры

// Создание стен (например, комната 10x10)
function createWall(width, height, depth, x, y, z, rotY = 0) {
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshStandardMaterial({ map: wallTexture });
    const wall = new THREE.Mesh(geometry, material);
    wall.position.set(x, y, z);
    wall.rotation.y = rotY;
    scene.add(wall);
}

// Пол
const floorGeometry = new THREE.PlaneGeometry(20, 20);
const floorMaterial = new THREE.MeshStandardMaterial({ 
    map: wallTexture, 
    side: THREE.DoubleSide 
});
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -2.5;
scene.add(floor);

// Стены комнаты
createWall(10, 5, 0.5, 0, 0, -5);       // Передняя
createWall(10, 5, 0.5, 0, 0, 5);        // Задняя
createWall(0.5, 5, 10, -5, 0, 0, 0);    // Левая
createWall(0.5, 5, 10, 5, 0, 0, 0);     // Правая

// Игрок (камера)
camera.position.set(0, 1.6, 0); // Высота глаз человека
camera.lookAt(0, 1.6, 1);

// Управление
let moveX = 0;
let moveZ = 0;
let rotationSpeed = 0.01;
let touchStartX = 0;
let touchStartY = 0;

// Джойстик
const joystick = document.getElementById('joystick');
const ctx = joystick.getContext('2d');
let joystickActive = false;
let joystickX = 0;
let joystickY = 0;

function drawJoystick() {
    ctx.clearRect(0, 0, joystick.width, joystick.height);
    // Основной круг
    ctx.beginPath();
    ctx.arc(100, 100, 80, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Ручка джойстика
    ctx.beginPath();
    ctx.arc(100 + joystickX, 100 + joystickY, 30, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
}

joystick.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = joystick.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const dx = touch.clientX - centerX;
    const dy = touch.clientY - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < 80) {
        joystickActive = true;
        updateJoystickPosition(touch.clientX, touch.clientY, rect);
    }
});

joystick.addEventListener('touchmove', (e) => {
    if (!joystickActive) return;
    e.preventDefault();
    const touch = e.touches[0];
    const rect = joystick.getBoundingClientRect();
    updateJoystickPosition(touch.clientX, touch.clientY, rect);
});

joystick.addEventListener('touchend', () => {
    joystickActive = false;
    joystickX = 0;
    joystickY = 0;
    moveX = 0;
    moveZ = 0;
    drawJoystick();
});

function updateJoystickPosition(clientX, clientY, rect) {
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    let dx = clientX - centerX;
    let dy = clientY - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > 80) {
        dx = (dx / distance) * 80;
        dy = (dy / distance) * 80;
    }

    joystickX = dx;
    joystickY = dy;

    // Нормализуем направление движения
    moveX = dx / 80;
    moveZ = dy / 80;

    drawJoystick();
}

// Управление камерой свайпом
document.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1 && !joystickActive) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }
});

document.addEventListener('touchmove', (e) => {
    if (e.touches.length === 1 && !joystickActive) {
        e.preventDefault();
        const deltaX = e.touches[0].clientX - touchStartX;
        const deltaY = e.touches[0].clientY - touchStartY;

        // Поворот по горизонтали — вращение вокруг Y
        camera.rotation.y -= deltaX * 0.01;

        // Поворот по вертикали — наклон (ограниченный)
        camera.rotation.x -= deltaY * 0.01;
        camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));

        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }
});

// Анимация и движение
function animate() {
    requestAnimationFrame(animate);

    // Движение вперёд/назад и влево/вправо
    const speed = 0.1;
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);

    // Боковое движение (влево/вправо)
    const right = new THREE.Vector3();
    right.crossVectors(camera.up, direction).normalize();

    camera.position.addScaledVector(direction, -moveZ * speed);
    camera.position.addScaledVector(right, moveX * speed);

    renderer.render(scene, camera);
}

// Адаптация под размер экрана
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Запуск
drawJoystick();
animate();
