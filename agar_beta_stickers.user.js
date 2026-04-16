// ==UserScript==
// @name         Agar.su Beta - Reaction Stickers
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Добавляет механику стикеров реакций на шаре игрока через нажатие на цифры 1-9 (как на agar.su)
// @author       You
// @match        https://agar.su/beta*
// @match        https://agar.su/beta/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // Ждём пока CORE инициализируется
    function waitForCore(callback) {
        const check = setInterval(() => {
            if (window.CORE && window.CORE.net && window.CORE.app) {
                clearInterval(check);
                callback();
            }
        }, 100);
    }

    // Состояние стикеров
    let currentSticker = null;
    let stickerCooldown = false;
    let stickerCooldownTimer = null;

    // Функция отправки стикера на сервер
    function sendSticker(stickerId, action) {
        if (window.CORE && window.CORE.net && window.CORE.net.ws && window.CORE.net.ws.readyState === WebSocket.OPEN) {
            const msg = new DataView(new ArrayBuffer(3));
            msg.setUint8(0, 200);      // opcode для стикеров (как на agar.su)
            msg.setUint8(1, stickerId); // ID стикера (1-9)
            msg.setUint8(2, action ? 1 : 0); // 1 = показать, 0 = скрыть
            window.CORE.net.ws.send(msg.buffer);
        }
    }

    // Показать стикер над клеткой
    function showStickerOverCell(stickerId) {
        if (!window.CORE || !window.CORE.app) return;

        const ownedCells = window.CORE.app.ownedCells;
        if (!ownedCells || ownedCells.length === 0) return;

        // Применяем стикер ко всем клеткам игрока
        for (let i = 0; i < ownedCells.length; i++) {
            const cell = window.CORE.app.cellsByID.get(ownedCells[i]);
            if (cell && cell.sprite) {
                cell.currentSticker = stickerId;
                cell.stickerActive = true;

                // Если есть спрайт стикера - показываем
                if (cell.stickerSprite) {
                    cell.stickerSprite.visible = true;
                } else {
                    // Создаём спрайт стикера если нет
                    createStickerSprite(cell, stickerId);
                }
            }
        }
    }

    // Создать спрайт стикера
    function createStickerSprite(cell, stickerId) {
        if (!PIXI || !cell || !cell.sprite) return;

        // URL для стикеров (можно заменить на свои)
        const stickerUrls = {
            1: 'https://api.agar.su/stickers/1.png',
            2: 'https://api.agar.su/stickers/2.png',
            3: 'https://api.agar.su/stickers/3.png',
            4: 'https://api.agar.su/stickers/4.png',
            5: 'https://api.agar.su/stickers/5.png',
            6: 'https://api.agar.su/stickers/6.png',
            7: 'https://api.agar.su/stickers/7.png',
            8: 'https://api.agar.su/stickers/8.png',
            9: 'https://api.agar.su/stickers/9.png'
        };

        try {
            const texture = PIXI.Texture.from(stickerUrls[stickerId] || stickerUrls[1]);
            const stickerSprite = new PIXI.Sprite(texture);
            stickerSprite.anchor.set(0.5);
            stickerSprite.scale.set(0.5); // Размер стикера
            stickerSprite.zIndex = 100; // Поверх всего
            stickerSprite.visible = true;

            cell.sprite.addChild(stickerSprite);
            cell.stickerSprite = stickerSprite;
        } catch (e) {
            console.warn('Не удалось создать спрайт стикера:', e);
        }
    }

    // Скрыть стикер
    function hideSticker() {
        if (!window.CORE || !window.CORE.app) return;

        const ownedCells = window.CORE.app.ownedCells;
        if (!ownedCells || ownedCells.length === 0) return;

        for (let i = 0; i < ownedCells.length; i++) {
            const cell = window.CORE.app.cellsByID.get(ownedCells[i]);
            if (cell) {
                cell.currentSticker = null;
                cell.stickerActive = false;

                if (cell.stickerSprite) {
                    cell.stickerSprite.visible = false;
                }
            }
        }
    }

    // Обработчик нажатия клавиш
    function handleKeyDown(event) {
        if (!window.CORE || !window.CORE.net) return;

        // Проверяем что игра активна и игрок не печатает в чате
        const isTyping = document.activeElement.tagName === 'INPUT' ||
                        document.activeElement.id === 'chat-field';

        if (isTyping) return;

        const keyCode = event.keyCode;

        // Цифры 1-9 (коды 49-57)
        if (keyCode >= 49 && keyCode <= 57) {
            const stickerId = keyCode - 48; // Преобразуем в номер 1-9

            if (!stickerCooldown && currentSticker !== stickerId) {
                // Если уже есть активный стикер - скрываем его
                if (currentSticker !== null) {
                    sendSticker(currentSticker, false);
                    hideSticker();
                }

                // Показываем новый стикер
                currentSticker = stickerId;
                sendSticker(stickerId, true);
                showStickerOverCell(stickerId);

                // Активируем задержку (cooldown) чтобы избежать спама
                stickerCooldown = true;
                if (stickerCooldownTimer) clearTimeout(stickerCooldownTimer);
                stickerCooldownTimer = setTimeout(() => {
                    stickerCooldown = false;
                }, 300); // 300мс задержка
            }
        }
    }

    // Обработчик отпускания клавиш
    function handleKeyUp(event) {
        if (!window.CORE || !window.CORE.net) return;

        const keyCode = event.keyCode;

        // Цифры 1-9 (коды 49-57)
        if (keyCode >= 49 && keyCode <= 57) {
            const stickerId = keyCode - 48;

            if (currentSticker === stickerId) {
                currentSticker = null;
                sendSticker(stickerId, false);
                hideSticker();
            }
        }
    }

    // Основная функция инициализации
    function init() {
        console.log('[Stickers] Инициализация системы стикеров...');

        // Добавляем слушатели событий
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);

        // Также слушаем blur окна чтобы сбрасывать стикеры
        window.addEventListener('blur', () => {
            if (currentSticker !== null) {
                sendSticker(currentSticker, false);
                hideSticker();
                currentSticker = null;
            }
        });

        console.log('[Stickers] Система стикеров активирована! Используйте цифры 1-9 для показа стикеров.');
    }

    // Запускаем после инициализации CORE
    waitForCore(init);

})();
