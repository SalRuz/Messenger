import telebot
import random
import json
import os
import logging
import time
import requests
import uuid
import threading
import math
from random import choices
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from urllib.parse import quote
from io import BytesIO
# 🔧 Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_log.txt', encoding='utf-8')
    ])
logger = logging.getLogger(__name__)
CASINO_MULTIPLIERS = [0, 1.5, 2, 3, 5, 10]
CASINO_EMOJIS = {
    0: "💀",
    1.5: "🪙",
    2: "💰",
    3: "💎",
    5: "🔥",
    10: "✨"
}
CASINO_WEIGHTS = [50, 30, 15, 4, 0.9, 0.1]
WELCOME_STICKER = "CAACAgIAAxkBAAE8CI9o4Wj4OQ-OP86s95umuhppGvbnEQACR38AAqI86UhvlgNyXfulxzYE"
GOODBYE_STICKER = "CAACAgIAAxkBAAE8CJdo4WkgIeW6ZDCSmRTON-ef8Na35gACm30AAitHEUmiO_MpbV6K7TYE"
BOT_TOKEN = '8512207770:AAEKLtYEph7gleybGhF2lc7Gwq82Kj1yedM'
# 📁 Имена файлов
SAVE_FILE = "names.json"
KIDNAP_FILE = "kidnap_data.json"
USER_CACHE_FILE = "user_cache.json"
TRIGGERS_FILE = "triggers.json"
TRIGGER_ACCESS_FILE = "trigger_access.json"
INVENTORY_FILE = "inventory.json"
STEAL_TIMERS_FILE = "steal_timers.json"
MUTED_USERS_FILE = "muted_users.json"
CASINO_COOLDOWN_FILE = "casino_cooldown.json"
CASINO_PROFIT_STATS_FILE = "casino_profit_stats.json"
OFFLINE_USERS_FILE = "offline_users.json"
FEATURES_FILE = "features.json"
PAUSED_TIMERS_FILE = "paused_timers.json"
EXECUT_QUEUE_FILE = "execut_queue.json"
DAILY_REPORTS_FILE = "daily_reports.json"
MINESWEEPER_FILE = "minesweeper_data.json"
MINESWEEPER_REWARD = 300
MINESWEEPER_FIELD_SIZE = 5
MINESWEEPER_MINES_COUNT = 7
MINESWEEPER_SAFE_TO_WIN = 8 
# 🧠 Глобальные переменные
user_custom_names = {}
chat_members_cache = {}
last_kidnap_attempt = {}
kidnap_bags = {}
kidnap_points = {}
handcuffed_players = {}
shield_used = {}
user_coins = {}
last_job_attempt = {}
pending_knb_games = {}
knb_stats = {}
chat_triggers = {}
trigger_access = {}
user_inventory = {}
steal_timers = {}
muted_users = {}
last_casino_attempt = {}
casino_profit_stats = {}
pending_triggers = {}
offline_users = {}
chat_features = {}
paused_timers = {}
execut_queue = {}
daily_reports = {} 
minesweeper_data = {} 
minesweeper_stats = {}
image_search_cache = {} 
def create_bot():
    try:
        return telebot.TeleBot(BOT_TOKEN, parse_mode=None)
    except Exception as e:
        logger.error(f"Ошибка создания бота: {e}")
        time.sleep(5)
        return create_bot()
bot = create_bot()
# 📂 Загрузка данных
def load_minesweeper_data():
    global minesweeper_data, minesweeper_stats
    if os.path.exists(MINESWEEPER_FILE):
        try:
            with open(MINESWEEPER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                minesweeper_data = {int(chat_id): info for chat_id, info in data.get("events", {}).items()}
                minesweeper_stats = {
                    int(chat_id): {int(uid): stats for uid, stats in users.items()}
                    for chat_id, users in data.get("stats", {}).items()
                }
                logger.info(f"Загружены данные Сапёра для {len(minesweeper_data)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных Сапёра: {e}")
            minesweeper_data = {}
            minesweeper_stats = {}
    else:
        minesweeper_data = {}
        minesweeper_stats = {}
def load_daily_reports():
    global daily_reports
    if os.path.exists(DAILY_REPORTS_FILE):
        try:
            with open(DAILY_REPORTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                daily_reports = {int(chat_id): info for chat_id, info in data.items()}
                logger.info(f"Загружено {len(daily_reports)} ежедневных отчётов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки ежедневных отчётов: {e}")
            daily_reports = {}
    else:
        daily_reports = {}
def load_execut_queue():
    global execut_queue
    if os.path.exists(EXECUT_QUEUE_FILE):
        try:
            with open(EXECUT_QUEUE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                execut_queue = {int(chat_id): user_ids for chat_id, user_ids in data.items()}
                logger.info(f"Загружена очередь /execut для {len(execut_queue)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки очереди /execut: {e}")
            execut_queue = {}
    else:
        execut_queue = {}
def load_paused_timers():
    global paused_timers
    if os.path.exists(PAUSED_TIMERS_FILE):
        with open(PAUSED_TIMERS_FILE) as f:
            paused_timers = {int(k): v for k, v in json.load(f).items()}
def load_features():
    global chat_features
    if os.path.exists(FEATURES_FILE):
        try:
            with open(FEATURES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                chat_features = {
                    int(chat_id): {
                        "kidnap_game": info.get("kidnap_game", True),
                    }
                    for chat_id, info in data.items()
                }
                logger.info(f"Загружены настройки функций для {len(chat_features)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек функций: {e}")
            chat_features = {}
    else:
        chat_features = {}
def load_offline_users():
    global offline_users
    if os.path.exists(OFFLINE_USERS_FILE):
        try:
            with open(OFFLINE_USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                offline_users = {
                    int(chat_id): set(map(int, users))
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружено {sum(len(v) for v in offline_users.values())} пользователей в режиме offline.")
        except Exception as e:
            logger.error(f"Ошибка загрузки offline-пользователей: {e}")
            offline_users = {}
    else:
        offline_users = {}
def load_casino_data():
    global last_casino_attempt, casino_profit_stats
    if os.path.exists(CASINO_COOLDOWN_FILE):
        try:
            with open(CASINO_COOLDOWN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_casino_attempt = {
                    int(chat_id): {int(uid): ts for uid, ts in users.items()}
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружен кулдаун казино для {len(last_casino_attempt)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки кулдауна казино: {e}")
            last_casino_attempt = {}
    else:
        last_casino_attempt = {}
    if os.path.exists(CASINO_PROFIT_STATS_FILE):
        try:
            with open(CASINO_PROFIT_STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                casino_profit_stats = {
                    int(chat_id): {int(uid): profit for uid, profit in users.items()}
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружена статистика казино для {len(casino_profit_stats)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики казино: {e}")
            casino_profit_stats = {}
    else:
        casino_profit_stats = {}
def load_muted_users():
    global muted_users
    if os.path.exists(MUTED_USERS_FILE):
        try:
            with open(MUTED_USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                muted_users = {
                    int(chat_id): set(map(int, users))
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружено {sum(len(v) for v in muted_users.values())} замученных.")
        except Exception as e:
            logger.error(f"Ошибка загрузки замученных: {e}")
            muted_users = {}
    else:
        muted_users = {}
def load_steal_timers():
    global steal_timers
    if os.path.exists(STEAL_TIMERS_FILE):
        try:
            with open(STEAL_TIMERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                steal_timers = {
                    int(chat_id): {
                        tuple(map(int, pair.split(","))): ts
                        for pair, ts in pairs.items()
                    }
                    for chat_id, pairs in data.items()
                }
                logger.info(f"Загружено {sum(len(v) for v in steal_timers.values())} таймеров кражи.")
        except Exception as e:
            logger.error(f"Ошибка загрузки таймеров кражи: {e}")
            steal_timers = {}
    else:
        steal_timers = {}
def load_names():
    global user_custom_names
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                user_custom_names = json.load(f)
                logger.info(f"Загружено {len(user_custom_names)} имён.")
        except Exception as e:
            logger.error(f"Ошибка загрузки имён: {e}")
            user_custom_names = {}
    else:
        user_custom_names = {}
def load_kidnap_data():
    global last_kidnap_attempt, kidnap_bags, kidnap_points, handcuffed_players
    if os.path.exists(KIDNAP_FILE):
        try:
            with open(KIDNAP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_kidnap_attempt = {int(chat_id): {int(uid): ts for uid, ts in users.items()}
                for chat_id, users in data.get("last_kidnap_attempt", {}).items()
                }
                kidnap_bags_raw = data.get("kidnap_bags", {})
                kidnap_bags = {
                    int(chat_id): {
                        int(kidnapper_id): set(victims) for kidnapper_id, victims in kidnappers.items()
                    } for chat_id, kidnappers in kidnap_bags_raw.items()
                }
                kidnap_points = {
                    int(chat_id): {int(uid): pts for uid, pts in users.items()}
                    for chat_id, users in data.get("kidnap_points", {}).items()
                }
                handcuffed_raw = data.get("handcuffed_players", {})
                handcuffed_players = {
                    int(chat_id): set(users) for chat_id, users in handcuffed_raw.items()
                }
                logger.info(f"Загружены данные похищений: {len(kidnap_points)} чатов с очками, {len(kidnap_bags)} активных мешков.")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных похищений: {e}")
            last_kidnap_attempt = {}
            kidnap_bags = {}
            kidnap_points = {}
            handcuffed_players = {}
    else:
        last_kidnap_attempt = {}
        kidnap_bags = {}
        kidnap_points = {}
        handcuffed_players = {}
def load_user_cache():
    global chat_members_cache
    if os.path.exists(USER_CACHE_FILE):
        try:
            with open(USER_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                chat_members_cache = {
                    int(chat_id): {
                        int(user_id): user_data for user_id, user_data in users.items()
                    }
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружен кэш пользователей для {len(chat_members_cache)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша пользователей: {e}")
            chat_members_cache = {}
    else:
        chat_members_cache = {}
def load_coins():
    global user_coins
    if os.path.exists("coins.json"):
        try:
            with open("coins.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                user_coins = {
                    int(chat_id): {int(uid): int(math.ceil(float(bal))) for uid, bal in users.items()}
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружены монеты для {len(user_coins)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки монет: {e}")
            user_coins = {}
    else:
        user_coins = {}
def load_job_cooldown():
    global last_job_attempt
    if os.path.exists('job_cooldown.json'):
        try:
            with open('job_cooldown.json', "r", encoding="utf-8") as f:
                data = json.load(f)
                last_job_attempt = {
                    int(chat_id): {int(uid): ts for uid, ts in users.items()}
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружен кулдаун /job для {len(last_job_attempt)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки кулдауна /job: {e}")
            last_job_attempt = {}
    else:
        last_job_attempt = {}
def load_knb_stats():
    global knb_stats
    if os.path.exists("knb_stats.json"):
        try:
            with open("knb_stats.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                knb_stats = {
                    int(chat_id): {int(uid): wins for uid, wins in users.items()}
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружена статистика КНБ для {len(knb_stats)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики КНБ: {e}")
            knb_stats = {}
    else:
        knb_stats = {}
def load_triggers():
    global chat_triggers
    if os.path.exists(TRIGGERS_FILE):
        try:
            with open(TRIGGERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                chat_triggers = {}
                for chat_id_str, triggers in data.items():
                    chat_id = int(chat_id_str)
                    chat_triggers[chat_id] = {}
                    for phrase, trigger_data in triggers.items():
                      if isinstance(trigger_data, list):
                        chat_triggers[chat_id][phrase] = trigger_data
                      elif isinstance(trigger_data, str):  # старый формат (стикеры)
                        chat_triggers[chat_id][phrase] = [{"type": "sticker", "file_id": trigger_data}]
                      else:
                        chat_triggers[chat_id][phrase] = [trigger_data]
                logger.info(f"Загружено {sum(len(v) for v in chat_triggers.values())} триггеров.")
        except Exception as e:
            logger.error(f"Ошибка загрузки триггеров: {e}")
            chat_triggers = {}
    else:
        chat_triggers = {}
def load_trigger_access():
    global trigger_access
    if os.path.exists(TRIGGER_ACCESS_FILE):
        try:
            with open(TRIGGER_ACCESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                trigger_access = {
                    int(chat_id): {
                        "mode": info.get("mode", "creator"),
                        "allowed_users": [int(uid) for uid in info.get("allowed_users", [])]
                    }
                    for chat_id, info in data.items()
                }
                logger.info(f"Загружен доступ к триггерам для {len(trigger_access)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки доступа к триггерам: {e}")
            trigger_access = {}
    else:
        trigger_access = {}
def load_shield_data():
    global shield_used
    if os.path.exists('shield_data.json'):
        try:
            with open('shield_data.json', "r", encoding="utf-8") as f:
                data = json.load(f)
                shield_used = {int(chat_id): {int(uid): used for uid, used in users.items()}
                               for chat_id, users in data.get("used", {}).items()}
                logger.info(f"Загружены данные щитов: {len(shield_used)} чатов с флагами использования.")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных щитов: {e}")
            shield_used = {}
    else:
        shield_used = {}
def load_inventory():
    global user_inventory
    if os.path.exists(INVENTORY_FILE):
        try:
            with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_inventory = {
                    int(chat_id): {
                        int(uid): inv for uid, inv in users.items()
                    }
                    for chat_id, users in data.items()
                }
                logger.info(f"Загружен инвентарь для {len(user_inventory)} чатов.")
        except Exception as e:
            logger.error(f"Ошибка загрузки инвентаря: {e}")
            user_inventory = {}
    else:
        user_inventory = {}
# 💾 Сохранение данных
def save_minesweeper_data():
    try:
        data = {
            "events": {str(chat_id): info for chat_id, info in minesweeper_data.items()},
            "stats": {
                str(chat_id): {str(uid): stats for uid, stats in users.items()}
                for chat_id, users in minesweeper_stats.items()
            }
        }
        with open(MINESWEEPER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные Сапёра сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных Сапёра: {e}")
def save_daily_reports():
    try:
        data = {str(chat_id): info for chat_id, info in daily_reports.items()}
        with open(DAILY_REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Ежедневные отчёты сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения ежедневных отчётов: {e}")
def save_execut_queue():
    try:
        with open(EXECUT_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in execut_queue.items()}, f, ensure_ascii=False, indent=2)
        logger.info("Очередь /execut сохранена.")
    except Exception as e:
        logger.error(f"Ошибка сохранения очереди /execut: {e}")
def save_paused_timers():
    with open(PAUSED_TIMERS_FILE, "w") as f:
        json.dump({str(k): v for k, v in paused_timers.items()}, f)
def save_features():
    try:
        data = {
            str(chat_id): {
                "kidnap_game": info["kidnap_game"],
            }
            for chat_id, info in chat_features.items()
        }
        with open(FEATURES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Настройки функций сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек функций: {e}")
def save_offline_users():
    try:
        data_str = {
            str(chat_id): list(users)
            for chat_id, users in offline_users.items()
        }
        with open(OFFLINE_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Список offline-пользователей сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения offline-пользователей: {e}")
def save_casino_data():
    try:
        data_cd = {
            str(chat_id): {str(uid): ts for uid, ts in users.items()}
            for chat_id, users in last_casino_attempt.items()
        }
        with open(CASINO_COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(data_cd, f, ensure_ascii=False, indent=2)
        logger.info("Кулдаун казино сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения кулдауна казино: {e}")
def save_casino_profit_stats():
    try:
        data_stats = {
            str(chat_id): {str(uid): profit for uid, profit in users.items()}
            for chat_id, users in casino_profit_stats.items()
        }
        with open(CASINO_PROFIT_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_stats, f, ensure_ascii=False, indent=2)
        logger.info("Статистика казино сохранена.")
    except Exception as e:
        logger.error(f"Ошибка сохранения статистики казино: {e}")
def save_muted_users():
    try:
        data_str = {
            str(chat_id): list(users)
            for chat_id, users in muted_users.items()
        }
        with open(MUTED_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Список замученных сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения замученных: {e}")
def save_steal_timers():
    try:
        data_str = {
            str(chat_id): {
                f"{kidnapper_id},{victim_id}": ts
                for (kidnapper_id, victim_id), ts in pairs.items()
            }
            for chat_id, pairs in steal_timers.items()
        }
        with open(STEAL_TIMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Таймеры кражи сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения таймеров кражи: {e}")
def save_names():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(user_custom_names, f, ensure_ascii=False, indent=2)
        logger.info("Имена сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения имён: {e}")
def save_kidnap_data():
    try:
        bags_str = {
            str(chat_id): {
                str(kidnapper_id): list(victims) for kidnapper_id, victims in kidnappers.items()
            } for chat_id, kidnappers in kidnap_bags.items()
        }
        points_str = {
            str(chat_id): {str(uid): pts for uid, pts in users.items()}
            for chat_id, users in kidnap_points.items()
        }
        handcuffed_str = {
            str(chat_id): list(users) for chat_id, users in handcuffed_players.items()
        }
        data = {
            "last_kidnap_attempt": {str(chat_id): {str(uid): ts for uid, ts in users.items()}
            for chat_id, users in last_kidnap_attempt.items()
            },
            "kidnap_bags": bags_str,
            "kidnap_points": points_str,
            "handcuffed_players": handcuffed_str
        }
        with open(KIDNAP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные похищений сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных похищений: {e}")
def save_user_cache():
    try:
        cache_str = {
            str(chat_id): {
                str(user_id): user_data for user_id, user_data in users.items()
            }
            for chat_id, users in chat_members_cache.items()
        }
        with open(USER_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_str, f, ensure_ascii=False, indent=2)
        logger.info("Кэш пользователей сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения кэша пользователей: {e}")
def save_coins():
    try:
        data_str = {
            str(chat_id): {str(uid): bal for uid, bal in users.items()}
            for chat_id, users in user_coins.items()
        }
        with open("coins.json", "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Монеты сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения монет: {e}")
def save_job_cooldown():
    try:
        data_str = {
            str(chat_id): {str(uid): ts for uid, ts in users.items()}
            for chat_id, users in last_job_attempt.items()
        }
        with open('job_cooldown.json', "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Кулдаун /job сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения кулдауна /job: {e}")
def save_shield_data():
    try:
        data = {
            "used": {str(chat_id): {str(uid): used for uid, used in users.items()}
                     for chat_id, users in shield_used.items()}
        }
        with open('shield_data.json', "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные щитов сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных щитов: {e}")
def save_knb_stats():
    try:
        data_str = {
            str(chat_id): {str(uid): wins for uid, wins in users.items()}
            for chat_id, users in knb_stats.items()
        }
        with open("knb_stats.json", "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Статистика КНБ сохранена.")
    except Exception as e:
        logger.error(f"Ошибка сохранения статистики КНБ: {e}")
def save_triggers():
    try:
        data_str = {
            str(chat_id): {phrase: trigger_data for phrase, trigger_data in triggers.items()}
            for chat_id, triggers in chat_triggers.items()
        }
        with open(TRIGGERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Триггеры сохранены.")
    except Exception as e:
        logger.error(f"Ошибка сохранения триггеров: {e}")
def save_trigger_access():
    try:
        data_str = {
            str(chat_id): {
                "mode": info["mode"],
                "allowed_users": [str(uid) for uid in info["allowed_users"]]
            }
            for chat_id, info in trigger_access.items()
        }
        with open(TRIGGER_ACCESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Доступ к триггерам сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения доступа к триггерам: {e}")
def save_inventory():
    try:
        data_str = {
            str(chat_id): {
                str(uid): inv for uid, inv in users.items()
            }
            for chat_id, users in user_inventory.items()
        }
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_str, f, ensure_ascii=False, indent=2)
        logger.info("Инвентарь сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения инвентаря: {e}")
# 🧠 Вспомогательные функции
def generate_minesweeper_field():
    """Генерирует игровое поле с минами."""
    field = [[0 for _ in range(MINESWEEPER_FIELD_SIZE)] for _ in range(MINESWEEPER_FIELD_SIZE)]
    mines_placed = 0
    
    while mines_placed < MINESWEEPER_MINES_COUNT:
        x = random.randint(0, MINESWEEPER_FIELD_SIZE - 1)
        y = random.randint(0, MINESWEEPER_FIELD_SIZE - 1)
        if field[y][x] != -1:
            field[y][x] = -1  # -1 = мина
            mines_placed += 1
    
    # Подсчёт чисел вокруг мин
    for y in range(MINESWEEPER_FIELD_SIZE):
        for x in range(MINESWEEPER_FIELD_SIZE):
            if field[y][x] == -1:
                continue
            count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < MINESWEEPER_FIELD_SIZE and 0 <= nx < MINESWEEPER_FIELD_SIZE:
                        if field[ny][nx] == -1:
                            count += 1
            field[y][x] = count
    
    return field


def create_minesweeper_keyboard(game_data, game_over=False, show_all=False):
    """Создаёт клавиатуру игрового поля."""
    keyboard = InlineKeyboardMarkup(row_width=MINESWEEPER_FIELD_SIZE)
    field = game_data["field"]
    revealed = game_data["revealed"]
    chat_id = game_data["chat_id"]
    
    number_emojis = ["⬜", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
    
    for y in range(MINESWEEPER_FIELD_SIZE):
        row = []
        for x in range(MINESWEEPER_FIELD_SIZE):
            cell_value = field[y][x]
            is_revealed = revealed[y][x]
            
            if show_all or is_revealed:
                if cell_value == -1:
                    emoji = "💥" if is_revealed else "💣"
                else:
                    emoji = number_emojis[cell_value]
                callback = "minesweeper_noop"
            else:
                emoji = "🟦"
                callback = f"minesweeper_click_{chat_id}_{x}_{y}"
            
            row.append(InlineKeyboardButton(emoji, callback_data=callback))
        keyboard.row(*row)
    
    return keyboard


def get_minesweeper_status_text(game_data, status="playing"):
    """Генерирует текст статуса игры."""
    player_id = game_data["player_id"]
    chat_id = game_data["chat_id"]
    safe_revealed = game_data["safe_revealed"]
    safe_to_win = game_data["safe_to_win"]
    
    player_name = get_clickable_name(chat_id, player_id)
    
    if status == "playing":
        progress = f"{safe_revealed}/{safe_to_win}"
        return (
            f"💣 *Сапёр*\n\n"
            f"🎮 Играет: {player_name}\n"
            f"✅ Прогресс: {escape_markdown_v2(progress)}\n"
            f"🎯 Открой {safe_to_win} безопасных клеток\\!"
        )
    elif status == "win":
        return (
            f"🎉 *ПОБЕДА\\!*\n\n"
            f"🏆 {player_name} выиграл\\(а\\) {MINESWEEPER_REWARD} монет\\!"
        )
    elif status == "lose":
        return (
            f"💥 *ВЗРЫВ\\!*\n\n"
            f"😵 {player_name} наступил\\(а\\) на мину\\!"
        )


def start_minesweeper_event(chat_id):
    """Запускает событие приёма заявок на игру."""
    if chat_id not in minesweeper_data:
        minesweeper_data[chat_id] = {}
    
    minesweeper_data[chat_id]["accepting"] = True
    minesweeper_data[chat_id]["excluded_players"] = minesweeper_data[chat_id].get("excluded_players", [])
    minesweeper_data[chat_id]["active_game"] = None
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎮 Участвовать!", callback_data=f"minesweeper_join_{chat_id}"))
    
    try:
        msg = bot.send_message(
            chat_id,
            f"💣 *Событие: Сапёр\\!*\n\n"
            f"🎁 Награда: {MINESWEEPER_REWARD} монет\n"
            f"🎯 Открой {MINESWEEPER_SAFE_TO_WIN} безопасных клеток, чтобы победить\\!\n\n"
            f"👇 Нажми кнопку, чтобы начать игру\\!",
            reply_markup=keyboard,
            parse_mode='MarkdownV2'
        )
        minesweeper_data[chat_id]["accept_message_id"] = msg.message_id
        save_minesweeper_data()
        logger.info(f"[MINESWEEPER] Запущено событие в чате {chat_id}")
        return True
    except Exception as e:
        logger.error(f"[MINESWEEPER] Ошибка запуска события в чате {chat_id}: {e}")
        return False


def restart_minesweeper_accepting(chat_id, loser_id):
    """Перезапускает приём заявок после проигрыша."""
    if chat_id not in minesweeper_data:
        minesweeper_data[chat_id] = {}
    
    excluded = minesweeper_data[chat_id].get("excluded_players", [])
    if loser_id not in excluded:
        excluded.append(loser_id)
    
    minesweeper_data[chat_id]["accepting"] = True
    minesweeper_data[chat_id]["excluded_players"] = excluded
    minesweeper_data[chat_id]["active_game"] = None
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎮 Участвовать!", callback_data=f"minesweeper_join_{chat_id}"))
    
    try:
        msg = bot.send_message(
            chat_id,
            f"💣 *Ещё одна попытка\\!*\n\n"
            f"Предыдущий игрок проиграл\\.\\.\\. Кто следующий\\?\n\n"
            f"🎁 Награда: {MINESWEEPER_REWARD} монет\n"
            f"👇 Нажми кнопку, чтобы начать игру\\!",
            reply_markup=keyboard,
            parse_mode='MarkdownV2'
        )
        minesweeper_data[chat_id]["accept_message_id"] = msg.message_id
        save_minesweeper_data()
        logger.info(f"[MINESWEEPER] Перезапущен приём заявок в чате {chat_id}")
    except Exception as e:
        logger.error(f"[MINESWEEPER] Ошибка перезапуска в чате {chat_id}: {e}")
def log_and_cache_message(message):
    try:
        chat_type = message.chat.type
        text = message.text or "[не текст]"
        user = message.from_user
        username = f"@{user.username}" if user.username else f"id{user.id}"
        logger.info(f"[{chat_type}] {username}: {text}")
        if message.chat.type in ['group', 'supergroup']:
            chat_id = message.chat.id
            if chat_id not in chat_members_cache:
                chat_members_cache[chat_id] = {}
            chat_members_cache[chat_id][user.id] = {
                "name": user_custom_names.get(str(user.id), user.first_name or "Без имени"),
                "username": user.username,
                "first_name": user.first_name or "",
            }
            save_user_cache()
    except Exception as e:
        logger.error(f"Ошибка в log_and_cache_message: {e}")
def escape_markdown_v2(text):
    if not isinstance(text, str):
        text = str(text)
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in text)

def get_clickable_name(chat_id, user_id, user_obj=None):
    is_offline = chat_id in offline_users and user_id in offline_users[chat_id]
    if str(user_id) in user_custom_names:
        display_name = user_custom_names[str(user_id)]
        if is_offline:
            return escape_markdown_v2(display_name)
        else:
            safe_name = escape_markdown_v2(display_name)
            return f"[{safe_name}](tg://user?id={user_id})"
    elif chat_id in chat_members_cache and user_id in chat_members_cache[chat_id]:
        user_data = chat_members_cache[chat_id][user_id]
        if user_data.get("username"):
            username = user_data['username']
            if is_offline:
                return "@" + escape_markdown_v2(username)
            else:
                escaped_username = username.replace('_', r'\_')
                return f"@{escaped_username}"
        else:
            display_name = user_data.get("first_name", "Аноним")
            if is_offline:
                return escape_markdown_v2(display_name)
            else:
                safe_name = escape_markdown_v2(display_name)
                return f"[{safe_name}](tg://user?id={user_id})"
    elif user_obj and user_obj.username:
        username = user_obj.username
        if is_offline:
            return "@" + escape_markdown_v2(username)
        else:
            escaped_username = username.replace('_', r'\_')
            return f"@{escaped_username}"
    elif user_obj:
        display_name = user_obj.first_name or "Аноним"
        if is_offline:
            return escape_markdown_v2(display_name)
        else:
            safe_name = escape_markdown_v2(display_name)
            return f"[{safe_name}](tg://user?id={user_id})"
    else:
        display_name = "Аноним"
        if is_offline:
            return escape_markdown_v2(display_name)
        else:
            safe_name = escape_markdown_v2(display_name)
            return f"[{safe_name}](tg://user?id={user_id})"

def ensure_user_in_cache(chat_id, user_id, user_obj=None):
    if chat_id not in chat_members_cache:
        chat_members_cache[chat_id] = {}
    if user_id not in chat_members_cache[chat_id]:
        if user_obj:
            chat_members_cache[chat_id][user_id] = {
                "name": user_custom_names.get(str(user_id), user_obj.first_name or "Без имени"),
                "username": user_obj.username,
                "first_name": user_obj.first_name or "",
            }
        else:
            try:
                chat_member = bot.get_chat_member(chat_id, user_id)
                user_data = chat_member.user
                chat_members_cache[chat_id][user_id] = {
                    "name": user_custom_names.get(str(user_id), user_data.first_name or "Без имени"),
                    "username": user_data.username,
                    "first_name": user_data.first_name or "",
                }
            except Exception as e:
                logger.warning(f"Не удалось получить данные пользователя {user_id} через API: {e}")
                chat_members_cache[chat_id][user_id] = {
                    "name": "Аноним",
                    "username": None,
                    "first_name": "Аноним",
                }
        save_user_cache()
def fetch_all_members(chat_id):
    if chat_id not in chat_members_cache:
        chat_members_cache[chat_id] = {}
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            user = admin.user
            ensure_user_in_cache(chat_id, user.id, user)
        logger.info(f"Загружено {len(chat_members_cache[chat_id])} администраторов для чата {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке администраторов чата {chat_id}: {e}")
def error_handler(func):
    def wrapper(message):
        try:
            log_and_cache_message(message)
            func(message)
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}")
            try:
                bot.reply_to(message, "❌ Произошла ошибка. Попробуйте позже.")
            except:
                pass
    return wrapper
def format_time_diff(seconds):
    if seconds < 60:
        return f"{seconds} сек"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} мин"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} ч"
    else:
        days = int(seconds / 86400)
        return f"{days} д"
def is_user_chat_owner(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status == 'creator'
    except:
        return False
def is_user_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False
def can_use_trigger_command(chat_id, user_id):
    if chat_id not in trigger_access:
        return is_user_chat_owner(chat_id, user_id)
    mode = trigger_access[chat_id]["mode"]
    allowed_users = trigger_access[chat_id]["allowed_users"]
    if mode == "members":
        return True
    if mode == "admins":
        return is_user_admin(chat_id, user_id)
    if mode == "creator":
        return is_user_chat_owner(chat_id, user_id)
    return user_id in allowed_users
def get_inventory(chat_id, user_id):
    if chat_id not in user_inventory:
        user_inventory[chat_id] = {}
    if user_id not in user_inventory[chat_id]:
        user_inventory[chat_id][user_id] = {"handcuffs": 0, "shields": 0, "skipkd": 0}
    return user_inventory[chat_id][user_id]
def use_item(chat_id, user_id, item):
    inv = get_inventory(chat_id, user_id)
    if inv[item] > 0:
        inv[item] -= 1
        save_inventory()
        return True
    return False
def execut_kick_loop():
    """Фоновый процесс: каждые 60 минут исключает по одному участнику из очереди и уведомляет чат о следующем."""
    while True:
        time.sleep(3600)  # 60 минут
        try:
            to_remove = []
            for chat_id, user_list in list(execut_queue.items()):
                if not user_list:
                    # Все исключены — бот покидает чат
                    try:
                        bot.leave_chat(chat_id)
                        logger.info(f"[EXECUT] Бот покинул чат {chat_id} после ликвидации всех.")
                    except Exception as e:
                        logger.error(f"[EXECUT] Не удалось покинуть чат {chat_id}: {e}")
                    to_remove.append(chat_id)
                    continue

                user_id = user_list.pop(0)  # исключаем первого в очереди
                save_execut_queue()

                # Исключаем пользователя
                try:
                    bot.kick_chat_member(chat_id, user_id)
                    logger.info(f"[EXECUT] Исключён пользователь {user_id} из чата {chat_id}")
                except Exception as e:
                    logger.warning(f"[EXECUT] Не удалось исключить {user_id} из {chat_id}: {e}")

                # Теперь проверяем, есть ли следующий участник
                if execut_queue[chat_id]:
                    next_user_id = execut_queue[chat_id][0]
                    next_user_name = get_clickable_name(chat_id, next_user_id)
                    try:
                        bot.send_message(
                            chat_id,
                            f"⚠️ Следующий в очереди на ликвидацию: {next_user_name}",
                            parse_mode='MarkdownV2'
                        )
                        logger.info(f"[EXECUT] Уведомление о следующем участнике: {next_user_name} в чате {chat_id}")
                    except Exception as e:
                        logger.warning(f"[EXECUT] Не удалось отправить уведомление о следующем участнике {next_user_id}: {e}")
                else:
                    # Очередь пуста — бот покинет чат при следующем цикле
                    pass

            for chat_id in to_remove:
                execut_queue.pop(chat_id, None)
            if to_remove:
                save_execut_queue()

        except Exception as e:
            logger.error(f"[EXECUT] Ошибка в фоновом процессе: {e}")

@bot.message_handler(func=lambda m: (
    m.chat.type in ['group', 'supergroup'] and
    m.text is not None and
    not m.text.startswith('/') and
    not (m.chat.id in chat_triggers and m.text.strip().lower() in chat_triggers[m.chat.id]) and
    not m.text.lower().startswith("members") and
    not m.text.lower().startswith("сомка кто ") and
    not m.text.lower().startswith("сомка фото ") and
    not m.text.lower().startswith("сомка нарисуй ")))
def delete_muted_text_messages(message):   
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалено текстовое сообщение от замученного пользователя {user_id} в чате {chat_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить текстовое сообщение от замученного: {e}")

def is_kidnap_game_enabled(chat_id):
    return chat_features.get(chat_id, {}).get("kidnap_game", True)

def are_triggers_enabled(chat_id):
    return chat_features.get(chat_id, {}).get("triggers", True)
# 📋 Команда members — ПОЛНОСТЬЮ ПЕРЕПИСАНА
@bot.message_handler(commands=['members'])
@error_handler
def show_members(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        ensure_user_in_cache(chat_id, target_user.id, target_user)
    fetch_all_members(chat_id)
    if chat_id not in chat_members_cache or not chat_members_cache[chat_id]:
        bot.reply_to(message, "🤷‍♂️ Я пока не знаю ни одного пользователя в этом чате. Попросите их написать что-нибудь!")
        return
    members = []
    for user_id, user_data in chat_members_cache[chat_id].items():
        name_link = get_clickable_name(chat_id, user_id)
        members.append(name_link)
    if not members:
        bot.reply_to(message, "🤷‍♂️ Не удалось получить список участников.")
        return
    members.sort()
    safe_header = escape_markdown_v2("👥 Участники чата:")
    response = safe_header + "\n" + "\n".join(f"• {m}" for m in members)
    bot.reply_to(message, response, parse_mode='MarkdownV2')
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("members") and message.chat.type in ['group', 'supergroup'])
@error_handler
def handle_somka_start5(message):
    logger.info("[members] — сработал триггер")
    show_members(message)
# 🛒 Магазин
@bot.message_handler(commands=['shop'])
@error_handler
def show_shop(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    shop_text = (
        "🛒 *Магазин Сомки*\n"
        "🔻 Купленные предметы можно использовать, не тратя время на восстановление кулдауна\n\n"
        "Нажми на кнопку, чтобы купить предмет:\n"
        "• `🔗 handcuffs` — наручники \\(50 монет\\)\n"
        "• `🛡️ shields` — щит \\(50 монет\\)\n"
        "• `🕑 skipkd` — скип кулдауна \\(60 монет\\)")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔗 Купить наручники (50 монет)", callback_data="buy_handcuffs"),
        InlineKeyboardButton("🛡️ Купить щит (50 монет)", callback_data="buy_shields"),
        InlineKeyboardButton("⏱️ Купить скип кд (60 монет)", callback_data="buy_skipkd"))
    bot.reply_to(message, shop_text, reply_markup=keyboard, parse_mode='MarkdownV2')
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    item_key = call.data[4:]  # "handcuffs", "shields", "skipkd"
    item_names = {
        "handcuffs": "наручники",
        "shields": "щит",
        "skipkd": "скип кулдауна"
    }
    prices = {"handcuffs": 50, "shields": 50, "skipkd": 60}
    if item_key not in prices:
        bot.answer_callback_query(call.id, "❌ Неверный товар.", show_alert=True)
        return
    price = prices[item_key]
    if chat_id not in user_coins or user_coins[chat_id].get(user_id, 0) < price:
        bot.answer_callback_query(call.id, f"❌ Недостаточно монет. Нужно {price}.", show_alert=True)
        return
    user_coins[chat_id][user_id] -= price
    inv = get_inventory(chat_id, user_id)
    inv[item_key] += 1
    save_coins()
    save_inventory()
    display_name = get_clickable_name(chat_id, user_id, call.from_user)
    item_name = item_names[item_key]
    bot.answer_callback_query(call.id, f"✅ Куплено: {item_name}!", show_alert=False)
    bot.send_message(
        chat_id,
        f"✅ Игрок {display_name} купил\\(а\\) *{escape_markdown_v2(item_name)}* за {price} монет\\!", parse_mode='MarkdownV2')
# 🕹️ Мини-игра "Похищение"
@bot.message_handler(commands=['kidnap'])
def attempt_kidnap(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    kidnapper_id = message.from_user.id
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = time.time()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if chat_id not in kidnap_bags:
        kidnap_bags[chat_id] = {}
    if chat_id not in handcuffed_players:
        handcuffed_players[chat_id] = set()
    if chat_id not in shield_used:
        shield_used[chat_id] = {}
    if kidnapper_id in last_kidnap_attempt[chat_id]:
        unlock_time = last_kidnap_attempt[chat_id][kidnapper_id]
        if current_time < unlock_time:
            remaining = int((unlock_time - current_time) / 60)
            bot.reply_to(message, f"⏳ Ты слишком устал. Подожди ещё {remaining} минут.")
            return
    is_kidnapper_victim = any(kidnapper_id in victims for victims in kidnap_bags[chat_id].values())
    if is_kidnapper_victim:
        bot.reply_to(message, "🔒 Ты находишься в плену и не можешь никого похищать!")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Чтобы похитить, ответь на сообщение жертвы командой /kidnap")
        return
    target_user = message.reply_to_message.from_user
    target_id = target_user.id
    ensure_user_in_cache(chat_id, target_id, target_user)
    if kidnapper_id == target_id:
        bot.reply_to(message, "🤔 Ты не можешь похитить самого себя!")
        return
    if any(target_id in victims for victims in kidnap_bags[chat_id].values()):
        target_name = get_clickable_name(chat_id, target_id, target_user)
        bot.reply_to(message, f"🔒 {target_name} уже в чьём\\-то мешке\\!", parse_mode='MarkdownV2')
        return
    if random.choice([True, False]):  # 50% шанс успеха
        if kidnapper_id not in kidnap_bags[chat_id]:
            kidnap_bags[chat_id][kidnapper_id] = set()
        if shield_used[chat_id].get(target_id, False):
            shield_used[chat_id][target_id] = False
            save_shield_data()
            victim_count = len(kidnap_bags[chat_id].get(kidnapper_id, set()))
            if victim_count >= 7:
                cooldown = 900      # 15 мин
            elif victim_count >= 5:
                cooldown = 1200     # 20 мин
            elif victim_count >= 3:
                cooldown = 1500     # 25 мин
            else:
                cooldown = 1800     # 30 мин
            last_kidnap_attempt[chat_id][kidnapper_id] = current_time + cooldown
            save_kidnap_data()

            target_name = get_clickable_name(chat_id, target_id, target_user)
            bot.reply_to(
                message,
                f"🛡️ Попытка похищения провалилась\\! {target_name} был защищён щитом\\! Попробуй через {cooldown // 60} мин\\.",parse_mode='MarkdownV2')
            return
        kidnap_bags[chat_id][kidnapper_id].add(target_id)
        stolen = kidnap_bags[chat_id].pop(target_id, set())
        kidnap_bags[chat_id][kidnapper_id].update(stolen)
        if chat_id not in kidnap_points:
            kidnap_points[chat_id] = {}
        kidnap_points[chat_id][kidnapper_id] = kidnap_points[chat_id].get(kidnapper_id, 0) + 1
        victim_count = len(kidnap_bags[chat_id][kidnapper_id])
        if victim_count >= 7:
            cooldown = 900
        elif victim_count >= 5:
            cooldown = 1200
        elif victim_count >= 3:
            cooldown = 1500
        else:
            cooldown = 1800
        last_kidnap_attempt[chat_id][kidnapper_id] = current_time + cooldown
        if chat_id not in steal_timers:
            steal_timers[chat_id] = {}
        steal_timers[chat_id][(kidnapper_id, target_id)] = current_time
        for stolen_victim in stolen:
            steal_timers[chat_id][(kidnapper_id, stolen_victim)] = current_time
        save_steal_timers()
        save_kidnap_data()
        target_name = get_clickable_name(chat_id, target_id, target_user)
        bot.reply_to(
            message,
            f"🎉 Успешно\\! Ты похитил {target_name}\\! Кулдаун: {cooldown // 60} мин\\.", parse_mode='MarkdownV2' )
    else:
      victim_count = len(kidnap_bags[chat_id].get(kidnapper_id, set()))
      if victim_count >= 7:
        cooldown = 900
      elif victim_count >= 5:
        cooldown = 1200
      elif victim_count >= 3:
        cooldown = 1500
      else:
        cooldown = 1800
      last_kidnap_attempt[chat_id][kidnapper_id] = current_time + cooldown
      save_kidnap_data()
      target_name = get_clickable_name(chat_id, target_id, target_user)
      bot.reply_to(message, f"😱 Неудача! Попробуй через {cooldown // 60} минут.")

@bot.message_handler(commands=['freed'])
def attempt_freed(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if chat_id not in kidnap_bags:
        kidnap_bags[chat_id] = {}
    if chat_id not in handcuffed_players:
        handcuffed_players[chat_id] = set()
    is_victim = any(user_id in victims for victims in kidnap_bags[chat_id].values())
    is_handcuffed = user_id in handcuffed_players[chat_id]
    if not is_victim and not is_handcuffed:
        bot.reply_to(message, "😌 Ты и так на свободе!")
        return
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if user_id in last_kidnap_attempt[chat_id]:
        unlock_time = last_kidnap_attempt[chat_id][user_id]
        if current_time < unlock_time:
            remaining = int((unlock_time - current_time) / 60)
            bot.reply_to(message, f"⏳ Ты слишком устал. Подожди ещё {remaining} минут.")
            return
    last_kidnap_attempt[chat_id][user_id] = current_time + 1800  # 30 минут
    save_kidnap_data()
    if is_handcuffed:
        if random.random() < 0.9:
            handcuffed_players[chat_id].discard(user_id)
            if chat_id in muted_users and user_id in muted_users[chat_id]:
                muted_users[chat_id].discard(user_id)
                save_muted_users()
            bot.reply_to(message, "🔗🌿 Ура! Ты снял наручники!")
        else:
            bot.reply_to(message, "😱 Неудача! Попробуй через 30 минут.")
        return
    if is_victim:
        kidnapper_id = None
        for kidnapper, victims in kidnap_bags[chat_id].items():
            if user_id in victims:
                kidnapper_id = kidnapper
                break
        if random.random() < 0.5:
            if kidnapper_id:
                kidnap_bags[chat_id][kidnapper_id].discard(user_id)
                if not kidnap_bags[chat_id][kidnapper_id]:
                    del kidnap_bags[chat_id][kidnapper_id]
            save_kidnap_data()
            if kidnapper_id:
                kidnapper_name = get_clickable_name(chat_id, kidnapper_id)
                bot.reply_to(message, f"🎉 Ура\\! Ты сбежал из плена {kidnapper_name}\\!", parse_mode='MarkdownV2')
            else:
                bot.reply_to(message, "🎉 Ура! Ты сбежал из плена!")
        else:
            bot.reply_to(message, "😱 Неудача! Попробуй через 30 минут.")

@bot.message_handler(commands=['handcuff'])
def attempt_handcuff(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if chat_id not in kidnap_bags:
        kidnap_bags[chat_id] = {}
    if chat_id not in handcuffed_players:
        handcuffed_players[chat_id] = set()
    used_item = use_item(chat_id, user_id, "handcuffs")
    if not used_item:
        if user_id in last_kidnap_attempt[chat_id]:
            unlock_time = last_kidnap_attempt[chat_id][user_id]
            if current_time < unlock_time:
                remaining = int((unlock_time - current_time) / 60)
                bot.reply_to(message, f"⏳ Подожди ещё {remaining} минут.")
                return
        is_victim = any(user_id in victims for victims in kidnap_bags[chat_id].values())
        if is_victim:
            bot.reply_to(message, "🔒 Ты в плену и не можешь никого заковывать!")
            return
        if user_id not in kidnap_bags[chat_id] or not kidnap_bags[chat_id][user_id]:
            bot.reply_to(message, "📭 У тебя нет пленников!")
            return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответь на сообщение пленника командой /handcuff")
        return
    target_user = message.reply_to_message.from_user
    target_id = target_user.id
    ensure_user_in_cache(chat_id, target_id, target_user)
    if user_id == target_id:
        bot.reply_to(message, "🤔 Ты не можешь заковать себя!")
        return
    if target_id not in kidnap_bags[chat_id].get(user_id, set()):
        bot.reply_to(message, "🔒 Эта цель не в твоём мешке!")
        return
    if not used_item:
        victim_count = len(kidnap_bags[chat_id][user_id])
        if victim_count >= 7:
            cooldown = 900
        elif victim_count >= 5:
            cooldown = 1200
        elif victim_count >= 3:
            cooldown = 1500
        else:
            cooldown = 1800
        last_kidnap_attempt[chat_id][user_id] = current_time + cooldown
        save_kidnap_data()
    if random.random() < 0.9:
        handcuffed_players[chat_id].add(target_id)
        target_name = get_clickable_name(chat_id, target_id, target_user)
        cooldown_text = f" Кулдаун: {cooldown // 60} мин\\." if not used_item else ""
        bot.reply_to(message, f"🔗 Успешно\\! Ты заковал {target_name} в наручники\\!{cooldown_text}\n🔇 Чтобы заставить своего пленника замолчать, воспользуйся командой \\/mute", parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, "😱 Неудача!" + (" Попробуй через 30 минут." if not used_item else ""))

@bot.message_handler(commands=['shield'])
def activate_shield(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if chat_id not in shield_used:
        shield_used[chat_id] = {}
    if chat_id not in kidnap_bags:
        kidnap_bags[chat_id] = {}
    is_victim = any(user_id in victims for victims in kidnap_bags[chat_id].values())
    if is_victim:
        bot.reply_to(message, "🔒 Ты в плену и не можешь активировать щит!")
        return
    used_item = use_item(chat_id, user_id, "shields")
    if not used_item:
        if user_id in last_kidnap_attempt[chat_id]:
            unlock_time = last_kidnap_attempt[chat_id][user_id]
            if current_time < unlock_time:
                remaining = int((unlock_time - current_time) / 60)
                bot.reply_to(message, f"⏳ Подожди ещё {remaining} минут")
                return
        if shield_used[chat_id].get(user_id, False):
            bot.reply_to(message, "🛡️ У тебя уже есть активный щит!")
            return
        victim_count = len(kidnap_bags[chat_id].get(user_id, set()))
        if victim_count >= 7:
            cooldown = 900
        elif victim_count >= 5:
            cooldown = 1200
        elif victim_count >= 3:
            cooldown = 1500
        else:
            cooldown = 1800
        last_kidnap_attempt[chat_id][user_id] = current_time + cooldown
        save_kidnap_data()
    shield_used[chat_id][user_id] = True
    save_shield_data()
    display_name = get_clickable_name(chat_id, user_id, message.from_user)
    cooldown_text = f" Кулдаун: {cooldown // 60} мин\\." if not used_item else ""
    bot.reply_to(message, f"🛡️ {display_name}, ты активировал\\(а\\) щит\\!{cooldown_text}", parse_mode='MarkdownV2')

@bot.message_handler(commands=['skipkd'])
@error_handler
def skip_kd(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    user_id = message.from_user.id
    chat_id = message.chat.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if not use_item(chat_id, user_id, "skipkd"):
        bot.reply_to(message, "❌ У тебя нет предмета «скип кулдауна».")
        return
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        ensure_user_in_cache(chat_id, target_id, target_user)
        if target_id in last_kidnap_attempt[chat_id]:
            del last_kidnap_attempt[chat_id][target_id]
            save_kidnap_data()
            target_name = get_clickable_name(chat_id, target_id, message.reply_to_message.from_user)
            bot.reply_to(message, f"✅ Кулдаун сброшен для {target_name}\\!", parse_mode='MarkdownV2')
        else:
            target_name = get_clickable_name(chat_id, target_id, message.reply_to_message.from_user)
            bot.reply_to(message, f"✅ У {target_name} и так нет кулдауна\\.", parse_mode='MarkdownV2')
    else:
        if user_id in last_kidnap_attempt[chat_id]:
            del last_kidnap_attempt[chat_id][user_id]
            save_kidnap_data()
            bot.reply_to(message, "✅ Твой кулдаун сброшен!")
        else:
            bot.reply_to(message, "✅ У тебя и так нет активного кулдауна.")

@bot.message_handler(commands=['bag'])
@error_handler
def show_my_bag(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in kidnap_bags:
        kidnap_bags[chat_id] = {}
    if chat_id not in handcuffed_players:
        handcuffed_players[chat_id] = set()
    if chat_id not in muted_users:
        muted_users[chat_id] = set()
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        ensure_user_in_cache(chat_id, target_id, target_user)
        header_name = get_clickable_name(chat_id, target_id, target_user)
    else:
        target_id = message.from_user.id
        header_name = escape_markdown_v2("твой")
    status_parts = []
    is_in_bag = False
    captor_id = None
    for kidnapper, victims in kidnap_bags.get(chat_id, {}).items():
        if target_id in victims:
            is_in_bag = True
            captor_id = kidnapper
            break
    if is_in_bag:
        captor_name = get_clickable_name(chat_id, captor_id)
        status_parts.append(f"🪝 В мешке у {captor_name}")
    if target_id in handcuffed_players.get(chat_id, set()):
        status_parts.append("🔗 Прикован наручниками")
    if target_id in muted_users.get(chat_id, set()):
        status_parts.append("🔇 Замучен")
    if status_parts:
        status_line = "📌 *Статус*: " + ", ".join(status_parts) + "\n"
    else:
        status_line = "🌿 *Статус*: на свободе\n"
    balance = user_coins.get(chat_id, {}).get(target_id, 0)
    balance_line = f"💰 *Баланс*: {balance} монет\n"
    inv = get_inventory(chat_id, target_id)
    inv_line = (
        f"🎒 *Инвентарь*:\n"
        f"🔗 Наручники — {inv['handcuffs']},\n"
        f"🛡️ Щиты — {inv['shields']},\n"
        f"🕑 Скип кд — {inv['skipkd']}\n" )
    if target_id not in kidnap_bags[chat_id] or not kidnap_bags[chat_id][target_id]:
        if message.reply_to_message:
            response = f"{status_line}{balance_line}{inv_line}📭 Мешок игрока {header_name} пуст\\."
        else:
            response = f"{status_line}{balance_line}{inv_line}📭 Твой мешок пуст, ты никого не похищал\\."
        bot.reply_to(message, response, parse_mode='MarkdownV2')
        return
    victims = kidnap_bags[chat_id][target_id]
    victim_links = []
    for vid in victims:
        name_link = get_clickable_name(chat_id, vid)
        suffix = " 🔗" if vid in handcuffed_players.get(chat_id, set()) else ""
        victim_links.append(name_link + suffix)
    victim_list = "\n".join(f"• {link}" for link in victim_links)
    if message.reply_to_message:
        response = f"{status_line}{balance_line}{inv_line}🪝 *Мешок похищенных игрока {header_name}:*\n{victim_list}"
    else:
        response = f"{status_line}{balance_line}{inv_line}🪝 *Твой мешок похищенных:*\n{victim_list}"
    bot.reply_to(message, response, parse_mode='MarkdownV2')

@bot.message_handler(commands=['kidnapstat'])
def show_kidnap_stats(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in kidnap_points or not kidnap_points[chat_id]:
        bot.reply_to(message, "📊 В этом чате пока никто не заработал очков в похищениях.")
        return
    sorted_players = sorted(kidnap_points[chat_id].items(), key=lambda x: x[1], reverse=True)
    stats = []
    for uid, points in sorted_players:
        link = get_clickable_name(chat_id, uid)
        stats.append(f"• {link}: {points} очков")
    response = "🏆 *Таблица лидеров по похищениям в этом чате:*\n" + "\n".join(stats)
    bot.reply_to(message, response, parse_mode='MarkdownV2')

SALRUZO_USER_ID = 1170970828
PEXELS_API_KEY = "JdCL2H1f4FxbFq3HAMhk3ELTBXV6IqPIHO16S11EaOfthzLF5TitQR5u"
@bot.message_handler(commands=['resetkidnap'])
@error_handler
def reset_kidnap_cooldown_only(message):
    if message.from_user.id != SALRUZO_USER_ID:
        bot.reply_to(message, "❌ Эта команда доступна только @SalRuzO.")
        return
    chat_id = message.chat.id
    if chat_id not in last_kidnap_attempt:
        last_kidnap_attempt[chat_id] = {}
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        ensure_user_in_cache(chat_id, target_id, target_user)
        target_name = get_clickable_name(chat_id, target_id, target_user)
    else:
        target_id = message.from_user.id
        target_name = "твой"
    if target_id in last_kidnap_attempt[chat_id]:
        del last_kidnap_attempt[chat_id][target_id]
        save_kidnap_data()
        if message.reply_to_message:
            bot.reply_to(message, f"✅ Кулдаун похищения сброшен для {target_name}\\!", parse_mode='MarkdownV2')
        else:
            bot.reply_to(message, "✅ Твой кулдаун похищения сброшен!")
        logger.info(f"[RESETKIDNAP] Кулдаун сброшен для {target_id} в чате {chat_id} (@SalRuzO)")
    else:
        if message.reply_to_message:
            bot.reply_to(message, f"✅ У {target_name} и так нет активного кулдауна\\.", parse_mode='MarkdownV2')
        else:
            bot.reply_to(message, "✅ У тебя и так нет активного кулдауна.")

@bot.message_handler(commands=['dailyreport'])
@error_handler
def set_daily_report(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверка прав: только создатель чата или SalRuzO
    if user_id != SALRUZO_USER_ID and not is_user_chat_owner(chat_id, user_id):
        bot.reply_to(message, "❌ Эта команда доступна только создателю чата\\.", parse_mode='MarkdownV2')
        return
    
    # Парсим аргументы: /dailyreport 12.12.2026 комментарий
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(
            message, 
            "❌ Использование: `/dailyreport ДД\\.ММ\\.ГГГГ комментарий`\n"
            "Пример: `/dailyreport 12\\.12\\.2026 До Нового года\\!`", 
            parse_mode='MarkdownV2'
        )
        return
    
    date_str = args[1]
    comment = args[2]
    
    # Парсим дату
    try:
        target_date = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат даты\\. Используй: ДД\\.ММ\\.ГГГГ", parse_mode='MarkdownV2')
        return
    
    # Проверяем что дата в будущем
    if target_date.date() <= datetime.now().date():
        bot.reply_to(message, "❌ Дата должна быть в будущем\\.", parse_mode='MarkdownV2')
        return
    
    # Сохраняем
    daily_reports[chat_id] = {
        "target_date": target_date.strftime("%Y-%m-%d"),
        "comment": comment,
        "last_sent": None
    }
    save_daily_reports()
    
    escaped_date = escape_markdown_v2(date_str)
    escaped_comment = escape_markdown_v2(comment)
    bot.reply_to(
        message, 
        f"✅ Ежедневный отчёт установлен\\!\n"
        f"📅 Дата: {escaped_date}\n"
        f"💬 Комментарий: {escaped_comment}", 
        parse_mode='MarkdownV2'
    )
    logger.info(f"[DAILY_REPORT] Установлен отчёт в чате {chat_id} до {date_str}")


@bot.message_handler(commands=['stopreport'])
@error_handler
def stop_daily_report(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверка прав: только создатель чата или SalRuzO
    if user_id != SALRUZO_USER_ID and not is_user_chat_owner(chat_id, user_id):
        bot.reply_to(message, "❌ Эта команда доступна только создателю чата\\.", parse_mode='MarkdownV2')
        return
    
    if chat_id in daily_reports:
        # Открепляем последнее сообщение
        old_message_id = daily_reports[chat_id].get("last_message_id")
        if old_message_id:
            try:
                bot.unpin_chat_message(chat_id, old_message_id)
                logger.info(f"[DAILY_REPORT] Откреплено сообщение при отключении отчёта в чате {chat_id}")
            except Exception as e:
                logger.warning(f"[DAILY_REPORT] Не удалось открепить сообщение при отключении: {e}")
        
        del daily_reports[chat_id]
        save_daily_reports()
        bot.reply_to(message, "✅ Ежедневный отчёт отключён\\.", parse_mode='MarkdownV2')
        logger.info(f"[DAILY_REPORT] Отчёт отключён в чате {chat_id}")
    else:
        bot.reply_to(message, "❌ В этом чате нет активного ежедневного отчёта\\.", parse_mode='MarkdownV2')

@bot.message_handler(commands=['minestat'])
@error_handler
def show_minesweeper_stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        return
    
    if chat_id not in minesweeper_stats or not minesweeper_stats[chat_id]:
        bot.reply_to(message, "📊 В этом чате ещё никто не играл в Сапёра\\.", parse_mode='MarkdownV2')
        return
    
    # Сортируем по победам
    sorted_players = sorted(
        minesweeper_stats[chat_id].items(),
        key=lambda x: (x[1]["wins"], -x[1]["losses"]),
        reverse=True
    )
    
    lines = []
    for uid, stats in sorted_players[:15]:
        name = get_clickable_name(chat_id, uid)
        wins = stats["wins"]
        losses = stats["losses"]
        lines.append(f"• {name}: ✅ {wins} / ❌ {losses}")
    
    response = "💣 *Статистика Сапёра:*\n\n" + "\n".join(lines)
    bot.reply_to(message, response, parse_mode='MarkdownV2')


@bot.message_handler(commands=['minesweeper'])
@error_handler
def force_minesweeper_event(message):
    """Принудительный запуск события (только для SalRuzO)."""
    if message.from_user.id != SALRUZO_USER_ID:
        bot.reply_to(message, "❌ Эта команда доступна только @SalRuzO\\.", parse_mode='MarkdownV2')
        return
    
    chat_id = message.chat.id
    
    # Проверяем, нет ли активной игры
    if chat_id in minesweeper_data:
        if minesweeper_data[chat_id].get("active_game"):
            bot.reply_to(message, "❌ В этом чате уже идёт игра\\.", parse_mode='MarkdownV2')
            return
        if minesweeper_data[chat_id].get("accepting"):
            bot.reply_to(message, "❌ В этом чате уже открыт приём заявок\\.", parse_mode='MarkdownV2')
            return
    
    # Сбрасываем исключённых игроков
    if chat_id in minesweeper_data:
        minesweeper_data[chat_id]["excluded_players"] = []
    
    if start_minesweeper_event(chat_id):
        bot.reply_to(message, "✅ Событие Сапёра запущено\\!", parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, "❌ Не удалось запустить событие\\.", parse_mode='MarkdownV2')
        
@bot.message_handler(commands=['job'])
@error_handler
def earn_coins(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in last_job_attempt:
        last_job_attempt[chat_id] = {}
    if chat_id not in user_coins:
        user_coins[chat_id] = {}
    if user_id in last_job_attempt[chat_id]:
        elapsed = current_time - last_job_attempt[chat_id][user_id]
        if elapsed < 3600:
            remaining_minutes = int((3600 - elapsed) / 60)
            bot.reply_to(message, f"⏳ Ты слишком устал\\. Подожди ещё {remaining_minutes} минут, прежде чем снова идти на работу\\.", parse_mode='MarkdownV2')
            return
    earned = 10
    user_coins[chat_id][user_id] = user_coins[chat_id].get(user_id, 0) + earned
    new_balance = user_coins[chat_id][user_id]
    last_job_attempt[chat_id][user_id] = current_time
    save_coins()
    save_job_cooldown()
    display_name = get_clickable_name(chat_id, user_id, message.from_user)
    bot.reply_to(
        message,
        f"✅ {display_name}, ты отработал тяжелую смену и заработал {earned} монет\\! 💰\n💰 Твой баланс: {new_balance} монет\\.", parse_mode='MarkdownV2')

@bot.message_handler(commands=['knb'])
@error_handler
def start_knb_game(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    initiator = message.from_user
    initiator_id = initiator.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Чтобы предложить игру, ответь на сообщение соперника командой /knb <ставка>")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Использование: /knb <сумма>\nПример: /knb 10")
        return
    try:
        bet = int(args[1])
        if bet <= 0:
            bot.reply_to(message, "❌ Ставка должна быть положительным числом\\!")
            return
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите целое число для ставки\\.")
        return
    opponent = message.reply_to_message.from_user
    opponent_id = opponent.id
    ensure_user_in_cache(chat_id, opponent_id, opponent)
    if initiator_id == opponent_id:
        bot.reply_to(message, "🤔 Ты не можешь играть сам с собой\\!")
        return
    if chat_id not in user_coins:
        user_coins[chat_id] = {}
    initiator_balance = user_coins[chat_id].get(initiator_id, 0)
    opponent_balance = user_coins[chat_id].get(opponent_id, 0)
    if initiator_balance < bet:
        bot.reply_to(message, "❌ У тебя недостаточно монет для этой ставки!")
        return
    if opponent_balance < bet:
        bot.reply_to(message, "❌ У твоего соперника недостаточно монет для этой ставки!")
        return
    game_id = str(uuid.uuid4())
    initiator_name = get_clickable_name(chat_id, initiator_id, initiator)
    opponent_name = get_clickable_name(chat_id, opponent_id, opponent)
    keyboard = InlineKeyboardMarkup()
    rock_btn = InlineKeyboardButton("🪨 Камень", callback_data=f"knb_choose_rock_{game_id}")
    scissors_btn = InlineKeyboardButton("✂️ Ножницы", callback_data=f"knb_choose_scissors_{game_id}")
    paper_btn = InlineKeyboardButton("📄 Бумага", callback_data=f"knb_choose_paper_{game_id}")
    keyboard.add(rock_btn, scissors_btn, paper_btn)
    status_msg = bot.send_message(
        chat_id,
        f"🎲 Игра «Камень, Ножницы, Бумага» между {initiator_name} и {opponent_name} на {bet} монет\\.\n👉 Сейчас ходит {initiator_name}\\.\\.\\.",
        reply_markup=keyboard,parse_mode='MarkdownV2')
    pending_knb_games[game_id] = {
        "chat_id": chat_id,
        "initiator_id": initiator_id,
        "opponent_id": opponent_id,
        "bet": bet,
        "initiator_choice": None,
        "opponent_choice": None,
        "message_id": status_msg.message_id,
        "current_turn": "initiator"
    }
@bot.callback_query_handler(func=lambda call: call.data.startswith("knb_choose_"))
def handle_knb_choice(call):
    parts = call.data.split("_")
    choice = parts[2]
    game_id = parts[3]
    if game_id not in pending_knb_games:
        bot.answer_callback_query(call.id, "❌ Игра не найдена или уже завершена\\.")
        return
    game = pending_knb_games[game_id]
    user_id = call.from_user.id
    chat_id = game["chat_id"]
    if game["current_turn"] == "initiator" and user_id != game["initiator_id"]:
        bot.answer_callback_query(call.id, "⏳ Сейчас ходит другой игрок\\.")
        return
    if game["current_turn"] == "opponent" and user_id != game["opponent_id"]:
        bot.answer_callback_query(call.id, "⏳ Сейчас ходит другой игрок\\.")
        return
    if user_id == game["initiator_id"]:
        game["initiator_choice"] = choice
        game["current_turn"] = "opponent"
        next_player_name = get_clickable_name(chat_id, game["opponent_id"])
        status_text = f"✅ {get_clickable_name(chat_id, user_id)} сделал выбор\\.\n👉 Теперь ходит {next_player_name}\\."
    else:
        game["opponent_choice"] = choice
        status_text = "✅ Оба игрока сделали выбор\nРаскрываем результаты\\.\\.\\."
    bot.answer_callback_query(call.id, f"✅ Выбор принят: {choice}")
    initiator_name = get_clickable_name(chat_id, game["initiator_id"])
    opponent_name = get_clickable_name(chat_id, game["opponent_id"])
    try:
        if user_id == game["opponent_id"]:
            bot.edit_message_text(
                f"🎲 Игра «Камень, Ножницы, Бумага» между {initiator_name} и {opponent_name} на {game['bet']} монет\\.\n{status_text}",
                chat_id=chat_id,
                message_id=game["message_id"],parse_mode='MarkdownV2')
            finalize_knb_game(game_id)
        else:
            new_keyboard = InlineKeyboardMarkup()
            rock_btn = InlineKeyboardButton("🪨 Камень", callback_data=f"knb_choose_rock_{game_id}")
            scissors_btn = InlineKeyboardButton("✂️ Ножницы", callback_data=f"knb_choose_scissors_{game_id}")
            paper_btn = InlineKeyboardButton("📄 Бумага", callback_data=f"knb_choose_paper_{game_id}")
            new_keyboard.add(rock_btn, scissors_btn, paper_btn)
            bot.edit_message_text(
                f"🎲 Игра «Камень, Ножницы, Бумага» между {initiator_name} и {opponent_name} на {game['bet']} монет\\.\n{status_text}",
                chat_id=chat_id,
                message_id=game["message_id"],
                reply_markup=new_keyboard, parse_mode='MarkdownV2')
    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения КНБ: {e}")
def finalize_knb_game(game_id):
    game = pending_knb_games[game_id]
    chat_id = game["chat_id"]
    initiator_id = game["initiator_id"]
    opponent_id = game["opponent_id"]
    bet = game["bet"]
    initiator_choice = game["initiator_choice"]
    opponent_choice = game["opponent_choice"]
    initiator_name = get_clickable_name(chat_id, initiator_id)
    opponent_name = get_clickable_name(chat_id, opponent_id)
    timer = game.get("timer")
    if timer:
        timer.cancel()
    emoji_map = {"rock": "🪨", "scissors": "✂️", "paper": "📄"}
    i_emoji = emoji_map[initiator_choice]
    o_emoji = emoji_map[opponent_choice]
    if initiator_choice == opponent_choice:
        result = "draw"
    elif (initiator_choice == "rock" and opponent_choice == "scissors") or \
         (initiator_choice == "scissors" and opponent_choice == "paper") or \
         (initiator_choice == "paper" and opponent_choice == "rock"):
        result = "initiator_win"
    else:
        result = "opponent_win"
    if chat_id not in knb_stats:
        knb_stats[chat_id] = {}
    if result == "initiator_win":
        knb_stats[chat_id][initiator_id] = knb_stats[chat_id].get(initiator_id, 0) + 1
    elif result == "opponent_win":
        knb_stats[chat_id][opponent_id] = knb_stats[chat_id].get(opponent_id, 0) + 1
    save_knb_stats()
    if result == "initiator_win":
        user_coins[chat_id][initiator_id] = user_coins[chat_id].get(initiator_id, 0) + bet
        user_coins[chat_id][opponent_id] = user_coins[chat_id].get(opponent_id, 0) - bet
    elif result == "opponent_win":
        user_coins[chat_id][opponent_id] = user_coins[chat_id].get(opponent_id, 0) + bet
        user_coins[chat_id][initiator_id] = user_coins[chat_id].get(initiator_id, 0) - bet
    save_coins()
    if result == "draw":
        final_text = f"🎲 Игра между {initiator_name} и {opponent_name} завершилась ничьей\\! {i_emoji} vs {o_emoji}"
    elif result == "initiator_win":
        final_text = f"🎲 Победил\\(а\\) {initiator_name}\\! {i_emoji} vs {o_emoji}"
    else:
        final_text = f"🎲 Победил\\(а\\) {opponent_name}\\! {i_emoji} vs {o_emoji}"
    stats_button = InlineKeyboardMarkup()
    stats_button.add(InlineKeyboardButton("📊 Показать статистику", callback_data=f"knb_show_stats_{chat_id}"))
    try:
        bot.edit_message_text(
            final_text,
            chat_id=chat_id,
            message_id=game["message_id"],
            reply_markup=stats_button,parse_mode='MarkdownV2')
    except Exception as e:
        logger.error(f"Ошибка при отправке финального сообщения КНБ: {e}")
    del pending_knb_games[game_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("knb_show_stats_"))
def show_knb_stats_from_button(call):
    try:
        chat_id = int(call.data.split("_")[-1])
        if chat_id not in knb_stats or not knb_stats[chat_id]:
            bot.answer_callback_query(call.id, "📊 В этом чате ещё никто не выиграл в КНБ.", show_alert=True)
            return
        sorted_players = sorted(knb_stats[chat_id].items(), key=lambda x: x[1], reverse=True)
        lines = []
        for uid, wins in sorted_players:
            name = get_clickable_name(chat_id, uid)
            lines.append(f"• {name}: {wins} побед")
        response = "🏆 *Таблица побед в КНБ в этом чате:*\n" + "\n".join(lines)
        bot.send_message(call.message.chat.id, response, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Ошибка в show_knb_stats_from_button: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при загрузке статистики.", show_alert=True)

@bot.message_handler(commands=['knbstat'])
@error_handler
def show_knb_stats(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in knb_stats or not knb_stats[chat_id]:
        bot.reply_to(message, "📊 В этом чате ещё никто не выиграл в КНБ.")
        return
    sorted_players = sorted(knb_stats[chat_id].items(), key=lambda x: x[1], reverse=True)
    lines = []
    for uid, wins in sorted_players:
        name = get_clickable_name(chat_id, uid)
        lines.append(f"• {name}: {wins} побед")
    response = "🏆 *Таблица побед в КНБ в этом чате:*\n" + "\n".join(lines)
    bot.reply_to(message, response, parse_mode='MarkdownV2')
# 🎯 Триггеры
@bot.message_handler(commands=['trigger'])
@error_handler
def add_trigger(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
        return
    if not can_use_trigger_command(chat_id, user_id):
        bot.reply_to(message, "❌ У тебя нет прав использовать эту команду.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажи подпись после команды:`/trigger мяу`", parse_mode='MarkdownV2')
        return
    phrase = args[1].strip()
    if not phrase:
        bot.reply_to(message, "❌ Подпись не может быть пустой.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответь на медиафайл (стикер, фото, видео, GIF, аудио, документ) или текстовое сообщение этой командой.")
        return
    media_file_id = None
    media_type = None
    text_reply = None
    if message.reply_to_message.sticker:
        media_file_id = message.reply_to_message.sticker.file_id
        media_type = "sticker"
    elif message.reply_to_message.photo:
        media_file_id = message.reply_to_message.photo[-1].file_id
        media_type = "photo"
    elif message.reply_to_message.video:
        media_file_id = message.reply_to_message.video.file_id
        media_type = "video"
    elif message.reply_to_message.animation:
        media_file_id = message.reply_to_message.animation.file_id
        media_type = "animation"
    elif message.reply_to_message.audio:
        media_file_id = message.reply_to_message.audio.file_id
        media_type = "audio"
    elif message.reply_to_message.voice:
        media_file_id = message.reply_to_message.voice.file_id
        media_type = "voice"
    elif message.reply_to_message.document:
        media_file_id = message.reply_to_message.document.file_id
        media_type = "document"
    elif message.reply_to_message.text:
        text_reply = message.reply_to_message.text
        media_type = "text"
    if not media_file_id and not text_reply:
        bot.reply_to(message, "❌ Не удалось распознать медиа или текст в ответе. Попробуйте ещё раз.")
        return
    new_trigger = {"type": media_type}
    if media_type == "text":
        new_trigger["text"] = text_reply
    else:
        new_trigger["file_id"] = media_file_id
    if chat_id not in chat_triggers:
        chat_triggers[chat_id] = {}
    phrase_lower = phrase.lower()
    escaped_phrase = escape_markdown_v2(phrase)
    if phrase_lower in chat_triggers[chat_id]:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔄 Заменить", callback_data=f"trig_replace_{chat_id}_{phrase_lower}"))
        keyboard.add(InlineKeyboardButton("➕ Добавить", callback_data=f"trig_addmulti_{chat_id}_{phrase_lower}"))
        keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="trig_cancel"))
        pending_triggers[f"{chat_id}_{user_id}_{phrase_lower}"] = new_trigger
        bot.reply_to(message, f"⚠️ Триггер «{escaped_phrase}» уже существует\\. Что сделать?", reply_markup=keyboard, parse_mode='MarkdownV2')
    else:
        chat_triggers[chat_id][phrase_lower] = [new_trigger]
        save_triggers()
        bot.reply_to(message, f"✅ Триггер «{escaped_phrase}» сохранён\\!", parse_mode='MarkdownV2')

@bot.message_handler(commands=['deletetrigger'])
@error_handler
def delete_trigger(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if not can_use_trigger_command(chat_id, user_id):
        bot.reply_to(message, "❌ У тебя нет прав удалять триггеры.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажи подпись триггера для удаления:\n/deletetrigger мяу")
        return
    phrase = args[1].strip()
    if not phrase:
        bot.reply_to(message, "❌ Подпись не может быть пустой.")
        return
    if chat_id not in chat_triggers or not chat_triggers[chat_id]:
        bot.reply_to(message, "📭 В этом чате ещё нет триггеров.")
        return
    phrase_lower = phrase.lower()
    if phrase_lower in chat_triggers[chat_id]:
        del chat_triggers[chat_id][phrase_lower]
        save_triggers()
        escaped_phrase = escape_markdown_v2(phrase)
        bot.reply_to(message, f"🗑️ Все триггеры для «{escaped_phrase}» успешно удалены\\.", parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, f"❌ Триггер «{phrase}» не найден.")

@bot.message_handler(commands=['execut'])
@error_handler
def start_execut(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not is_user_chat_owner(chat_id, user_id):
        bot.reply_to(message, "❌ Только создатель чата может использовать эту команду.")
        return
    if chat_id in execut_queue:
        bot.reply_to(message, "⚠️ Операция /execut уже запущена в этом чате.")
        return
    regular_users = set()
    bots = set()
    bot_id = bot.get_me().id
    if chat_id in chat_members_cache:
        for uid, data in chat_members_cache[chat_id].items():
            if uid == bot_id:
                continue
            regular_users.add(uid)
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            uid = admin.user.id
            if uid == bot_id:
                continue
            if admin.user.is_bot:
                bots.add(uid)
            else:
                regular_users.add(uid)
    except Exception as e:
        logger.warning(f"[EXECUT] Не удалось получить админов чата {chat_id}: {e}")
    regular_users -= bots
    all_members = list(regular_users) + list(bots)

    logger.info(f"[EXECUT] Найдено {len(regular_users)} обычных участников и {len(bots)} ботов в чате {chat_id}")
    if not all_members:
        bot.reply_to(message, "📭 В чате нет известных участников для исключения.")
        return

    execut_queue[chat_id] = all_members
    save_execut_queue()
    bot.reply_to(
        message,
        f"✅ Запущена операция *ликвидации*.\n"
        f"Будет исключено {len(regular_users)} участников по одному каждые 60 минут.\n"
        f"После завершения — бот покинет чат.",
        parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("minesweeper_join_"))
def handle_minesweeper_join(call):
    chat_id = int(call.data.split("_")[-1])
    user_id = call.from_user.id
    
    if chat_id not in minesweeper_data or not minesweeper_data[chat_id].get("accepting"):
        bot.answer_callback_query(call.id, "❌ Событие уже завершено.", show_alert=True)
        return
    
    excluded = minesweeper_data[chat_id].get("excluded_players", [])
    if user_id in excluded:
        bot.answer_callback_query(call.id, "❌ Ты уже проиграл в этом событии.", show_alert=True)
        return
    
    # Останавливаем приём заявок
    minesweeper_data[chat_id]["accepting"] = False
    
    # Удаляем сообщение с кнопкой участия
    try:
        accept_msg_id = minesweeper_data[chat_id].get("accept_message_id")
        if accept_msg_id:
            bot.delete_message(chat_id, accept_msg_id)
    except:
        pass
    
    # Создаём игру
    field = generate_minesweeper_field()
    revealed = [[False for _ in range(MINESWEEPER_FIELD_SIZE)] for _ in range(MINESWEEPER_FIELD_SIZE)]
    
    game_data = {
        "chat_id": chat_id,
        "player_id": user_id,
        "field": field,
        "revealed": revealed,
        "safe_revealed": 0,
        "safe_to_win": MINESWEEPER_SAFE_TO_WIN,
        "message_id": None
    }
    
    keyboard = create_minesweeper_keyboard(game_data)
    status_text = get_minesweeper_status_text(game_data, "playing")
    
    try:
        msg = bot.send_message(chat_id, status_text, reply_markup=keyboard, parse_mode='MarkdownV2')
        game_data["message_id"] = msg.message_id
        minesweeper_data[chat_id]["active_game"] = game_data
        save_minesweeper_data()
        bot.answer_callback_query(call.id, "🎮 Игра началась!")
        logger.info(f"[MINESWEEPER] Игрок {user_id} начал игру в чате {chat_id}")
    except Exception as e:
        logger.error(f"[MINESWEEPER] Ошибка создания игры: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка создания игры.", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("minesweeper_click_"))
def handle_minesweeper_click(call):
    parts = call.data.split("_")
    chat_id = int(parts[2])
    x = int(parts[3])
    y = int(parts[4])
    user_id = call.from_user.id
    
    if chat_id not in minesweeper_data:
        bot.answer_callback_query(call.id, "❌ Игра не найдена.", show_alert=True)
        return
    
    game_data = minesweeper_data[chat_id].get("active_game")
    if not game_data:
        bot.answer_callback_query(call.id, "❌ Нет активной игры.", show_alert=True)
        return
    
    if user_id != game_data["player_id"]:
        player_name = get_clickable_name(chat_id, game_data["player_id"])
        bot.answer_callback_query(call.id, "👀 Ты можешь только наблюдать.", show_alert=True)
        return
    
    if game_data["revealed"][y][x]:
        bot.answer_callback_query(call.id, "Уже открыто!", show_alert=False)
        return
    
    # Открываем клетку
    game_data["revealed"][y][x] = True
    cell_value = game_data["field"][y][x]
    
    if cell_value == -1:
        # ПРОИГРЫШ - наступил на мину
        if chat_id not in minesweeper_stats:
            minesweeper_stats[chat_id] = {}
        if user_id not in minesweeper_stats[chat_id]:
            minesweeper_stats[chat_id][user_id] = {"wins": 0, "losses": 0}
        minesweeper_stats[chat_id][user_id]["losses"] += 1
        
        # Показываем всё поле
        keyboard = create_minesweeper_keyboard(game_data, game_over=True, show_all=True)
        status_text = get_minesweeper_status_text(game_data, "lose")
        
        try:
            bot.edit_message_text(
                status_text,
                chat_id=chat_id,
                message_id=game_data["message_id"],
                reply_markup=keyboard,
                parse_mode='MarkdownV2'
            )
        except Exception as e:
            logger.warning(f"[MINESWEEPER] Ошибка обновления сообщения: {e}")
        
        bot.answer_callback_query(call.id, "💥 БУМ! Ты проиграл!", show_alert=True)
        
        minesweeper_data[chat_id]["active_game"] = None
        save_minesweeper_data()
        
        logger.info(f"[MINESWEEPER] Игрок {user_id} проиграл в чате {chat_id}")
        
        # Перезапускаем приём заявок через 3 секунды
        def delayed_restart():
            time.sleep(3)
            restart_minesweeper_accepting(chat_id, user_id)
        
        threading.Thread(target=delayed_restart, daemon=True).start()
        
    else:
        # Безопасная клетка
        game_data["safe_revealed"] += 1
        
        if game_data["safe_revealed"] >= game_data["safe_to_win"]:
            # ПОБЕДА!
            if chat_id not in minesweeper_stats:
                minesweeper_stats[chat_id] = {}
            if user_id not in minesweeper_stats[chat_id]:
                minesweeper_stats[chat_id][user_id] = {"wins": 0, "losses": 0}
            minesweeper_stats[chat_id][user_id]["wins"] += 1
            
            # Выдаём награду
            if chat_id not in user_coins:
                user_coins[chat_id] = {}
            user_coins[chat_id][user_id] = user_coins[chat_id].get(user_id, 0) + MINESWEEPER_REWARD
            save_coins()
            
            # Показываем всё поле
            keyboard = create_minesweeper_keyboard(game_data, game_over=True, show_all=True)
            status_text = get_minesweeper_status_text(game_data, "win")
            
            try:
                bot.edit_message_text(
                    status_text,
                    chat_id=chat_id,
                    message_id=game_data["message_id"],
                    reply_markup=keyboard,
                    parse_mode='MarkdownV2'
                )
            except Exception as e:
                logger.warning(f"[MINESWEEPER] Ошибка обновления сообщения: {e}")
            
            bot.answer_callback_query(call.id, f"🎉 ПОБЕДА! +{MINESWEEPER_REWARD} монет!", show_alert=True)
            
            # Устанавливаем следующее событие через день
            minesweeper_data[chat_id]["active_game"] = None
            minesweeper_data[chat_id]["excluded_players"] = []
            minesweeper_data[chat_id]["next_event_time"] = time.time() + 86400 + random.randint(0, 43200)  # 24-36 часов
            save_minesweeper_data()
            
            logger.info(f"[MINESWEEPER] Игрок {user_id} выиграл в чате {chat_id}")
            
        else:
            # Продолжаем игру
            keyboard = create_minesweeper_keyboard(game_data)
            status_text = get_minesweeper_status_text(game_data, "playing")
            
            try:
                bot.edit_message_text(
                    status_text,
                    chat_id=chat_id,
                    message_id=game_data["message_id"],
                    reply_markup=keyboard,
                    parse_mode='MarkdownV2'
                )
            except Exception as e:
                logger.warning(f"[MINESWEEPER] Ошибка обновления сообщения: {e}")
            
            remaining = game_data["safe_to_win"] - game_data["safe_revealed"]
            bot.answer_callback_query(call.id, f"✅ Осталось: {remaining}")
        
        minesweeper_data[chat_id]["active_game"] = game_data
        save_minesweeper_data()


@bot.callback_query_handler(func=lambda call: call.data == "minesweeper_noop")
def handle_minesweeper_noop(call):
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("trig_replace_"))
def handle_replace_trigger(call):
    _, _, chat_id_str, phrase = call.data.split("_", 3)
    chat_id = int(chat_id_str)
    user_id = call.from_user.id
    if not can_use_trigger_command(chat_id, user_id):
        bot.answer_callback_query(call.id, "❌ У тебя нет прав управлять триггерами.", show_alert=True)
        return
    key = f"{chat_id}_{user_id}_{phrase}"
    if key not in pending_triggers:
        logger.warning(f"Key '{key}' not found in pending_triggers during replace operation.")
        bot.edit_message_text("❌ Произошла ошибка при замене триггера. Попробуйте снова.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    new_trigger = pending_triggers.pop(key)
    if chat_id not in chat_triggers or phrase not in chat_triggers[chat_id]:
        logger.warning(f"Trigger phrase '{phrase}' not found in chat_triggers[{chat_id}] during replace operation.")
        bot.edit_message_text("❌ Триггер больше не существует. Попробуйте создать новый.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    chat_triggers[chat_id][phrase] = [new_trigger]
    save_triggers()
    bot.edit_message_text("✅ Триггер успешно заменён!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("trig_addmulti_"))
def handle_add_multi_trigger(call):
    _, _, chat_id_str, phrase = call.data.split("_", 3)
    chat_id = int(chat_id_str)
    user_id = call.from_user.id
    if not can_use_trigger_command(chat_id, user_id):
        bot.answer_callback_query(call.id, "❌ У тебя нет прав управлять триггерами.", show_alert=True)
        return
    key = f"{chat_id}_{user_id}_{phrase}"
    if key not in pending_triggers:
        logger.warning(f"Key '{key}' not found in pending_triggers during addmulti operation.")
        bot.edit_message_text("❌ Произошла ошибка при добавлении триггера. Попробуйте снова.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    new_trigger = pending_triggers.pop(key)
    if chat_id not in chat_triggers or phrase not in chat_triggers[chat_id]:
        logger.warning(f"Trigger phrase '{phrase}' not found in chat_triggers[{chat_id}] during addmulti operation.")
        bot.edit_message_text("❌ Триггер больше не существует. Попробуйте создать новый.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    chat_triggers[chat_id][phrase].append(new_trigger)
    save_triggers()
    bot.edit_message_text("✅ Новый триггер успешно добавлен к существующему!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "trig_cancel")
def handle_cancel_trigger(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    if not can_use_trigger_command(chat_id, user_id):
        bot.answer_callback_query(call.id, "❌ У тебя нет прав управлять триггерами.", show_alert=True)
        return
    bot.edit_message_text("❌ Действие отменено.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['triggersettings'])
@error_handler
def open_trigger_settings(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_owner = is_user_chat_owner(chat_id, user_id)
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
        return
    if chat_id not in chat_features:
        chat_features[chat_id] = {"kidnap_game": True}
        save_features()
    if chat_id not in trigger_access:
        trigger_access[chat_id] = {"mode": "creator", "allowed_users": []}
        save_trigger_access()
    mode = trigger_access[chat_id]["mode"]
    mode_text = {
        "creator": "только создатель",
        "admins": "админы",
        "members": "все участники"
    }.get(mode, "только создатель")
    safe_mode_text = escape_markdown_v2(mode_text)
    help_text = (
        "🛠 *Настройки триггеров*\n"
        f"Текущий режим: *{safe_mode_text}*\n"
        "Только создатель чата может менять настройки\\.\n"
        "Все могут просматривать инструкцию и список триггеров\\.")
    keyboard = InlineKeyboardMarkup(row_width=1)
    if is_owner:
        keyboard.add(
            InlineKeyboardButton("👥 Кто может добавлять триггеры", callback_data="trig_set_mode"),
            InlineKeyboardButton("📋 Список пользователей", callback_data="trig_list_allowed_0"),
            InlineKeyboardButton("🕹️ Игры: ВКЛ" if chat_features[chat_id]["kidnap_game"] else "🕹️ Игры: ВЫКЛ", callback_data="toggle_kidnap_game"),
            InlineKeyboardButton("🗑️ Сбросить всё", callback_data="trig_reset_all"))
    keyboard.add(
        InlineKeyboardButton("📄 Инструкция", callback_data="trig_help_embedded"),
        InlineKeyboardButton("🔍 Посмотреть триггеры", callback_data="trig_list_0"),
        InlineKeyboardButton("🎰 Инфо о казино", callback_data="casino_info"))
    bot.reply_to(message, help_text, reply_markup=keyboard, parse_mode='MarkdownV2')
@bot.callback_query_handler(func=lambda call: call.data.startswith("trig_") or call.data in ["back_to_settings", "casino_info", "toggle_kidnap_game"])
def handle_trigger_settings(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    is_owner = is_user_chat_owner(chat_id, user_id)
    data = call.data

    # 🔑 КРИТИЧЕСКИ ВАЖНО: инициализируем chat_features ДО любых обращений к нему
    if chat_id not in chat_features:
        chat_features[chat_id] = {"kidnap_game": True}
        save_features()

    # Защита от не-владельцев для опасных действий
    if data in ["trig_set_mode", "trig_reset_all", "trig_reset_confirm", "toggle_kidnap_game"] or \
       data.startswith("trig_remove_user_") or data.startswith("trig_mode_"):
        if not is_owner:
            bot.answer_callback_query(call.id, "❌ Только создатель чата может это делать.", show_alert=True)
            return
    if data == "casino_info":
        info_text = (
            "🎰 *Как работает казино\\?*\n"
            "• Доступно раз в 3 часа\\.\n"
            "• Используй: `/casino <ставка>`\n"
            "*Множители и эмодзи:*\n"
            "💀 — x0 \\(проигрыш\\)\n"
            "🪙 — x1\\.5\n"
            "💰 — x2\n"
            "💎 — x3\n"
            "🔥 — x5\n"
            "✨ — x10 \\(очень редко\\!\\)\n"
            "🏆 Чистая прибыль \\= \\(ставка × множитель\\) − ставка\n"
            "📊 Топ игроков: `/casinostat`"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text(info_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return

    if data == "trig_help_embedded":
        help_msg = (
            "ℹ️ *Инструкция по триггерам*\n"
            "1\\. Чтобы создать триггер:\n"
            "— Ответьте на стикер, фото, видео, аудио, гиф или документ командой `/trigger привет`\n"
            "— Теперь при слове «привет» бот отправит сообщение, которое вы отметили\n"
            "— Триггеры можно накладывать друг на друга\n"
            "2\\. Удалить триггер:\n"
            " —  `/deletetrigger привет`\n"
            "3\\. Менять настройки может только создатель чата\n"
            "4\\. В режиме «выбранные пользователи» используйте:\n"
            " — `/addtriggerright @username`, в ответ на сообщение или по ID"
        )
        back_button = InlineKeyboardMarkup()
        back_button.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text(help_msg, chat_id=chat_id, message_id=call.message.message_id, reply_markup=back_button, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return

    if data.startswith("trig_list_allowed_"):
        page = int(data.split("_")[-1])
        allowed_users = trigger_access.get(chat_id, {}).get("allowed_users", [])
        if not allowed_users:
            bot.answer_callback_query(call.id, "📭 Нет пользователей с правами.")
            return
        items_per_page = 5
        total_pages = (len(allowed_users) + items_per_page - 1) // items_per_page
        start = page * items_per_page
        end = start + items_per_page
        page_users = allowed_users[start:end]
        lines = []
        for uid in page_users:
            name = get_clickable_name(chat_id, uid)
            lines.append(f"• {name} \\(ID: `{uid}`\\)")
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️", callback_data=f"trig_list_allowed_{page-1}"))
        nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("➡️", callback_data=f"trig_list_allowed_{page+1}"))
        keyboard = InlineKeyboardMarkup()
        if nav:
            keyboard.row(*nav)
        for uid in page_users:
            keyboard.add(InlineKeyboardButton(f"🗑 Удалить {uid}", callback_data=f"trig_remove_user_{uid}"))
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        response = "📋 *Пользователи с правом добавлять триггеры:*\n" + "\n".join(lines)
        bot.edit_message_text(response, chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data.startswith("trig_remove_user_"):
        target_uid = int(data.split("_")[-1])
        if chat_id in trigger_access and target_uid in trigger_access[chat_id]["allowed_users"]:
            trigger_access[chat_id]["allowed_users"].remove(target_uid)
            save_trigger_access()
            bot.answer_callback_query(call.id, "✅ Пользователь удалён из списка.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден в списке.", show_alert=True)
        handle_trigger_settings(call)
        return

    if data.startswith("trig_list_"):
        page = int(data.split("_")[-1])
        triggers = chat_triggers.get(chat_id, {})
        if not triggers:
            bot.answer_callback_query(call.id, "📭 Нет сохранённых триггеров.")
            return
        sorted_phrases = sorted(triggers.keys())
        items_per_page = 10
        total_pages = (len(sorted_phrases) + items_per_page - 1) // items_per_page
        start = page * items_per_page
        end = start + items_per_page
        page_phrases = sorted_phrases[start:end]
        lines = [f"• {escape_markdown_v2(phrase)}" for phrase in page_phrases]
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️", callback_data=f"trig_list_{page-1}"))
        nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("➡️", callback_data=f"trig_list_{page+1}"))
        keyboard = InlineKeyboardMarkup()
        if nav:
            keyboard.row(*nav)
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        response = f"📄 *Список триггеров \\(стр\\. {page+1}\\):*\n" + "\n".join(lines)
        bot.edit_message_text(response, chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return

    if data == "toggle_kidnap_game":
     chat_id = call.message.chat.id
     current_state = chat_features.get(chat_id, {}).get("kidnap_game", True)
     new_state = not current_state
     chat_features[chat_id] = {"kidnap_game": new_state}
     save_features()
     if not new_state:
        paused_timers[chat_id] = time.time()
     else:
        if chat_id in paused_timers:
            pause_start = paused_timers.pop(chat_id)
            pause_duration = time.time() - pause_start
            for uid in last_kidnap_attempt.get(chat_id, {}):
                last_kidnap_attempt[chat_id][uid] += pause_duration
            for uid in last_job_attempt.get(chat_id, {}):
                last_job_attempt[chat_id][uid] += pause_duration
            for uid in last_casino_attempt.get(chat_id, {}):
                last_casino_attempt[chat_id][uid] += pause_duration
            for (k, v), ts in list(steal_timers.get(chat_id, {}).items()):
                steal_timers[chat_id][(k, v)] = ts + pause_duration
            save_kidnap_data()
            save_job_cooldown()
            save_casino_data()
            save_steal_timers()
     status = "включены" if new_state else "отключены"
     bot.answer_callback_query(call.id, f"✅ Мини-игры {status}.", show_alert=True)
     mode = trigger_access.get(chat_id, {}).get("mode", "creator")
     mode_text = {
        "creator": "только создатель",
        "admins": "админы",
        "members": "все участники"
     }.get(mode, "только создатель")
     keyboard = InlineKeyboardMarkup(row_width=1)
     is_owner = is_user_chat_owner(chat_id, call.from_user.id)
     if is_owner:
        keyboard.add(
            InlineKeyboardButton("👥 Кто может добавлять триггеры", callback_data="trig_set_mode"),
            InlineKeyboardButton("📋 Список пользователей", callback_data="trig_list_allowed_0"),
            InlineKeyboardButton("🕹️ Игры: ВКЛ" if chat_features[chat_id]["kidnap_game"] else "🕹️ Игры: ВЫКЛ", callback_data="toggle_kidnap_game"),
            InlineKeyboardButton("🗑️ Сбросить всё", callback_data="trig_reset_all"))
     keyboard.add(
        InlineKeyboardButton("📄 Инструкция", callback_data="trig_help_embedded"),
        InlineKeyboardButton("🔍 Посмотреть триггеры", callback_data="trig_list_0"),
        InlineKeyboardButton("🎰 Инфо о казино", callback_data="casino_info"))
     help_text = (
        "🛠 *Настройки триггеров*\n"
        f"Текущий режим: *{escape_markdown_v2(mode_text)}*\n"
        "Только создатель чата может менять настройки.\n"
        "Все могут просматривать инструкцию и список триггеров.")
     try:
        bot.edit_message_text(
            help_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode='MarkdownV2')
     except Exception as e:
        logger.warning(f"Не удалось обновить сообщение после toggle_kidnap_game: {e}")
     return
    if data == "trig_reset_all":
        confirm_keyboard = InlineKeyboardMarkup()
        confirm_keyboard.add(
            InlineKeyboardButton("✅ Да, сбросить всё", callback_data="trig_reset_confirm"),
            InlineKeyboardButton("❌ Отмена", callback_data="back_to_settings"))
        bot.edit_message_text(
            "⚠️ Ты уверен\\(а\\), что хочешь *полностью сбросить все триггеры и настройки*\\?\n"
            "Это действие *невозможно отменить*\\.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=confirm_keyboard,parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data == "trig_reset_confirm":
        chat_triggers.pop(chat_id, None)
        trigger_access.pop(chat_id, None)
        save_triggers()
        save_trigger_access()
        back_kb = InlineKeyboardMarkup()
        back_kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text("✅ Все триггеры и настройки сброшены\\!", chat_id=chat_id, message_id=call.message.message_id, reply_markup=back_kb)
        bot.answer_callback_query(call.id)
        return
    if data == "trig_set_mode":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("👤 Только создатель", callback_data="trig_mode_creator"),
            InlineKeyboardButton("🛡️ Админы", callback_data="trig_mode_admins"),
            InlineKeyboardButton("👥 Все участники", callback_data="trig_mode_members"),
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        help_text = (
            "Выбери, кто может добавлять триггеры:\n"
            "✏️ Чтобы выдать право конкретному пользователю, отправь команду в формате:\n"
            "`/addtriggerright @username`\n"
            "или ответь на сообщение пользователя командой `/addtriggerright`")
        bot.edit_message_text(help_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data.startswith("trig_mode_"):
        mode = data.split("_")[-1]
        trigger_access[chat_id]["mode"] = mode
        trigger_access[chat_id]["allowed_users"] = []
        save_trigger_access()
        back_kb = InlineKeyboardMarkup()
        back_kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text("✅ Режим успешно изменён\\!", chat_id=chat_id, message_id=call.message.message_id, reply_markup=back_kb)
        bot.answer_callback_query(call.id)
        return
    if data == "back_to_settings":
        mode = trigger_access[chat_id]["mode"]
        mode_text = {
            "creator": "только создатель",
            "admins": "админы",
            "members": "все участники"
        }.get(mode, "только создатель")
        keyboard = InlineKeyboardMarkup(row_width=1)
        if is_owner:
            keyboard.add(
                InlineKeyboardButton("👥 Кто может добавлять триггеры", callback_data="trig_set_mode"),
                InlineKeyboardButton("📋 Список пользователей", callback_data="trig_list_allowed_0"),
                InlineKeyboardButton("🕹️ Игры: ВКЛ" if chat_features[chat_id]["kidnap_game"] else "🕹️ Игры: ВЫКЛ", callback_data="toggle_kidnap_game"),
                InlineKeyboardButton("🗑️ Сбросить всё", callback_data="trig_reset_all"))
        keyboard.add(
            InlineKeyboardButton("📄 Инструкция", callback_data="trig_help_embedded"),
            InlineKeyboardButton("🔍 Посмотреть триггеры", callback_data="trig_list_0"),
            InlineKeyboardButton("🎰 Инфо о казино", callback_data="casino_info"))
        help_text = (
            "🛠 *Настройки триггеров*\n"
            f"Текущий режим: *{escape_markdown_v2(mode_text)}*\n"
            "Только создатель чата может менять настройки\\.\n"
            "Все могут просматривать инструкцию и список триггеров\\.")
        bot.edit_message_text(help_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard, parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data == "trig_set_mode":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👤 Только создатель", callback_data="trig_mode_creator"))
        keyboard.add(InlineKeyboardButton("🛡️ Админы", callback_data="trig_mode_admins"))
        keyboard.add(InlineKeyboardButton("👥 Все участники", callback_data="trig_mode_members"))
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        help_text = (
            "Выбери, кто может добавлять триггеры:\n\n"
            "✏️ Чтобы выдать право конкретному пользователю, отправь команду в формате:\n"
            "`/addtriggerright @username`\n"
            "или ответь на сообщение пользователя командой `/addtriggerright`")
        bot.edit_message_text(
            help_text,
            chat_id=chat_id,
            message_id=call.message.message_id,reply_markup=keyboard,parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data.startswith("trig_mode_"):
        mode = data.split("_")[-1]
        trigger_access[chat_id]["mode"] = mode
        trigger_access[chat_id]["allowed_users"] = []
        save_trigger_access()
        back_kb = InlineKeyboardMarkup()
        back_kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text(
            "✅ Режим успешно изменён!",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=back_kb)
        bot.answer_callback_query(call.id)
        return
    if data == "trig_reset_all":
        confirm_keyboard = InlineKeyboardMarkup()
        confirm_keyboard.add(
            InlineKeyboardButton("✅ Да, сбросить всё", callback_data="trig_reset_confirm"),
            InlineKeyboardButton("❌ Отмена", callback_data="back_to_settings"))
        bot.edit_message_text(
            "⚠️ Ты уверен\\(а\\), что хочешь *полностью сбросить все триггеры и настройки*\\?\n"
            "Это действие *невозможно отменить*\\.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=confirm_keyboard,parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return
    if data == "trig_reset_confirm":
        chat_triggers.pop(chat_id, None)
        trigger_access.pop(chat_id, None)
        save_triggers()
        save_trigger_access()
        back_kb = InlineKeyboardMarkup()
        back_kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_settings"))
        bot.edit_message_text(
            "✅ Все триггеры и настройки сброшены\\!",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=back_kb,parse_mode='MarkdownV2')
        bot.answer_callback_query(call.id)
        return

@bot.message_handler(commands=['addtriggerright'])
@error_handler
def add_user_to_trigger_access(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if not is_user_chat_owner(chat_id, user_id):
        bot.reply_to(message, "❌ Только создатель чата может выдавать права.")
        return
    target_id = None
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_user = message.reply_to_message.from_user
        ensure_user_in_cache(chat_id, target_id, target_user)
    else:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Укажи @username или ответь на сообщение.")
            return
        username = args[1].lstrip('@')
        if not username:
            bot.reply_to(message, "❌ Некорректный username.")
            return
        found = False
        for uid, data in chat_members_cache.get(chat_id, {}).items():
            if data.get("username") == username:
                target_id = uid
                found = True
                break
        if not found:
            bot.reply_to(message, "❌ Пользователь не найден в кэше. Пусть он напишет что-нибудь в чат.")
            return
    if chat_id not in trigger_access:
        trigger_access[chat_id] = {"mode": "creator", "allowed_users": []}
    if target_id not in trigger_access[chat_id]["allowed_users"]:
        trigger_access[chat_id]["allowed_users"].append(target_id)
        save_trigger_access()
        target_name = get_clickable_name(chat_id, target_id)
        bot.reply_to(message, f"✅ Пользователь {target_name} получил право добавлять триггеры\\.", parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, "ℹ️ Этот пользователь уже имеет право.")

@bot.message_handler(commands=['resettriggers'])
@error_handler
def reset_all_triggers(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if not is_user_chat_owner(chat_id, user_id):
        bot.reply_to(message, "❌ Только создатель чата может сбросить триггеры.")
        return
    chat_triggers.pop(chat_id, None)
    trigger_access.pop(chat_id, None)
    save_triggers()
    save_trigger_access()
    bot.reply_to(message, "✅ Все триггеры и настройки сброшены до значений по умолчанию\\.")

@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith("сомка кто ") and message.chat.type in ['group', 'supergroup'])
@error_handler
def handle_somka_who(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалён запрос 'Сомка кто' от замученного пользователя {user_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить 'Сомка кто' от замученного: {e}")
        return
    text = message.text[len("сомка кто "):].strip()
    if not text:
        bot.reply_to(message, "❌ Напиши что-то после «Сомка кто».\nПример: Сомка кто любит пиццу?")
        return
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        ensure_user_in_cache(chat_id, target_user.id, target_user)
    if chat_id not in chat_members_cache or not chat_members_cache[chat_id]:
        bot.reply_to(message, "🤷‍♂️ Не удалось получить список участников.")
        return
    available_users = list(chat_members_cache[chat_id].keys())
    if not available_users:
        bot.reply_to(message, "🤷‍♂️ Я пока не знаю ни одного пользователя в этом чате.")
        return
    user_id = random.choice(available_users)
    user_data = chat_members_cache[chat_id][user_id]
    username = user_data.get("username")
    escaped_query = escape_markdown_v2(text)
    if username:
        response = f'Мне кажется, "{escaped_query}" — @{username}'
        bot.reply_to(message, response)
    else:
        user_link = get_clickable_name(chat_id, user_id)  # уже экранировано и в MarkdownV2
        response = f'Мне кажется, "{escaped_query}" — {user_link}'
        bot.reply_to(message, response, parse_mode='MarkdownV2')
        
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("сомка фото ") and m.chat.type in ['group', 'supergroup'])
@error_handler
def search_image(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        return
    
    query = message.text[len("сомка фото "):].strip()
    if not query:
        bot.reply_to(message, "❌ Укажи запрос\\. Пример: `Сомка фото котики`", parse_mode='MarkdownV2')
        return
    
    loading_msg = bot.reply_to(message, "🔍 Ищу картинку...")
    
    try:
        headers = {
            "Authorization": PEXELS_API_KEY
        }
        
        encoded_query = quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page=15&locale=ru-RU"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logger.info(f"[IMAGE_SEARCH] Pexels ответ: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            
            if not photos:
                bot.edit_message_text("❌ Ничего не найдено\\. Попробуй другой запрос\\.", chat_id=chat_id, message_id=loading_msg.message_id, parse_mode='MarkdownV2')
                return
            
            # Выбираем случайное фото
            photo = random.choice(photos)
            image_url = photo["src"]["large"]  # Можно также: original, large2x, medium, small
            photographer = photo.get("photographer", "Unknown")
            
            bot.delete_message(chat_id, loading_msg.message_id)
            
            escaped_query = escape_markdown_v2(query)
            escaped_author = escape_markdown_v2(photographer)
            caption = f"🔍 *{escaped_query}*\n📷 {escaped_author} \\(Pexels\\)"
            
            bot.send_photo(
                chat_id, 
                image_url, 
                caption=caption,
                reply_to_message_id=message.message_id,
                parse_mode='MarkdownV2'
            )
            logger.info(f"[IMAGE_SEARCH] Успешно: '{query}' от {user_id}")
            
        elif response.status_code == 401:
            logger.error("[IMAGE_SEARCH] Неверный API ключ Pexels")
            bot.edit_message_text("❌ Ошибка авторизации API\\.", chat_id=chat_id, message_id=loading_msg.message_id, parse_mode='MarkdownV2')
        else:
            logger.error(f"[IMAGE_SEARCH] Ошибка Pexels: {response.status_code}")
            bot.edit_message_text("❌ Ошибка поиска\\. Попробуй позже\\.", chat_id=chat_id, message_id=loading_msg.message_id, parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f"[IMAGE_SEARCH] Ошибка: {e}")
        try:
            bot.edit_message_text("❌ Ошибка поиска\\. Попробуй позже\\.", chat_id=chat_id, message_id=loading_msg.message_id, parse_mode='MarkdownV2')
        except:
            pass
            
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("сомка нарисуй ") and m.chat.type in ['group', 'supergroup'])
@error_handler
def generate_image(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        return
    
    prompt = message.text[len("сомка нарисуй "):].strip()
    if not prompt:
        bot.reply_to(message, "❌ Укажи что нарисовать\\. Пример: `Сомка нарисуй кот в космосе`", parse_mode='MarkdownV2')
        return
    
    if len(prompt) > 500:
        bot.reply_to(message, "❌ Слишком длинный запрос\\. Максимум 500 символов\\.", parse_mode='MarkdownV2')
        return
    
    loading_msg = bot.reply_to(message, "🎨 Генерирую изображение... Это может занять 15-60 секунд.")
    
    success = False
    image_data = None
    
    # Список серверов для попыток
    servers = [
        {
            "name": "Pollinations",
            "url": lambda p, s: f"https://image.pollinations.ai/prompt/{quote(p)}?seed={s}&width=1024&height=1024&nologo=true&model=flux"
        },
        {
            "name": "Pollinations Turbo",
            "url": lambda p, s: f"https://image.pollinations.ai/prompt/{quote(p)}?seed={s}&width=512&height=512&nologo=true&model=turbo"
        },
    ]
    
    seed = random.randint(1, 999999)
    
    for server in servers:
        if success:
            break
            
        try:
            url = server["url"](prompt, seed)
            logger.info(f"[IMAGE_GEN] Попытка {server['name']}...")
            
            response = requests.get(url, timeout=90, stream=True)
            
            if response.status_code == 200:
                image_data = response.content
                
                # Проверяем что это реально изображение
                if len(image_data) > 5000 and (image_data[:4] == b'\xff\xd8\xff\xe0' or image_data[:8] == b'\x89PNG\r\n\x1a\n'):
                    success = True
                    logger.info(f"[IMAGE_GEN] Успех с {server['name']}, размер: {len(image_data)}")
                else:
                    logger.warning(f"[IMAGE_GEN] {server['name']} вернул не изображение")
            else:
                logger.warning(f"[IMAGE_GEN] {server['name']} вернул {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"[IMAGE_GEN] Timeout для {server['name']}")
        except Exception as e:
            logger.warning(f"[IMAGE_GEN] Ошибка {server['name']}: {e}")
    
    if success and image_data:
        try:
            bot.delete_message(chat_id, loading_msg.message_id)
        except:
            pass
        
        photo = BytesIO(image_data)
        photo.name = "generated.png"
        
        escaped_prompt = escape_markdown_v2(prompt[:100])
        caption = f"🎨 *Запрос:* {escaped_prompt}"
        
        try:
            bot.send_photo(
                chat_id, 
                photo, 
                caption=caption,
                reply_to_message_id=message.message_id,
                parse_mode='MarkdownV2'
            )
            logger.info(f"[IMAGE_GEN] Отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"[IMAGE_GEN] Ошибка отправки фото: {e}")
            bot.send_message(chat_id, "❌ Не удалось отправить изображение\\.", parse_mode='MarkdownV2')
    else:
        try:
            bot.edit_message_text(
                "❌ Все серверы генерации недоступны\\. Попробуй позже\\.",
                chat_id=chat_id,
                message_id=loading_msg.message_id,
                parse_mode='MarkdownV2'
            )
        except:
            pass
            
def process_steal_timers():
    current_time = time.time()
    to_remove = []
    theft_summary = {}
    for chat_id, timers in list(steal_timers.items()):
        if not is_kidnap_game_enabled(chat_id):
            continue
        for (kidnapper_id, victim_id), last_time in list(timers.items()):
            if current_time - last_time >= 3600:
                if chat_id in kidnap_bags and kidnapper_id in kidnap_bags[chat_id] and victim_id in kidnap_bags[chat_id][kidnapper_id]:
                    victim_balance = user_coins.get(chat_id, {}).get(victim_id, 0)
                    stolen = min(5, victim_balance)
                    if stolen > 0:
                        user_coins[chat_id][victim_id] -= stolen
                        user_coins[chat_id][kidnapper_id] = user_coins[chat_id].get(kidnapper_id, 0) + stolen
                        key = (chat_id, kidnapper_id)
                        theft_summary[key] = theft_summary.get(key, 0) + stolen
                        logger.info(f"[STEAL] {kidnapper_id} украл {stolen} монет у {victim_id} в чате {chat_id}")
                    steal_timers[chat_id][(kidnapper_id, victim_id)] = current_time
                else:
                    to_remove.append((chat_id, kidnapper_id, victim_id))
    for chat_id, kidnapper_id, victim_id in to_remove:
        if chat_id in steal_timers:
            steal_timers[chat_id].pop((kidnapper_id, victim_id), None)
    if to_remove:
        save_steal_timers()
    if theft_summary:
        save_coins()
        for (chat_id, kidnapper_id), total in theft_summary.items():
            display_name = "Аноним"
            if str(kidnapper_id) in user_custom_names:
                display_name = user_custom_names[str(kidnapper_id)]
            elif chat_id in chat_members_cache and kidnapper_id in chat_members_cache[chat_id]:
                user_data = chat_members_cache[chat_id][kidnapper_id]
                display_name = user_data.get("first_name") or user_data.get("name") or "Аноним"
            elif chat_id in offline_users and kidnapper_id in offline_users[chat_id]:
                if str(kidnapper_id) in user_custom_names:
                    display_name = user_custom_names[str(kidnapper_id)]
                else:
                    try:
                        user_obj = bot.get_chat_member(chat_id, kidnapper_id).user
                        display_name = user_obj.first_name or "Аноним"
                    except:
                        display_name = "Аноним"
            try:
                bot.send_message(
                    chat_id,
                    f"🪝 {display_name} украл {total} монет у своих пленников.")
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление о краже в чат {chat_id}: {e}")

@bot.message_handler(commands=['news'], func=lambda m: m.chat.type == 'private')
@error_handler
def send_news_to_all_chats(message):
    if message.from_user.id != SALRUZO_USER_ID:
        bot.reply_to(message, "❌ Эта команда доступна только разработчику\\.")
        return
    news_text = message.text.split(maxsplit=1)
    if len(news_text) < 2:
        bot.reply_to(message, "❌ Использование: /news <текст обновления>")
        return
    update_msg = news_text[1].strip()
    escaped_update = escape_markdown_v2(update_msg)
    header = "🆕 *Новое обновление\\!*"
    separator = "\n" + "\\- " * 20  # Экранируем дефисы: \-
    full_message = header + separator + "\n" + escaped_update
    success_count = 0
    error_count = 0
    all_chat_ids = set()
    for d in [kidnap_points, user_coins, chat_triggers, chat_members_cache]:
        all_chat_ids.update(d.keys())
    for chat_id in all_chat_ids:
        try:
            bot.send_message(chat_id, full_message, parse_mode="MarkdownV2")
            success_count += 1
        except Exception as e:
            logger.warning(f"Не удалось отправить новость в чат {chat_id}: {e}")
            error_count += 1
    bot.reply_to(
        message,
        f"✅ Новость отправлена в {success_count} чатов.\n"
        f"⚠️ Ошибок: {error_count}")

@bot.message_handler(commands=['casino'])
@error_handler
def play_casino(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = time.time()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in last_casino_attempt:
        last_casino_attempt[chat_id] = {}
    if chat_id not in user_coins:
        user_coins[chat_id] = {}
    if chat_id not in casino_profit_stats:
        casino_profit_stats[chat_id] = {}
    if user_id in last_casino_attempt[chat_id]:
        elapsed = current_time - last_casino_attempt[chat_id][user_id]
        if elapsed < 10800:  # 5 часов
            remaining = int((10800 - elapsed) / 60)
            bot.reply_to(message, f"⏳ Казино доступно раз в 3 часа\\. Подожди ещё {remaining} минут\\.", parse_mode='MarkdownV2')
            return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Укажи сумму ставки: `/casino 50`", parse_mode='MarkdownV2')
        return
    try:
        bet = int(args[1])
        if bet <= 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ Ставка должна быть положительным целым числом\\.", parse_mode='MarkdownV2')
        return
    balance = user_coins[chat_id].get(user_id, 0)
    if balance < bet:
        bot.reply_to(message, "❌ Недостаточно монет для ставки\\.", parse_mode='MarkdownV2')
        return
    user_coins[chat_id][user_id] -= bet
    save_coins()
    spin_msg = bot.reply_to(message, "🎰 Крутим колесо...")
    time.sleep(0.5)
    for _ in range(8):
        fake_result = random.choice(CASINO_MULTIPLIERS)
        fake_emoji = CASINO_EMOJIS[fake_result]
        try:
            bot.edit_message_text(f"🎰 Крутим... {fake_emoji}", chat_id=chat_id, message_id=spin_msg.message_id)
        except:
            pass
        time.sleep(0.4)
    result = choices(CASINO_MULTIPLIERS, weights=CASINO_WEIGHTS, k=1)[0]
    emoji = CASINO_EMOJIS[result]
    win_amount = math.ceil(bet * result)
    net_profit = win_amount - bet
    user_coins[chat_id][user_id] += win_amount
    casino_profit_stats[chat_id][user_id] = casino_profit_stats[chat_id].get(user_id, 0) + net_profit
    last_casino_attempt[chat_id][user_id] = current_time
    save_casino_data()
    save_casino_profit_stats()
    save_coins()
    display_name = get_clickable_name(chat_id, user_id, message.from_user)
    if result == 0:
        escaped_bet = escape_markdown_v2(str(bet))
        bot.edit_message_text(
            f"🎰 {display_name}, тебе не повезло\\.\\.\\. Ты проиграл\\(а\\) {escaped_bet} монет\\. {emoji}",
            chat_id=chat_id,
            message_id=spin_msg.message_id, parse_mode='MarkdownV2')
    else:
        escaped_win = escape_markdown_v2(str(int(win_amount)))
        escaped_mult = escape_markdown_v2(str(result))
        escaped_profit = escape_markdown_v2(str(int(net_profit)))
        bot.edit_message_text(
            f"🎰 {display_name}, ты выиграл\\(а\\) {escaped_win} монет \\(x{escaped_mult}\\)\\! Чистая прибыль: {escaped_profit} 💰 {emoji}",
            chat_id=chat_id,
            message_id=spin_msg.message_id,parse_mode='MarkdownV2')

@bot.message_handler(commands=['casinostat'])
@error_handler
def show_casino_stats(message):
    if not is_kidnap_game_enabled(message.chat.id):
     bot.reply_to(message, "🔒 Эта функция отключена администратором.")
     return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in casino_profit_stats or not casino_profit_stats[chat_id]:
        bot.reply_to(message, "📊 В этом чате ещё никто не играл в казино\\.", parse_mode='MarkdownV2')
        return
    sorted_players = sorted(
        casino_profit_stats[chat_id].items(),
        key=lambda x: x[1],
        reverse=True)
    lines = []
    for uid, profit in sorted_players[:10]:
        name = get_clickable_name(chat_id, uid)  # уже экранировано внутри
        sign = "+" if profit >= 0 else ""
        escaped_profit = escape_markdown_v2(f"{sign}{int(profit)}")
        lines.append(f"• {name}: {escaped_profit} монет")
    response = "🏆 *Топ игроков казино \\(чистая прибыль\\):*\n" + "\n".join(lines)
    bot.reply_to(message, response, parse_mode='MarkdownV2')

@bot.message_handler(commands=['mute'])
@error_handler
def mute_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалена команда от замученного пользователя {user_id}: {message.text}")
        except Exception as e:
            logger.warning(f"Не удалось удалить команду от замученного: {e}")
    if chat_id not in muted_users:
        muted_users[chat_id] = set()
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответь на сообщение пользователя, с которым хочешь взаимодействовать.")
        return
    target_user = message.reply_to_message.from_user
    target_id = target_user.id
    target_name = get_clickable_name(chat_id, target_id, target_user)
    if is_user_admin(chat_id, user_id):
        if is_user_admin(chat_id, target_id):
            bot.reply_to(message, "❌ Нельзя замутить администратора или создателя чата.")
            return
        if target_id in muted_users[chat_id]:
            muted_users[chat_id].discard(target_id)
            save_muted_users()
            bot.reply_to(message, f"🔊 {target_name} размучен\\(а\\) администратором\\.", parse_mode='MarkdownV2')
        else:
            muted_users[chat_id].add(target_id)
            save_muted_users()
            bot.reply_to(message, f"🔇 {target_name} замучен\\(а\\) администратором\\.", parse_mode='MarkdownV2')
        return
    if chat_id not in handcuffed_players or target_id not in handcuffed_players[chat_id]:
        bot.reply_to(message, "❌ Этот пользователь не в наручниках или не твой пленник.")
        return
    is_victim_of_user = False
    if chat_id in kidnap_bags and user_id in kidnap_bags[chat_id]:
        if target_id in kidnap_bags[chat_id][user_id]:
            is_victim_of_user = True
    if not is_victim_of_user:
        bot.reply_to(message, "❌ Ты можешь взаимодействовать только со своими пленниками в наручниках.")
        return
    if target_id in muted_users[chat_id]:
        muted_users[chat_id].discard(target_id)
        save_muted_users()
        bot.reply_to(message, f"🔊 Ты размутил\\(а\\) {target_name}\\.", parse_mode='MarkdownV2')
    else:
        muted_users[chat_id].add(target_id)
        save_muted_users()
        bot.reply_to(message, f"🔇 Ты замутил\\(а\\) {target_name}\\.", parse_mode='MarkdownV2')

@bot.message_handler(commands=['offline'])
@error_handler
def toggle_offline_mode(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in offline_users:
        offline_users[chat_id] = set()

    if user_id in offline_users[chat_id]:
        offline_users[chat_id].discard(user_id)
        status = "отключён"
    else:
        offline_users[chat_id].add(user_id)
        status = "включён"
    save_offline_users()
    bot.reply_to(message, f"✅ Режим «оффлайн» {status}.")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    for user in message.new_chat_members:
        if user.is_bot:
            continue  # Пропускаем других ботов
        try:
            bot.send_sticker(message.chat.id, WELCOME_STICKER)
            welcome_text = (
                f"👋 Привет, [{escape_markdown_v2(user.first_name)}](tg://user?id={user.id})\\!\n"
                "Я — Сомка, игровой бот с мини\\-играми, похищениями, казино и триггерами\\.\n\n"
                "🔹 Основные команды:\n"
                "• `/members` — список участников\n"
                "• `/kidnap` — похитить кого\\-то\n"
                "• `/job` — заработать монеты\n"
                "• `/shop` — купить предметы\n"
                "• `/casino` \\<ставка\\> — испытать удачу\n\n"
                "⚙️ Настройки бота:\n"
                "• `/triggersettings`\n"
                "• `/offline` — отключить упоминания от бота\n\n"
                "Удачи и веселья в чате\\! 🎮")
            bot.send_message(
                message.chat.id,
                welcome_text,parse_mode='MarkdownV2')
            logger.info(f"[WELCOME] Приветствие отправлено пользователю {user.id} в чате {message.chat.id}")
        except Exception as e:
            logger.error(f"[WELCOME] Ошибка при приветствии {user.id}: {e}")

@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(message):
    """Приветствие в ЛС с инструкцией по добавлению в чат."""
    welcome_text = (
        "👋 Привет! Я — Сомка, игровой бот с мини-играми, похищениями, казино и триггерами.\n\n"
        "❗️**Я работаю только в группах и супергруппах!**\n\n"
        "Чтобы начать:\n"
        "1. Добавь меня в беседу.\n"
        "2. Сделай меня **администратором** (иначе я не смогу приветствовать участников, удалять сообщения и т.д.).\n\n"
        "После этого в чате будут доступны все команды:\n"
        "• `/members` — список участников\n"
        "• `/kidnap` — похищать игроков\n"
        "• `/casino` — испытать удачу\n"
        "• `/shop` — покупать предметы\n"
        "• и многое другое!\n\n"
        "Удачи и веселья! 🎮")
    bot.send_message(
        message.chat.id,
        welcome_text,parse_mode='Markdown')
    logger.info(f"[START] Пользователь {message.from_user.id} запустил бота в ЛС.")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye_left_member(message):
    user = message.left_chat_member
    if user.is_bot:
        return
    try:
        bot.send_sticker(message.chat.id, GOODBYE_STICKER)
        logger.info(f"[GOODBYE] Прощальный стикер отправлен при выходе {user.id} из чата {message.chat.id}")
    except Exception as e:
        logger.error(f"[GOODBYE] Ошибка при отправке прощального стикера {user.id}: {e}")
# 🔄 Обработка обычных сообщений для триггеров
@bot.message_handler(func=lambda m: m.text and m.chat.type in ['group', 'supergroup'])
def handle_trigger_text(message):
    chat_id = message.chat.id
    if not are_triggers_enabled(chat_id):
        return
    user_id = message.from_user.id
    text = message.text.strip().lower()
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалено сообщение с триггером от замученного пользователя {user_id} в чате {chat_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение с триггером от замученного: {e}")
        return
    if chat_id in chat_triggers and text in chat_triggers[chat_id]:
        trigger_list = chat_triggers[chat_id][text]
        for trigger_data in trigger_list:
            try:
                media_type = trigger_data["type"]
                if media_type == "text":
                    bot.send_message(chat_id, trigger_data["text"])
                elif media_type == "sticker":
                    bot.send_sticker(chat_id, trigger_data["file_id"])
                elif media_type == "photo":
                    bot.send_photo(chat_id, trigger_data["file_id"])
                elif media_type == "video":
                    bot.send_video(chat_id, trigger_data["file_id"])
                elif media_type == "animation":
                    bot.send_animation(chat_id, trigger_data["file_id"])
                elif media_type == "audio":
                    bot.send_audio(chat_id, trigger_data["file_id"])
                elif media_type == "voice":
                    bot.send_voice(chat_id, trigger_data["file_id"])
                elif media_type == "document":
                    bot.send_document(chat_id, trigger_data["file_id"])
            except Exception as e:
                logger.warning(f"Не удалось отправить медиа/текст для триггера '{text}': {e}")

@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'], content_types=['sticker', 'photo', 'video', 'document', 'voice', 'audio', 'animation', 'contact', 'location', 'poll'])
def delete_muted_media_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"[MUTE] Удалено медиа-сообщение от замученного пользователя {user_id} в чате {chat_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить медиа-сообщение от замученного: {e}")

def daily_report_loop():
    """Фоновый процесс: отправляет ежедневные отчёты в 9:00, закрепляет новые и откредляет старые."""
    while True:
        try:
            now = datetime.now()
            target_hour = 9  # Час отправки (можно изменить)
            
            for chat_id, report in list(daily_reports.items()):
                target_date = datetime.strptime(report["target_date"], "%Y-%m-%d").date()
                today = now.date()
                last_sent = report.get("last_sent")
                
                # Проверяем, отправляли ли сегодня
                if last_sent == str(today):
                    continue
                
                # Проверяем время (отправляем после target_hour)
                if now.hour < target_hour:
                    continue
                
                # Проверяем, не прошла ли дата
                if today > target_date:
                    # Откреепляем последнее сообщение перед удалением
                    old_message_id = report.get("last_message_id")
                    if old_message_id:
                        try:
                            bot.unpin_chat_message(chat_id, old_message_id)
                        except Exception as e:
                            logger.warning(f"[DAILY_REPORT] Не удалось открепить сообщение при завершении: {e}")
                    
                    del daily_reports[chat_id]
                    save_daily_reports()
                    try:
                        bot.send_message(
                            chat_id, 
                            "📅 Целевая дата отчёта прошла\\. Ежедневный отчёт автоматически отключён\\.", 
                            parse_mode='MarkdownV2'
                        )
                    except Exception as e:
                        logger.warning(f"[DAILY_REPORT] Не удалось уведомить чат {chat_id} о завершении: {e}")
                    continue
                
                # Открепляем старое сообщение
                old_message_id = report.get("last_message_id")
                if old_message_id:
                    try:
                        bot.unpin_chat_message(chat_id, old_message_id)
                        logger.info(f"[DAILY_REPORT] Откреплено старое сообщение {old_message_id} в чате {chat_id}")
                    except Exception as e:
                        logger.warning(f"[DAILY_REPORT] Не удалось открепить сообщение {old_message_id}: {e}")
                
                # Считаем дни
                days_left = (target_date - today).days
                comment = report["comment"]
                formatted_date = target_date.strftime("%d.%m.%Y")
                
                if days_left == 0:
                    days_text = "🎉 Сегодня этот день!"
                elif days_left == 1:
                    days_text = "⏰ Остался 1 день!"
                else:
                    # Правильное склонение
                    if days_left % 10 == 1 and days_left % 100 != 11:
                        days_word = "день"
                    elif 2 <= days_left % 10 <= 4 and not (12 <= days_left % 100 <= 14):
                        days_word = "дня"
                    else:
                        days_word = "дней"
                    days_text = f"⏳ Осталось: {days_left} {days_word}"
                
                escaped_date = escape_markdown_v2(formatted_date)
                escaped_comment = escape_markdown_v2(comment)
                escaped_days = escape_markdown_v2(days_text)
                
                message_text = (
                    f"📆 *Ежедневный отчёт*\n\n"
                    f"📅 Дата: {escaped_date}\n"
                    f"{escaped_days}\n\n"
                    f"💬 {escaped_comment}"
                )
                
                try:
                    # Отправляем новое сообщение
                    sent_message = bot.send_message(chat_id, message_text, parse_mode='MarkdownV2')
                    
                    # Закрепляем новое сообщение
                    try:
                        bot.pin_chat_message(chat_id, sent_message.message_id, disable_notification=True)
                        logger.info(f"[DAILY_REPORT] Закреплено сообщение {sent_message.message_id} в чате {chat_id}")
                    except Exception as e:
                        logger.warning(f"[DAILY_REPORT] Не удалось закрепить сообщение: {e}")
                    
                    # Обновляем данные
                    daily_reports[chat_id]["last_sent"] = str(today)
                    daily_reports[chat_id]["last_message_id"] = sent_message.message_id
                    save_daily_reports()
                    logger.info(f"[DAILY_REPORT] Отправлен отчёт в чат {chat_id}, осталось {days_left} дней")
                    
                except Exception as e:
                    logger.warning(f"[DAILY_REPORT] Не удалось отправить отчёт в чат {chat_id}: {e}")
                    
        except Exception as e:
            logger.error(f"[DAILY_REPORT] Ошибка в цикле: {e}")

def minesweeper_event_loop():
    """Фоновый процесс: запускает события Сапёра в случайное время."""
    while True:
        try:
            current_time = time.time()
            
            # Проверяем все чаты с активностью
            all_chats = set()
            for d in [user_coins, chat_members_cache, kidnap_points]:
                all_chats.update(d.keys())
            
            for chat_id in all_chats:
                # Пропускаем если игры отключены
                if not is_kidnap_game_enabled(chat_id):
                    continue
                
                # Инициализируем данные если нет
                if chat_id not in minesweeper_data:
                    # Первое событие - через случайное время от 1 до 24 часов
                    minesweeper_data[chat_id] = {
                        "next_event_time": current_time + random.randint(3600, 86400),
                        "active_game": None,
                        "excluded_players": [],
                        "accepting": False
                    }
                    save_minesweeper_data()
                    continue
                
                # Пропускаем если есть активная игра или приём заявок
                if minesweeper_data[chat_id].get("active_game") or minesweeper_data[chat_id].get("accepting"):
                    continue
                
                # Проверяем время следующего события
                next_time = minesweeper_data[chat_id].get("next_event_time", 0)
                if current_time >= next_time:
                    logger.info(f"[MINESWEEPER] Автозапуск события в чате {chat_id}")
                    minesweeper_data[chat_id]["excluded_players"] = []
                    start_minesweeper_event(chat_id)
                    
        except Exception as e:
            logger.error(f"[MINESWEEPER] Ошибка в фоновом процессе: {e}")
        
        time.sleep(300)  # Проверяем каждые 5 минут

# 🔄 Фоновый таймер для кражи монет (запускается каждую минуту)
def background_timer_loop():
    while True:
        time.sleep(60)  # проверяем каждую минуту
        try:
            process_steal_timers()
        except Exception as e:
            logger.error(f"Ошибка в фоновом таймере кражи: {e}")# 💾 Автосохранение каждые 5 минут
def auto_save():
    while True:
        time.sleep(300)
        save_names()
        save_kidnap_data()
        save_user_cache()
        save_coins()
        save_job_cooldown()
        save_shield_data()
        save_knb_stats()
        save_triggers()
        save_trigger_access()
        save_inventory()
        save_steal_timers()
        save_muted_users()
        save_casino_data()
        save_casino_profit_stats()
        save_offline_users()
        save_features()
        save_paused_timers()
        save_execut_queue()
        save_daily_reports()
        save_minesweeper_data()
# 🚀 Запуск бота
if __name__ == '__main__':
    logger.info("=== ЗАПУСК БОТА СОМКА ===")
    load_names()
    load_kidnap_data()
    load_user_cache()
    load_shield_data()
    load_coins()
    load_job_cooldown()
    load_knb_stats()
    load_triggers()
    load_trigger_access()
    load_inventory()
    load_steal_timers()
    load_muted_users()
    load_casino_data()
    load_offline_users()
    load_features()
    load_paused_timers()
    load_execut_queue()
    load_daily_reports()
    load_minesweeper_data()
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("members", "👥 Участники чата"),
            telebot.types.BotCommand("kidnap", "🕵️ Похитить"),
            telebot.types.BotCommand("freed", "🏃‍♂️ Сбежать"),
            telebot.types.BotCommand("handcuff", "🔗 Наручники"),
            telebot.types.BotCommand("bag", "🪝 Мешок"),
            telebot.types.BotCommand("shield", "🛡️ Щит"),
            telebot.types.BotCommand("job", "💰 Заработать монеты"),
            telebot.types.BotCommand("shop", "🛒 Магазин"),
            telebot.types.BotCommand("skipkd", "⏱️ Скип кулдауна"),
            telebot.types.BotCommand("casino", "🎰 Казино"),
            telebot.types.BotCommand("knb", "🎲 Камень-Ножницы-Бумага"),
            telebot.types.BotCommand("kidnapstat", "📊 Статистика похищений"),
            telebot.types.BotCommand("knbstat", "🎲 Статистика КНБ"),
            telebot.types.BotCommand("minestat", "💣 Статистика Сапёра"),
            telebot.types.BotCommand("casinostat", "🏆 Топ казино"),
            telebot.types.BotCommand("triggersettings", "⚙️ Настройки"),
            telebot.types.BotCommand("who_somka", "❓ Напиши сомка кто (текст)"),
            telebot.types.BotCommand("mute", "🔇 Замутить своих пленников в наручниках"),
            telebot.types.BotCommand("offline", "🔇 Отключить упоминание ботом"),
        ])
        logger.info("Команды зарегистрированы!")
    except Exception as e:
        logger.error(f"Ошибка регистрации команд: {e}")
    logger.info("Удаляем вебхук...")
    bot.remove_webhook()
    time.sleep(1)
    threading.Thread(target=background_timer_loop, daemon=True).start()
    threading.Thread(target=auto_save, daemon=True).start()
    threading.Thread(target=execut_kick_loop, daemon=True).start()
    threading.Thread(target=daily_report_loop, daemon=True).start()
    threading.Thread(target=minesweeper_event_loop, daemon=True).start()
    while True:
        try:
            logger.info("Запуск polling...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except requests.exceptions.ProxyError as e:
            logger.error(f"Ошибка прокси: {e}. Переподключение через 10 секунд...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}. Переподключение через 5 секунд...")
            time.sleep(5)
