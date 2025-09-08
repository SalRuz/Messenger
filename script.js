// Инициализация Three.js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x87CEEB);
document.getElementById('gameContainer').appendChild(renderer.domElement);

// Свет
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(50, 100, 70);
scene.add(directionalLight);

// Загрузка текстур
const textureLoader = new THREE.TextureLoader();

const brickTexture = textureLoader.load('https://avatars.mds.yandex.net/i?id=cd19cdb11d3fdb1ae1927afb09eea85c_l-16409040-images-thumbs&n=13');
brickTexture.wrapS = THREE.RepeatWrapping;
brickTexture.wrapT = THREE.RepeatWrapping;
brickTexture.repeat.set(4, 4); // Увеличим повтор для больших стен

const houseTexture = textureLoader.load('https://avatars.mds.yandex.net/i?id=bcc62e7653b6b1e068912ae7e7a0ad5c_l-2925590-images-thumbs&n=13');
houseTexture.wrapS = THREE.RepeatWrapping;
houseTexture.wrapT = THREE.RepeatWrapping;
houseTexture.repeat.set(2, 2);

const floorHouseTexture = textureLoader.load('https://static.insales-cdn.com/images/products/1/7649/613162465/%D0%B1%D0%B5%D0%BB%D1%8C%D1%84%D0%BE%D1%80.jpg');
floorHouseTexture.wrapS = THREE.RepeatWrapping;
floorHouseTexture.wrapT = THREE.RepeatWrapping;
floorHouseTexture.repeat.set(4, 4);

const grassTexture = textureLoader.load('https://i.pinimg.com/originals/d1/cc/9c/d1cc9c7433f5c12bac1d86726716af9e.jpg?nii=t');
grassTexture.wrapS = THREE.RepeatWrapping;
grassTexture.wrapT = THREE.RepeatWrapping;
grassTexture.repeat.set(16, 16); // Большая карта — больше повторов

// Физика игрока
let player = {
    height: 1.8,
    radius: 0.5,
    velocity: new THREE.Vector3(0, 0, 0),
    position: new THREE.Vector3(0, 50, 0), // ✅ НАЧИНАЕТ ВЫСОКО В НЕБЕ!
    onGround: false,
    speed: 0.2,
    jumpStrength: 0.3
};

camera.position.copy(player.position);
scene.add(camera);

// Коллекция коллайдеров
const collidableMeshes = [];

// Функция создания стены
function createWall(width, height, depth, x, y, z, rotY = 0, texture = brickTexture, isHouse = false) {
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshStandardMaterial({ map: texture });
    const wall = new THREE.Mesh(geometry, material);
    wall.position.set(x, y, z);
    wall.rotation.y = rotY;
    wall.userData = { isHouse: isHouse };
    scene.add(wall);
    collidableMeshes.push(wall);
    return wall;
}

// Создание платформы (пола)
function createPlatform(width, depth, x, z, texture = grassTexture) {
    const geometry = new THREE.PlaneGeometry(width, depth);
    const material = new THREE.MeshStandardMaterial({ 
        map: texture,
        side: THREE.DoubleSide 
    });
    const platform = new THREE.Mesh(geometry, material);
    platform.rotation.x = -Math.PI / 2;
    platform.position.set(x, 0, z); // Все платформы на y=0
    scene.add(platform);
    collidableMeshes.push(platform);
    return platform;
}

// Создание большого дома (в 4 раза больше)
function createHouse(x, z) {
    const scale = 4;
    const houseWidth = 6 * scale;
    const houseDepth = 6 * scale;
    const houseHeight = 5 * scale;
    const wallThickness = 0.5 * scale;

    // Пол дома — новая текстура
    createPlatform(houseWidth, houseDepth, x, z, floorHouseTexture);

    // Стены
    createWall(houseWidth, houseHeight, wallThickness, x, houseHeight/2, z - houseDepth/2 + wallThickness/2, 0, houseTexture, true); // Передняя
    createWall(houseWidth, houseHeight, wallThickness, x, houseHeight/2, z + houseDepth/2 - wallThickness/2, 0, houseTexture, true);  // Задняя
    createWall(wallThickness, houseHeight, houseDepth - 2 * scale, x - houseWidth/2 + wallThickness/2, houseHeight/2, z, 0, houseTexture, true); // Левая
    createWall(wallThickness, houseHeight, houseDepth - 2 * scale, x + houseWidth/2 - wallThickness/2, houseHeight/2, z, 0, houseTexture, true); // Правая

    // Крыша
    const roofGeometry = new THREE.ConeGeometry(houseWidth + 1, 4 * scale, 4);
    const roofMaterial = new THREE.MeshStandardMaterial({ color: 0x5c4033 });
    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
    roof.position.set(x, houseHeight + 2 * scale, z);
    roof.rotation.y = Math.PI / 4;
    scene.add(roof);
}

// ✅ КАРТА В 4 РАЗА БОЛЬШЕ
const mapSize = 400; // было 100 → теперь 400

// Основной пол — трава
createPlatform(mapSize, mapSize, 0, 0, grassTexture);

// Дома (в 4 раза больше и дальше друг от друга)
createHouse(80, 80);
createHouse(-100, 120);
createHouse(120, -100);
createHouse(-120, -120);

// Ограждения по краям карты
for (let i = -mapSize/2 + 10; i <= mapSize/2 - 10; i += 20) {
    createWall(0.5 * 4, 6 * 4, 20, i, 3 * 4, -mapSize/2, 0, brickTexture);
    createWall(0.5 * 4, 6 * 4, 20, i, 3 * 4, mapSize/2, 0, brickTexture);
    createWall(20, 6 * 4, 0.5 * 4, -mapSize/2, 3 * 4, i, 0, brickTexture);
    createWall(20, 6 * 4, 0.5 * 4, mapSize/2, 3 * 4, i, 0, brickTexture);
}

// === УПРАВЛЕНИЕ ===

let moveX = 0;
let moveZ = 0;
let canJump = false;

// Джойстик
const joystick = document.getElementById('joystick');
const ctx = joystick.getContext('2d');
let joystickActive = false;
let joystickX = 0;
let joystickY = 0;

function drawJoystick() {
    ctx.clearRect(0, 0, joystick.width, joystick.height);
    ctx.beginPath();
    ctx.arc(100, 100, 80, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();

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

    moveX = dx / 80;
    moveZ = dy / 80;

    drawJoystick();
}

// Поворот камеры свайпом
let touchStartX = 0;
let touchStartY = 0;

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

        camera.rotation.y -= deltaX * 0.01;
        camera.rotation.x -= deltaY * 0.01;
        camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, camera.rotation.x));

        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }
});

// Прыжок по тапу
document.addEventListener('touchend', (e) => {
    if (!joystickActive && canJump) {
        player.velocity.y = player.jumpStrength;
        player.onGround = false;
        canJump = false;
    }
});

// === ФИЗИКА И СТОЛКНОВЕНИЯ ===

function checkCollision() {
    const p = player.position;
    const v = player.velocity;
    const h = player.height;
    const r = player.radius;

    const playerBottom = p.y - h/2;
    const playerTop = p.y + h/2;
    const playerLeft = p.x - r;
    const playerRight = p.x + r;
    const playerFront = p.z - r;
    const playerBack = p.z + r;

    player.onGround = false;

    for (let mesh of collidableMeshes) {
        const box = new THREE.Box3().setFromObject(mesh);
        const { min, max } = box;

        // Горизонтальное пересечение?
        if (playerRight <= min.x || playerLeft >= max.x ||
            playerBack <= min.z || playerFront >= max.z) {
            continue;
        }

        // Если это пол (почти горизонтальный)
        if (Math.abs(mesh.rotation.x + Math.PI/2) < 0.1 || mesh.rotation.x === 0) {
            // Проверка снизу — приземление
            if (playerBottom <= max.y && playerBottom + v.y >= max.y && v.y <= 0) {
                player.position.y = max.y + h/2;
                player.velocity.y = 0;
                player.onGround = true;
                canJump = true;
            }
        } else {
            // Вертикальные стены — блокируем движение по X/Z
            if (playerRight > min.x && playerLeft < min.x && v.x > 0) {
                player.position.x = min.x - r;
                player.velocity.x = 0;
            }
            if (playerLeft < max.x && playerRight > max.x && v.x < 0) {
                player.position.x = max.x + r;
                player.velocity.x = 0;
            }
            if (playerBack > min.z && playerFront < min.z && v.z > 0) {
                player.position.z = min.z - r;
                player.velocity.z = 0;
            }
            if (playerFront < max.z && playerBack > max.z && v.z < 0) {
                player.position.z = max.z + r;
                player.velocity.z = 0;
            }
        }
    }
}

// Анимация
function animate() {
    requestAnimationFrame(animate);

    // Гравитация
    if (!player.onGround) {
        player.velocity.y -= 0.012; // немного сильнее гравитация для падения с высоты
    }

    // Направление движения
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    direction.y = 0;
    direction.normalize();

    const right = new THREE.Vector3();
    right.crossVectors(camera.up, direction).normalize();

    // Применяем управление
    player.velocity.x = right.x * moveX * player.speed + direction.x * (-moveZ) * player.speed;
    player.velocity.z = right.z * moveX * player.speed + direction.z * (-moveZ) * player.speed;

    // Обновляем позицию
    player.position.add(player.velocity);

    // Столкновения
    checkCollision();

    // Респавн, если упал слишком низко
    if (player.position.y < -50) {
        player.position.set(0, 50, 0);
        player.velocity.set(0, 0, 0);
    }

    // Обновляем камеру
    camera.position.copy(player.position);

    renderer.render(scene, camera);
}

// Адаптация
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Старт
drawJoystick();
animate();
