import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon import events  # <- Добавьте эту строку
from telethon.tl.types import PeerUser, PeerChannel, PeerChat
from telethon.tl.functions.messages import DeleteHistoryRequest

class TelegramTools:
    def __init__(self):
        self.client = None
        self.config_file = 'tg_tools_config.json'
        self.session_file = 'session_name.session'
        self.title_art = r"""
   _______________                        |*\_/*|________
  |  ___________  |     .-.     .-.      ||_/-\_|______  |
  | |           | |    .****. .****.     | |           | |
  | |   0   0   | |    .*****.*****.     | |   0   0   | |
  | |     -     | |     .*********.      | |     -     | |
  | |   \___/   | |      .*******.       | |   \___/   | |
  | |___     ___| |       .*****.        | |___________| |
  |_____|\_/|_____|        .***.         |_______________|
    _|__|/ \|_|_.............*.............._|________|_
   / ********** \                          / ********** \
 /  ************  \                      /  ************  \       
 """

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, data):
        with open(self.config_file, 'w') as f:
            json.dump(data, f)

    async def init_client(self):
        print("\n" + self.title_art)
        config = self.load_config()

        if 'api_id' in config and 'api_hash' in config and 'phone' in config:
            use_saved = input("Найдены сохраненные данные. Использовать их? (y/n): ").lower()
            if use_saved == 'y':
                api_id = config['api_id']
                api_hash = config['api_hash']
                phone = config['phone']
            else:
                api_id, api_hash, phone = self.get_auth_data()
        else:
            api_id, api_hash, phone = self.get_auth_data()

        self.client = TelegramClient('session_name', int(api_id), api_hash)
        await self.client.start(phone)
        print("✓ Успешное подключение к Telegram")

        # Сохраняем данные
        config.update({'api_id': api_id, 'api_hash': api_hash, 'phone': phone})
        self.save_config(config)

    def get_auth_data(self):
        api_id = input("Введите ваш API ID: ")
        api_hash = input("Введите ваш API Hash: ")
        phone = input("Введите ваш номер телефона (с кодом страны): ")
        return api_id, api_hash, phone

    async def cleanup_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            print("✓ Файл сессии удален")
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            print("✓ Конфигурация удалена")
        else:
            print("Файлы сессии/конфигурации не найдены")

    async def clean_chat(self):
        print("\n" + "=" * 40)
        print("Очистка переписки")

        search_method = input("Искать чат по:\n1. ID\n2. Имени\nВыберите (1/2): ")

        if search_method == "1":
            chat_id = input("Введите ID чата: ")
            try:
                entity = await self.client.get_entity(int(chat_id))
            except Exception as e:
                print(f"Ошибка: {e}")
                return
        else:
            chat_name = input("Введите имя чата: ")
            entity = None
            async for dialog in self.client.iter_dialogs():
                if chat_name.lower() in dialog.name.lower():
                    entity = dialog.entity
                    break

            if not entity:
                print("Чат не найден!")
                return

        minutes = int(input("За сколько минут удалить (0=все): "))
        delete_only_my = input("Удалять только свои сообщения? (y/n): ").lower() == 'y'
        delete_media = input("Удалять медиа (фото/видео/файлы)? (y/n): ").lower() == 'y'

        if minutes > 0:
            time_threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        else:
            time_threshold = None

        deleted_count = 0
        async for message in self.client.iter_messages(entity):
            if time_threshold and message.date < time_threshold:
                break

            try:
                if message.media and not delete_media:
                    continue

                if delete_only_my and message.out:
                    await message.delete()
                    deleted_count += 1
                    print(f"Удалено сообщение от {message.date}")
                elif not delete_only_my:
                    if isinstance(entity, PeerUser) or message.out:
                        await message.delete()
                        deleted_count += 1
                        print(f"Удалено сообщение от {message.date}")
            except Exception as e:
                print(f"Ошибка при удалении: {e}")

        print(f"\n✓ Удалено {deleted_count} сообщений")

    async def mass_send_messages(self):
        print("\n" + "=" * 40)
        print("Массовая рассылка сообщений")

        chats = []
        while True:
            chat = input("Введите ID или имя чата (или 'готово' для завершения): ")
            if chat.lower() == 'готово':
                break
            try:
                entity = await self.client.get_entity(int(chat)) if chat.isdigit() else None
            except:
                entity = None

            if not entity:
                async for dialog in self.client.iter_dialogs():
                    if chat.lower() in dialog.name.lower():
                        entity = dialog.entity
                        break

            if entity:
                chats.append(entity)
                print(f"Добавлен чат: {entity.title if hasattr(entity, 'title') else entity.first_name}")
            else:
                print("Чат не найден!")

        if not chats:
            print("Не выбрано ни одного чата!")
            return

        message = input("Введите сообщение для рассылки: ")
        send_media = input("Добавить медиа (фото/видео/файл)? (y/n): ").lower() == 'y'
        media_path = None
        if send_media:
            media_path = input("Укажите путь к файлу: ")
            if not os.path.exists(media_path):
                print("Файл не найден!")
                return

        confirm = input(f"Отправить сообщение в {len(chats)} чатов? (y/n): ").lower()
        if confirm != 'y':
            return

        success = 0
        for chat in chats:
            try:
                if send_media and media_path:
                    await self.client.send_file(chat, media_path, caption=message)
                else:
                    await self.client.send_message(chat, message)
                print(f"✓ Отправлено в {chat.title if hasattr(entity, 'title') else chat.first_name}")
                success += 1
            except Exception as e:
                print(f"Ошибка отправки в {chat.title if hasattr(entity, 'title') else chat.first_name}: {e}")

        print(f"\n✓ Сообщение отправлено в {success} из {len(chats)} чатов")

    async def setup_auto_reply(self):
        print("\n" + "=" * 40)
        print("Настройка автоответчика")

        target = input("Введите ID или имя чата (или 'всем' для всех чатов): ")
        reply_message = input("Введите сообщение для ответа: ")
        reply_media = input("Добавить медиа к ответу? (y/n): ").lower() == 'y'
        media_path = None
        if reply_media:
            media_path = input("Укажите путь к файлу: ")
            if not os.path.exists(media_path):
                print("Файл не найден!")
                return

        keywords = [k.strip() for k in
                    input("Ключевые слова (через запятую, оставьте пустым для ответа на все): ").split(',') if
                    k.strip()]

        # Настройки антиспама
        print("\nНастройки антиспама:")
        print("1. Фиксированная задержка (например, 10 минут)")
        print("2. Прогрессивная задержка (10мин, 30мин, 1ч, 3ч, 6ч, 12ч, 24ч)")
        print("3. Случайная задержка (от 5 до 30 минут)")
        delay_type = input("Выберите тип задержки (1-3): ")

        # Инициализация словаря для хранения времени последнего ответа
        self.last_reply_time = {}

        @self.client.on(events.NewMessage(chats=None if target.lower() == 'всем' else entity))
        async def handler(event):
            chat_id = event.chat_id
            current_time = datetime.now(timezone.utc)

            # Проверяем, нужно ли отвечать по ключевым словам
            should_reply = not keywords or any(k.lower() in event.message.text.lower() for k in keywords)

            if should_reply:
                # Определяем задержку
                if delay_type == '1':
                    # Фиксированная задержка 10 минут
                    delay = timedelta(minutes=10)
                    can_reply = chat_id not in self.last_reply_time or \
                                (current_time - self.last_reply_time[chat_id]) >= delay
                elif delay_type == '2':
                    # Прогрессивная задержка
                    delays = [10, 30, 60, 180, 360, 720, 1440]  # в минутах
                    reply_count = self.last_reply_time.get(chat_id, {}).get('count', 0)
                    delay_index = min(reply_count, len(delays) - 1)
                    delay = timedelta(minutes=delays[delay_index])
                    can_reply = chat_id not in self.last_reply_time or \
                                (current_time - self.last_reply_time[chat_id]['time']) >= delay
                else:
                    # Случайная задержка от 5 до 30 минут
                    delay = timedelta(minutes=random.randint(5, 30))
                    can_reply = chat_id not in self.last_reply_time or \
                                (current_time - self.last_reply_time[chat_id]) >= delay

                if can_reply:
                    try:
                        if reply_media and media_path:
                            await event.reply(reply_message, file=media_path)
                        else:
                            await event.reply(reply_message)

                        # Обновляем время последнего ответа
                        if delay_type == '2':
                            self.last_reply_time[chat_id] = {
                                'time': current_time,
                                'count': self.last_reply_time.get(chat_id, {}).get('count', 0) + 1
                            }
                        else:
                            self.last_reply_time[chat_id] = current_time

                        print(
                            f"\n[{current_time.strftime('%H:%M:%S')}] Ответ отправлен в {event.chat.title if hasattr(event.chat, 'title') else 'личный чат'}")
                    except Exception as e:
                        print(f"Ошибка при отправке ответа: {e}")
                else:
                    remaining_time = (self.last_reply_time[chat_id] + delay - current_time).total_seconds() / 60
                    print(f"\nПропуск сообщения. Можно ответить через {remaining_time:.1f} минут")

        print("\nАвтоответчик запущен!")
        print("Нажмите Ctrl+C для остановки")
        await self.client.run_until_disconnected()

    async def run(self):
        await self.init_client()
        while True:
            print("\n" + "=" * 40)
            print("1. Очистить переписку (включая медиа)")
            print("2. Настроить автоответчик")
            print("3. Массовая рассылка сообщений")
            print("4. Удалить данные авторизации")
            print("5. Выход")
            choice = input("Выберите действие: ")

            if choice == "1":
                await self.clean_chat()
            elif choice == "2":
                await self.setup_auto_reply()
            elif choice == "3":
                await self.mass_send_messages()
            elif choice == "4":
                await self.cleanup_session()
            elif choice == "5":
                await self.client.disconnect()
                print("Сессия завершена")
                break
            else:
                print("Неверный ввод, попробуйте снова")


if __name__ == "__main__":
    tools = TelegramTools()
    try:
        asyncio.run(tools.run())
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
    except Exception as e:
        print(f"Произошла ошибка: {e}")