// ==UserScript==
// @name         Agar.su Beta Stickers Fix
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Исправленная система стикеров для agar.su/beta (цифры 1-9)
// @author       You
// @match        https://agar.su/beta*
// @match        https://agar.su/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';

    const BASE_URL = 'https://agar.su/';
    const STICKER_COUNT = 9;
    
    let renderer = null;
    let stickerSprites = [];
    let activeStickerIndex = -1;
    let stickerContainer = null;
    let lastPressTime = 0;
    const COOLDOWN = 300;

    console.log('[Stickers Beta] Инициализация...');

    function findGameObjects() {
        if (window.app && window.app.stage) {
            renderer = window.app;
            return true;
        }
        
        const names = ['game', 'app', 'main', 'view', 'renderer'];
        for (let name of names) {
            if (window[name]) {
                if (window[name].stage) {
                    renderer = window[name];
                    return true;
                }
                if (window[name].renderer && window[name].stage) {
                    renderer = window[name];
                    return true;
                }
            }
        }
        return false;
    }

    function initStickers() {
        if (!window.PIXI) {
            setTimeout(initStickers, 200);
            return;
        }
        
        if (!findGameObjects()) {
            setTimeout(initStickers, 500);
            return;
        }

        console.log('[Stickers Beta] Объект найден:', renderer);

        if (!stickerContainer) {
            stickerContainer = new PIXI.Container();
            stickerContainer.zIndex = 9999;
            renderer.stage.addChild(stickerContainer);
            renderer.stage.sortableChildren = true;
        }

        // Загрузка текстур с несколькими попытками путей
        for (let i = 1; i <= STICKER_COUNT; i++) {
            // Пробуем разные пути
            const paths = [
                `${BASE_URL}${i}.png`,
                `${BASE_URL}img/${i}.png`,
                `${BASE_URL}stickers/${i}.png`,
                `https://agar.su/img/stickers/${i}.png`
            ];
            
            let loaded = false;
            for (let url of paths) {
                if (loaded) break;
                
                try {
                    const base = new PIXI.BaseTexture.from(url, {
                        scaleMode: PIXI.SCALE_MODES.NEAREST,
                        resourceOptions: { crossOrigin: 'anonymous' }
                    });
                    
                    base.once('loaded', () => {
                        loaded = true;
                        console.log(`[Stickers Beta] Загружен стикер ${i}: ${url}`);
                    });
                    
                    base.once('error', () => {
                        // Тихая ошибка, пробуем следующий URL
                    });

                    const tex = new PIXI.Texture(base);
                    const sprite = new PIXI.Sprite(tex);
                    sprite.anchor.set(0.5);
                    sprite.visible = false;
                    sprite.scale.set(0.5);
                    stickerContainer.addChild(sprite);
                    stickerSprites[i] = sprite;
                    break;
                } catch(e) {
                    continue;
                }
            }
        }

        setupInput();
        console.log('[Stickers Beta] Готово! Жмите 1-9');
    }

    function setupInput() {
        document.addEventListener('keydown', (e) => {
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
            
            if (/^[1-9]$/.test(e.key)) {
                showSticker(parseInt(e.key));
            }
        });

        document.addEventListener('keyup', (e) => {
            if (/^[1-9]$/.test(e.key)) hideSticker();
        });
        
        window.addEventListener('blur', hideSticker);
    }

    function showSticker(index) {
        const now = Date.now();
        if (now - lastPressTime < COOLDOWN) return;
        lastPressTime = now;

        if (!stickerSprites[index]) return;

        // Отправка на сервер
        try {
            const ws = window.ws || window.socket;
            if (ws && ws.readyState === WebSocket.OPEN) {
                const packet = new Uint8Array(2);
                packet[0] = 200;
                packet[1] = index;
                ws.send(packet);
            }
        } catch(e) {}

        // Поиск клетки игрока
        let myCell = null;
        const arrays = ['cells', 'myCells', 'nodes', 'balls', 'allCells'];
        
        for (let name of arrays) {
            if (window[name] && Array.isArray(window[name]) && window[name].length > 0) {
                // Ищем самую большую
                let largest = null;
                let max = 0;
                for (let c of window[name]) {
                    const s = c.size || c.radius || 0;
                    if (s > max) { max = s; largest = c; }
                }
                if (largest) { myCell = largest; break; }
            }
        }

        const sprite = stickerSprites[index];
        sprite.visible = true;
        
        if (myCell && myCell.x !== undefined) {
            const zoom = window.viewZoom || window.cameraZoom || 1;
            const camX = window.viewX || window.cameraX || 0;
            const camY = window.viewY || window.cameraY || 0;
            
            sprite.x = (myCell.x - camX) * zoom + window.innerWidth / 2;
            sprite.y = (myCell.y - camY) * zoom + window.innerHeight / 2;
            
            const size = myCell.size || myCell.radius * 2 || 100;
            sprite.scale.set(Math.max(0.3, Math.min(1.5, size / 200)));
        } else {
            sprite.x = window.innerWidth / 2;
            sprite.y = window.innerHeight / 2;
            sprite.scale.set(1);
        }
        
        activeStickerIndex = index;
    }

    function hideSticker() {
        if (activeStickerIndex !== -1 && stickerSprites[activeStickerIndex]) {
            stickerSprites[activeStickerIndex].visible = false;
            activeStickerIndex = -1;
        }
    }

    // Автообновление позиции
    function loop() {
        if (activeStickerIndex !== -1 && stickerSprites[activeStickerIndex]) {
            let myCell = null;
            const arrays = ['cells', 'myCells', 'nodes'];
            for (let name of arrays) {
                if (window[name] && window[name].length > 0) {
                    myCell = window[name][0];
                    break;
                }
            }
            
            if (myCell && myCell.x !== undefined) {
                const zoom = window.viewZoom || 1;
                const camX = window.viewX || 0;
                const camY = window.viewY || 0;
                
                stickerSprites[activeStickerIndex].x = (myCell.x - camX) * zoom + window.innerWidth / 2;
                stickerSprites[activeStickerIndex].y = (myCell.y - camY) * zoom + window.innerHeight / 2;
            }
        }
        requestAnimationFrame(loop);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStickers);
    } else {
        initStickers();
    }
    
    loop();
})();
