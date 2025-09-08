// Инициализация Three.js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x87CEEB);
document.getElementById('gameContainer').appendChild(renderer.domElement);

// Свет
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(20, 50, 30);
scene.add(directionalLight);

// Загрузка текстур
const textureLoader = new THREE.TextureLoader();

const brickTexture = textureLoader.load('https://avatars.mds.yandex.net/i?id=cd19cdb11d3fdb1ae1927afb09eea85c_l-16409040-images-thumbs&n=13');
brickTexture.wrapS = THREE.RepeatWrapping;
brickTexture.wrapT = THREE.RepeatWrapping;
brickTexture.repeat.set(2, 2);

const houseTexture = textureLoader.load('https://avatars.mds.yandex.net/i?id=bcc62e7653b6b1e068912ae7e7a0ad5c_l-2925590-images-thumbs&n=13');
houseTexture.wrapS = THREE.RepeatWrapping;
houseTexture.wrapT = THREE.RepeatWrapping;
houseTexture.repeat.set(1, 1);

// Физика игрока
let player = {
    height: 1.8,
    radius: 0.4,
    velocity: new THREE.Vector3(0, 0, 0),
    position: new THREE.Vector3(0, 0, 0),
    onGround: false,
    speed: 0.15,
    jumpStrength: 0.25
};

// Камера = игрок
camera.position.set(0, player.height, 0);
scene.add(camera); // Добавляем камеру в сцену как объект

// Коллекция для столкновений
const collidableMeshes = [];

function createWall(width, height, depth, x, y, z, rotY = 0, texture = brickTexture, isHouse = false) {
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshStandardMaterial({ map: texture });
    const wall = new THREE.Mesh(geometry, material);
    wall.position.set(x, y, z);
    wall.rotation.y = rotY;
    wall.userData = { isHouse: isHouse }; // Для дверей позже
    scene.add(wall);
    collidableMeshes.push(wall);
    return wall;
}

// Создание платформы (земли)
function createPlatform(width, depth, x, z) {
    const geometry = new THREE.PlaneGeometry(width, depth);
    const material = new THREE.MeshStandardMaterial({ 
        map: brickTexture, 
        side: THREE.DoubleSide 
    });
    const platform = new THREE.Mesh(geometry, material);
    platform.rotation.x = -Math.PI / 2;
    platform.position.set(x, 0, z);
    scene.add(platform);
    collidableMeshes.push(platform);
}

// Создание дома с дверным проемом
function createHouse(x, z) {
    const houseWidth = 6;
    const houseDepth = 6;
    const houseHeight = 5;
    const wallThickness = 0.5;

    // Пол дома
    createPlatform(houseWidth, houseDepth, x, z);

    // Стены дома
    createWall(houseWidth, houseHeight, wallThickness, x, houseHeight/2, z - houseDepth/2 + wallThickness/2, 0, houseTexture, true); // Передняя
    createWall(houseWidth, houseHeight, wallThickness, x, houseHeight/2, z + houseDepth/2 - wallThickness/2, 0, houseTexture, true);  // Задняя
    createWall(wallThickness, houseHeight, houseDepth - 2, x - houseWidth/2 + wallThickness/2, houseHeight/2, z, 0, houseTexture, true); // Левая (с проемом)
    createWall(wallThickness, houseHeight, houseDepth - 2, x + houseWidth/2 - wallThickness/2, houseHeight/2, z, 0, houseTexture, true); // Правая (с проемом)

    // Крыша
    const roofGeometry = new THREE.ConeGeometry(houseWidth + 0.5, 3, 4);
    const roofMaterial = new THREE.MeshStandardMaterial({ color: 0x5c4033 });
    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
    roof.position.set(x, houseHeight + 1.5, z);
    roof.rotation.y = Math.PI / 4;
    scene.add(roof);
}

// Большая карта
createPlatform(100, 100, 0, 0); // Основная земля

// Дома
createHouse(15, 15);
createHouse(-15, 20);
createHouse(20, -15);
createHouse(-20, -20);

// Дополнительные стены-ограждения
for (let i = -50; i <= 50; i += 10) {
    createWall(0.5, 3, 10, i, 1.5, -50);
    createWall(0.5, 3, 10, i, 1.5, 50);
    createWall(10, 3, 0.5, -50, 1.5, i);
    createWall(10, 3, 0.5, 50, 1.5, i);
}

// Управление
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

// Прыжок по тапу на экран (кроме джойстика)
document.addEventListener('touchend', (e) => {
    if (!joystickActive && canJump) {
        player.velocity.y = player.jumpStrength;
        player.onGround = false;
        canJump = false;
    }
});

// Проверка столкновений AABB
function checkCollision() {
    const playerBottom = player.position.y - player.height / 2;
    const playerTop = player.position.y + player.height / 2;
    const playerLeft = player.position.x - player.radius;
    const playerRight = player.position.x + player.radius;
    const playerFront = player.position.z - player.radius;
    const playerBack = player.position.z + player.radius;

    player.onGround = false;

    for (let mesh of collidableMeshes) {
        const box = new THREE.Box3().setFromObject(mesh);
        const { min, max } = box;

        // Проверка пересечения по горизонтали
        if (playerRight <= min.x || playerLeft >= max.x ||
            playerBack <= min.z || playerFront >= max.z) {
            continue;
        }

        // Если это пол — проверяем снизу
        if (Math.abs(mesh.rotation.x + Math.PI / 2) < 0.1) { // Это пол
            if (playerBottom <= max.y && playerBottom + player.velocity.y >= max.y) {
                player.position.y = max.y + player.height / 2;
                player.velocity.y = 0;
                player.onGround = true;
                canJump = true;
            }
        } else {
            // Вертикальные стены — проверяем по X и Z
            if (playerRight > min.x && playerLeft < min.x && player.velocity.x > 0) {
                player.position.x = min.x - player.radius;
                player.velocity.x = 0;
            }
            if (playerLeft < max.x && playerRight > max.x && player.velocity.x < 0) {
                player.position.x = max.x + player.radius;
                player.velocity.x = 0;
            }
            if (playerBack > min.z && playerFront < min.z && player.velocity.z > 0) {
                player.position.z = min.z - player.radius;
                player.velocity.z = 0;
            }
            if (playerFront < max.z && playerBack > max.z && player.velocity.z < 0) {
                player.position.z = max.z + player.radius;
                player.velocity.z = 0;
            }
        }
    }
}

// Анимация и физика
function animate() {
    requestAnimationFrame(animate);

    // Гравитация
    if (!player.onGround) {
        player.velocity.y -= 0.01; // гравитация
    }

    // Получаем направление движения
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    direction.y = 0; // Игнорируем вертикаль для движения
    direction.normalize();

    const right = new THREE.Vector3();
    right.crossVectors(camera.up, direction).normalize();

    // Применяем управление
    player.velocity.x = right.x * moveX * player.speed + direction.x * (-moveZ) * player.speed;
    player.velocity.z = right.z * moveX * player.speed + direction.z * (-moveZ) * player.speed;

    // Обновляем позицию
    player.position.add(player.velocity);

    // Проверка столкновений
    checkCollision();

    // Ограничение падения "вниз мира"
    if (player.position.y < -10) {
        player.position.set(0, 5, 0); // Респавн
        player.velocity.set(0, 0, 0);
    }

    // Применяем позицию к камере
    camera.position.copy(player.position);

    renderer.render(scene, camera);
}

// Адаптация экрана
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Старт
drawJoystick();
animate();
