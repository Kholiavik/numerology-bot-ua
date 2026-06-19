import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from zk_texts import ZK_TEXTS
from kch_texts import KCH_TEXTS
from arcane_types import get_arcane_type, get_adult_meaning
from purpose_texts import PURPOSE_TEXTS


TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не задан")

ADMIN_ID = 387254782

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_choice = {}
users = set()
calculations_count = 0


def reduce_to_22(number):
    while number > 22:
        number -= 22
    return number


def calculate_year_arcane(year):
    result = sum(int(digit) for digit in str(year))
    return reduce_to_22(result)


def calculate_comfort_zone(day, month, year):
    dt = reduce_to_22(day)
    mt = month
    gt = calculate_year_arcane(year)
    result = dt + 2 * mt + gt
    return reduce_to_22(result)


def calculate_partner_problem(day, month, year):
    dt = reduce_to_22(day)
    gt = calculate_year_arcane(year)
    result = abs(dt - gt)

    if result == 0:
        result = 22

    return result

def calculate_purpose(day, month, year):
    dt = reduce_to_22(day)
    mt = month
    gt = calculate_year_arcane(year)

    result = 6 * dt + 6 * mt + 5 * gt
    return reduce_to_22(result)

    if result == 0:
        result = 22

    return result


def parse_birth_date(text):
    text = text.strip()

    if text.isdigit() and len(text) == 8:
        text = text[:2] + "." + text[2:4] + "." + text[4:]

    birth_date = datetime.strptime(text, "%d.%m.%Y")
    return birth_date.day, birth_date.month, birth_date.year


def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Зона комфорту для дітей")
    kb.button(text="Проблеми в партнерстві")
    kb.button(text="Аркан Долі або Волі")
    kb.button(text="У якій сфері краще реалізовуватись")
    kb.button(text="Обрати інший розрахунок")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def after_result_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎤 Отримати особистий голосовий розбір — 10 €")],
            [KeyboardButton(text="👀 Подивитися приклад розбору")],
            [KeyboardButton(text="🔄 Продовжити безкоштовні розрахунки")]
        ],
        resize_keyboard=True
    )


START_TEXT = """✨ Якби ваше життя стало книгою, як би називалися її розділи? ✨

Кожна людина має свою унікальну історію: таланти, доленосні повороти, сильні сторони, приховані можливості та життєві уроки.

📖 На основі вашої дати народження я створю для вас безкоштовну нумерологічну передмову до книги вашого життя та покажу перші розділи майбутнього змісту.

Зараз для вас доступні такі розрахунки:

✅ Зона комфорту для дітей

Дізнайтеся, у якому середовищі дитина почувається щасливою, впевненою та розкриває свої найкращі якості.

✅ Проблеми в партнерстві

Допомагає побачити основні уроки та складнощі, які можуть проявлятися у стосунках.

✅ Аркан Долі або Волі

Показує, якими енергіями ви живете.

✅ У якій сфері краще реалізовуватись

Показує, де знайти ту професію чи сферу діяльності, у якій ви зможете реалізувати свої таланти та потенціал та стати успішною особистістю.

🎁 Слідкуйте за оновленнями! Щотижня Книга Життя буде доповнюватися новими розділами, що дозволять глибше зрозуміти себе, свої таланти, завдання та можливості.

Оберіть потрібний розрахунок у меню нижче та розпочніть свою подорож сторінками власної історії.

✨ Можливо, найцікавіша книга, яку ви коли-небудь читали, — це книга про вас самих.
"""


@dp.message(CommandStart())
async def start(message: Message):
    users.add(message.from_user.id)

    await message.answer(
        START_TEXT,
        reply_markup=main_menu()
    )


@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📊 Панель адміністратора\n\n"
        f"👥 Користувачів за весь час: {len(users)}\n"
        f"🧮 Розрахунків за весь час: {calculations_count}"
    )


@dp.message(F.text.in_([
    "Обрати інший розрахунок",
    "🔄 Обрати інший розрахунок",
    "🔄 Продовжити безкоштовні розрахунки"
]))
async def choose_another(message: Message):
    user_choice.pop(message.from_user.id, None)

    await message.answer(
        "Оберіть розрахунок:",
        reply_markup=main_menu()
    )


@dp.message(F.text == "👀 Подивитися приклад розбору")
async def show_example_report(message: Message):
    await message.answer(
        "✨ ПРИКЛАД ФРАГМЕНТА ОСОБИСТОГО МІНІ-РОЗБОРУ\n\n"
        "Вітаю! Я переглянула вашу дату народження та бачу, що ваш сильний потенціал пов'язаний "
        "зі спілкуванням, передачею знань та вмінням надихати інших людей.\n\n"
        "💰 У темі грошей вам найпростіше рухатися через консультації, навчання, допомогу людям "
        "або діяльність, де є живе спілкування.\n\n"
        "❤️ У стосунках важливо зберігати баланс: не розчинятися в партнері та не забувати про себе.\n\n"
        "🚀 Ваш головний ресурс — проявленість. Чим більше ви показуєте свої таланти, "
        "тим легше до вас приходять можливості.\n\n"
        "⚠️ Що може гальмувати: сумніви, страх помилки та очікування ідеального моменту.\n\n"
        "🎤 У повному міні-розборі я аналізую саме вашу дату народження та записую особисту голосову відповідь:\n"
        "— грошовий потенціал\n"
        "— призначення\n"
        "— стосунки\n"
        "— сильні сторони\n"
        "— рекомендації щодо подальшого розвитку\n\n",
        reply_markup=after_result_menu()
    )


@dp.message(F.text.in_([
    "🎤 Отримати особистий голосовий розбір — 10 €",
    "Замовити особистий нумерологічний голосовий міні-розбір за 10 €",
    "✨ Замовити нумерологічний голосовий міні-розбір за 10 €"
]))
async def order_personal_report(message: Message):
    await message.answer(
        "✨ Заявку прийнято.\n\n"
        "Я отримала сповіщення та незабаром зв'яжуся з вами для оформлення особистого голосового міні-розбору."
    )

    await bot.send_message(
        ADMIN_ID,
        "🔔 Нова заявка на особистий голосовий міні-розбір за 10 €\n\n"
        f"Ім'я: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username}\n"
        f"Telegram ID: {message.from_user.id}"
    )

@dp.message(F.text.in_([
    "Зона комфорту для дітей",
    "Проблеми в партнерстві",
    "Аркан Долі або Волі",
    "У якій сфері краще реалізовуватись"
]))
async def choose_calculation(message: Message):
    user_choice[message.from_user.id] = message.text

    await message.answer(
        "Ви обрали розрахунок:\n"
        f"«{message.text}»\n\n"
        "Введіть дату народження, щоб продовжити:\n"
        "Наприклад: 01.01.1970 або 01011970\n\n"
        "Або натисніть «Обрати інший розрахунок»."
    )


@dp.message(F.text)
async def handle_date(message: Message):
    global calculations_count

    users.add(message.from_user.id)
    choice = user_choice.get(message.from_user.id)

    if not choice: 
        await message.answer( 
            "Спочатку оберіть розрахунок:", 
            reply_markup=main_menu() 
        )
        return

    try:
        day, month, year = parse_birth_date(message.text)
    except ValueError:
        await message.answer(
            "Помилка. Введіть дату правильно:\n"
            "01.01.1970 або 01011970"
        )
        return

    if choice == "Зона комфорту для дітей":
        result = calculate_comfort_zone(day, month, year)
        text = ZK_TEXTS.get(result, "Для цього аркану поки нема тлумачення.")

        await message.answer(
            f"Зона комфорту для дітей = {result}\n\n"
            f"{text}"
        )

    elif choice == "Проблеми в партнерстві":
        result = calculate_partner_problem(day, month, year)
        text = KCH_TEXTS.get(result, "Для цього аркану поки нема тлумачення.")

        await message.answer(
            f"Проблеми в партнерстві = {result}\n\n"
            f"{text}"
        )

    elif choice == "Аркан Долі або Волі":
        zk = calculate_comfort_zone(day, month, year)
        arcane_type = get_arcane_type(zk)
        meaning = get_adult_meaning(arcane_type)

        await message.answer(
            f"ЗК = {zk}\n"
            f"Тип: {arcane_type}\n\n"
            f"{meaning}"
        )

    elif choice == "У якій сфері краще реалізовуватись":
        result = calculate_purpose(day, month, year)
        text = PURPOSE_TEXTS.get(result, "Для цього аркану поки нема тлумачення.")

        await message.answer(
            f"У якій сфері краще реалізовуватись = {result}\n\n"
            f"{text}"
        )

    else:
        await message.answer("Цей розрахунок додамо наступним кроком.")

    calculations_count += 1
    user_choice.pop(message.from_user.id, None)

    await message.answer(
        "✨ Безкоштовний розрахунок показує лише маленький фрагмент вашої карти.\n\n"
        "В особистому голосовому міні-розборі я аналізую дату народження значно глибше:\n\n"
        "💰 грошовий потенціал\n"
        "🚀 призначення та самореалізацію\n"
        "🌟 сильні сторони та внутрішні ресурси\n\n"
        "Ви можете замовити особистий розбір або продовжити безкоштовні розрахунки.",
        reply_markup=after_result_menu()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
