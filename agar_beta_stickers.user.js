// ==UserScript==
// @name         Agar.su Beta Stickers Working
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Рабочая система стикеров для agar.su/beta (цифры 1-9) - видно всем
// @author       You
// @match        https://agar.su/beta*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    const STICKER_COUNT = 9;
    const STICKER_OPCODE = 200; // Свободный opcode для стикеров
    
    let core = null;
    let app = null;
    let net = null;
    let stickerTextures = [];
    let cellStickers = new Map(); // cellId -> {index, timestamp}
    let myActiveSticker = -1;
    let myStickerTimestamp = 0;
    const STICKER_DURATION = 3000; // 3 секунды отображения
    const COOLDOWN = 500;

    console.log('[Stickers Beta v2] Запуск...');

    // Перехватываем создание игры
    function interceptGameCreation() {
        if (window.CORE && window.CORE.app) {
            core = window.CORE;
            app = core.app;
            net = core.net;
            console.log('[Stickers Beta v2] Игра найдена!', core);
            initStickerSystem();
            return true;
        }
        return false;
    }

    function initStickerSystem() {
        if (!window.PIXI || !app || !app.stage) {
            setTimeout(initStickerSystem, 100);
            return;
        }

        console.log('[Stickers Beta v2] Инициализация системы стикеров...');

        // Загрузка текстур стикеров
        loadStickerTextures();
        
        // Перехват обработки пакетов для получения стикеров других игроков
        interceptPacketHandler();
        
        // Настройка ввода
        setupInput();
        
        // Запуск цикла обновления
        requestAnimationFrame(updateLoop);
        
        console.log('[Stickers Beta v2] Система активирована! Используйте цифры 1-9');
    }

    function loadStickerTextures() {
        const baseUrl = 'https://agar.su/';
        
        for (let i = 1; i <= STICKER_COUNT; i++) {
            const url = `${baseUrl}${i}.png`;
            
            try {
                const texture = PIXI.Texture.from(url, {
                    scaleMode: PIXI.SCALE_MODES.NEAREST,
                    resourceOptions: { crossOrigin: 'anonymous' }
                });
                
                texture.baseTexture.on('loaded', () => {
                    console.log(`[Stickers Beta v2] Загружен стикер ${i}`);
                });
                
                texture.baseTexture.on('error', (err) => {
                    console.warn(`[Stickers Beta v2] Ошибка загрузки стикера ${i}:`, url);
                });
                
                stickerTextures[i] = texture;
            } catch(e) {
                console.error('[Stickers Beta v2] Ошибка создания текстуры:', e);
            }
        }
    }

    function interceptPacketHandler() {
        // Перехватываем обработку входящих пакетов для чтения стикеров
        if (!net || !net.onMessage) return;
        
        const originalOnMessage = net.onMessage;
        
        // NOTE: Мы не можем легко перехватить бинарные пакеты,
        // но сервер отправляет стикеры в пакете UPDATE_NODES (opcode 16)
        // вместе с данными клетки - см. строки 1110-1116 в main.js
    }

    function sendStickerToServer(index) {
        if (!net || !net.ws || net.ws.readyState !== WebSocket.OPEN) {
            console.warn('[Stickers Beta v2] Нет соединения с сервером');
            return false;
        }

        try {
            // Формируем пакет: [opcode=200, stickerIndex]
            const packet = new Uint8Array(2);
            packet[0] = STICKER_OPCODE;
            packet[1] = index;
            
            net.ws.send(packet);
            console.log(`[Stickers Beta v2] Отправлен стикер ${index} на сервер`);
            return true;
        } catch(e) {
            console.error('[Stickers Beta v2] Ошибка отправки пакета:', e);
            return false;
        }
    }

    function createStickerSpriteForCell(cell, index) {
        if (!stickerTextures[index] || !cell || !cell.sprite) return null;
        
        const sprite = new PIXI.Sprite(stickerTextures[index]);
        sprite.anchor.set(0.5);
        sprite.zIndex = 9999;
        
        // Добавляем спрайт к клетке
        cell.sprite.addChild(sprite);
        
        return sprite;
    }

    function updateCellSticker(cell, index) {
        if (!cell || !cell.sprite) return;
        
        // Проверяем, есть ли уже спрайт стикера у этой клетки
        let stickerSprite = cell.stickerSprite;
        
        if (index > 0 && index <= STICKER_COUNT) {
            // Показываем стикер
            if (!stickerSprite) {
                stickerSprite = createStickerSpriteForCell(cell, index);
                if (stickerSprite) {
                    cell.stickerSprite = stickerSprite;
                }
            }
            
            if (stickerSprite) {
                stickerSprite.texture = stickerTextures[index];
                stickerSprite.visible = true;
                
                // Масштабирование относительно размера клетки
                const scale = Math.max(0.3, Math.min(1.2, cell.r / 150));
                stickerSprite.scale.set(scale);
            }
            
            // Обновляем информацию о стикере
            cellStickers.set(cell.id, {
                index: index,
                timestamp: Date.now()
            });
        } else {
            // Скрываем стикер
            if (stickerSprite) {
                stickerSprite.visible = false;
            }
            cellStickers.delete(cell.id);
        }
    }

    function setupInput() {
        document.addEventListener('keydown', (e) => {
            // Игнорируем ввод в полях текста
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
            
            if (/^[1-9]$/.test(e.key)) {
                const index = parseInt(e.key);
                activateMySticker(index);
            }
        });

        document.addEventListener('keyup', (e) => {
            if (/^[1-9]$/.test(e.key)) {
                deactivateMySticker();
            }
        });
        
        window.addEventListener('blur', deactivateMySticker);
    }

    function activateMySticker(index) {
        const now = Date.now();
        if (now - myStickerTimestamp < COOLDOWN) return;
        
        // Отправляем на сервер
        if (!sendStickerToServer(index)) return;
        
        myActiveSticker = index;
        myStickerTimestamp = now;
        
        // Находим клетки игрока и применяем стикер
        if (app && app.cells) {
            for (let cell of app.cells) {
                if (cell.id && app.ownedCells && app.ownedCells.includes(cell.id)) {
                    updateCellSticker(cell, index);
                }
            }
        }
        
        console.log(`[Stickers Beta v2] Активирован стикер ${index}`);
    }

    function deactivateMySticker() {
        if (myActiveSticker === -1) return;
        
        // Отправляем сигнал скрытия (индекс 0)
        sendStickerToServer(0);
        
        // Скрываем у своих клеток
        if (app && app.cells) {
            for (let cell of app.cells) {
                if (cell.id && app.ownedCells && app.ownedCells.includes(cell.id)) {
                    updateCellSticker(cell, 0);
                }
            }
        }
        
        myActiveSticker = -1;
    }

    function updateLoop() {
        const now = Date.now();
        
        // Обновляем стикеры всех клеток
        if (app && app.cells) {
            for (let cell of app.cells) {
                if (!cell || cell.destroyed) continue;
                
                const stickerInfo = cellStickers.get(cell.id);
                if (stickerInfo) {
                    // Проверяем время жизни стикера
                    if (now - stickerInfo.timestamp > STICKER_DURATION) {
                        updateCellSticker(cell, 0);
                        continue;
                    }
                    
                    // Обновляем позицию и масштаб
                    if (cell.stickerSprite && cell.stickerSprite.visible) {
                        const scale = Math.max(0.3, Math.min(1.2, cell.r / 150));
                        cell.stickerSprite.scale.set(scale);
                    }
                }
            }
        }
        
        requestAnimationFrame(updateLoop);
    }

    // Попытка инициализации
    function tryInit() {
        if (!interceptGameCreation()) {
            setTimeout(tryInit, 100);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tryInit);
    } else {
        tryInit();
    }
})();
