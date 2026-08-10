import os
import logging
import random
import string
import asyncio
from aiohttp import web
from datetime import datetime
from telethon import TelegramClient, events, Button, types
from telethon.sessions import StringSession
from database import (
    get_user, update_balance, add_account, get_available_accounts,
    get_account_by_id, mark_account_as_sold, create_order, get_order
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PORT = int(os.getenv("PORT", "10000"))

if API_ID:
    API_ID = int(API_ID)

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("API_ID, API_HASH, or BOT_TOKEN environment variable is missing!")
    exit(1)

client = TelegramClient("bot_session", API_ID, API_HASH)

# Premium Emotes IDs (For Message Body)
EMOTE_WELCOME_ID = 6260170796790980056
EMOTE_WALLET_ID = 5328098344495490329
EMOTE_SELECT_PROD_ID = 4900189275326252171
EMOTE_TG_ACC_ID = 6257974552379270658
EMOTE_TG_COMM_ID = 5472239203590888751
EMOTE_MYANMAR_ID = 6260246207826759565
EMOTE_COLOMBIA_ID = 5294111658396895748
EMOTE_US_ID = 5987769694407368809
EMOTE_CHOOSE_ID = 6159042351537853617
EMOTE_TYPE_ID = 5298877105000439431
EMOTE_PRICE_ID = 6039495948353146588
EMOTE_STOCK_ID = 5323289282499064033
EMOTE_PAGE_ID = 5197219609970758159
EMOTE_TAP_ID = 5231102735817918643
EMOTE_BEFORE_BUY_ID = 5864114012542736772
EMOTE_WARNING_ID = 5420323339723881652
EMOTE_LOCK_ID = 5296369303661067030
EMOTE_CHECK_ID = 6114069998089539705
EMOTE_AIRPLANE_ID = 5352587852880302091
EMOTE_PIN_ID = 6114141543654757519
EMOTE_MEGAPHONE_ID = 5769482310915199790
EMOTE_BACK_ID = 6257789602497572109
EMOTE_GET_OTP_ID = 6217723016529316157
EMOTE_NO_BALANCE_ID = 6010086804038884927
EMOTE_ADD_FUND_ID = 5222040745665379997

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

def get_start_text(balance):
    return (
        f"<tg-emoji document_id=\"{EMOTE_WELCOME_ID}\">🍬</tg-emoji><b>DigitalShopMm မှ ကြိုဆိုပါတယ်</b>\n\n"
        f"🛍Digital Products နှင့် Services များကို ငွေဖြည့်သွင်းပြီး လိုချင်သည့် ပစ္စည်းကို တိုက်ရိုက် လျှင်မြန်စွာဝယ်ယူနိုင်ပါသည်🛍\n\n"
        f"<tg-emoji document_id=\"{EMOTE_WALLET_ID}\">💳</tg-emoji>Wallet Balance: {balance:,} Ks"
    )

def get_reply_keyboard():
    # Telegram KeyboardButtons do not support custom emoji IDs.
    # We use standard emojis here to make it look clean and small.
    return [
        [Button.text("🛒 Products")],
        [Button.text("📦 My Orders"), Button.text("👤 Account")],
        [Button.text("👛 Balance"), Button.text("👋 Join Channel")],
        [Button.text("🌐 Language"), Button.text("🎁 Redeemcode")]
    ]

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    user = await get_user(user_id)
    balance = user.get("balance", 0)
    # resize=True makes buttons smaller and neat
    await event.respond(
        get_start_text(balance), 
        parse_mode='html', 
        buttons=client.build_reply_markup(get_reply_keyboard(), resize=True)
    )

# Handler for "Products" Reply Button
@client.on(events.NewMessage(pattern='🛒 Products'))
async def products_reply_handler(event):
    text = f"<tg-emoji document_id=\"{EMOTE_SELECT_PROD_ID}\">🖤</tg-emoji><b>Select a product:</b>"
    buttons = [
        [Button.inline("Buy Telegram Accounts", b"buy_tg_accounts", icon=EMOTE_TG_ACC_ID)],
        [Button.inline("Buy Telegram Comments", b"buy_tg_comments", icon=EMOTE_TG_COMM_ID)]
    ]
    await event.respond(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"buy_tg_accounts"))
async def tg_accounts_handler(event):
    text = f"<tg-emoji document_id=\"{EMOTE_SELECT_PROD_ID}\">🖤</tg-emoji><b>Select a product:</b>"
    buttons = [
        [Button.inline("+95 Myanmar Account . 2000ks", b"acc_country_mm", icon=EMOTE_MYANMAR_ID)],
        [Button.inline("+57 Colombia Account . 1500ks", b"acc_country_co", icon=EMOTE_COLOMBIA_ID)],
        [Button.inline("+1 UnitedState Account . 1500ks", b"acc_country_us", icon=EMOTE_US_ID)]
    ]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"acc_country_co"))
async def country_co_handler(event):
    accounts = await get_available_accounts("CO")
    stock_count = len(accounts)
    text = (
        f"<tg-emoji document_id=\"{EMOTE_CHOOSE_ID}\">➡️</tg-emoji><b>CHOOSE YOUR TELEGRAM ACCOUNT</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji document_id=\"{EMOTE_TYPE_ID}\">🏷</tg-emoji><b>Type:</b> <tg-emoji document_id=\"{EMOTE_COLOMBIA_ID}\">🇨🇴</tg-emoji> +57\n"
        f"<tg-emoji document_id=\"{EMOTE_PRODUCTS_ID}\">▪️</emoji> <b>Product:</b> Telegram Account\n"
        f"<tg-emoji document_id=\"{EMOTE_PRICE_ID}\">🔖</tg-emoji><b>Price:</b> 1,500 Ks\n"
        f"<tg-emoji document_id=\"{EMOTE_STOCK_ID}\">📦</tg-emoji> <b>In stock:</b> {stock_count} accounts\n"
        f"<tg-emoji document_id=\"{EMOTE_PAGE_ID}\">📝</tg-emoji> Page 1 of 1\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji document_id=\"{EMOTE_TAP_ID}\">👇</tg-emoji><b>Tap a phone number below to continue.</b>"
    )
    buttons = []
    for acc in accounts[:5]:
        buttons.append([Button.inline(f"{acc['phone']}", f"view_acc_{acc['_id']}", icon=EMOTE_COLOMBIA_ID)])
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(pattern=b"view_acc_(.+)"))
async def view_account_handler(event):
    acc_id = event.pattern_match.group(1).decode()
    account = await get_account_by_id(acc_id)
    if not account:
        await event.answer("Account already sold or not available!", alert=True)
        return
    text = (
        f"<tg-emoji document_id=\"{EMOTE_BEFORE_BUY_ID}\">🔥</tg-emoji><b>BEFORE YOU BUY</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji document_id=\"{EMOTE_PRODUCTS_ID}\">▪️</emoji> Telegram Colombia Account\n"
        f"<tg-emoji document_id=\"{EMOTE_TYPE_ID}\">🏷</tg-emoji> <b>New account</b>\n"
        f"<tg-emoji document_id=\"{EMOTE_COLOMBIA_ID}\">🇨🇴</tg-emoji> +57\n"
        f"<tg-emoji document_id=\"{EMOTE_PRICE_ID}\">🔖</tg-emoji> 1,500 Ks\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<tg-emoji document_id=\"{EMOTE_WARNING_ID}\">⚠️</tg-emoji> Telegram restrictions are outside our control.\n"
        f"<tg-emoji document_id=\"{EMOTE_LOCK_ID}\">🔒</tg-emoji> Request new login OTPs while the Bot remains connected.\n"
        f"<tg-emoji document_id=\"{EMOTE_CHECK_ID}\">✅</tg-emoji> Once you successfully log in, the account is under your control.\n"
        f"<tg-emoji document_id=\"{EMOTE_AIRPLANE_ID}\">✈️</tg-emoji> Change the email and 2FA immediately.\n\n"
        f"Tap “Accept & Buy” to continue.\n\n"
        f"<tg-emoji document_id=\"{EMOTE_PIN_ID}\">📌</tg-emoji> <b>PRODUCT DISCLAIMER</b>\n"
        f"Open the linked Telegram channel post and read it before confirming."
    )
    buttons = [
        [Button.url("Read Disclaimer", "https://t.me/your_channel", icon=EMOTE_MEGAPHONE_ID)],
        [Button.inline("Accept & Buy", f"buy_confirm_{acc_id}", icon=EMOTE_CHECK_ID)]
    ]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(pattern=b"buy_confirm_(.+)"))
async def buy_confirm_handler(event):
    user_id = event.sender_id
    acc_id = event.pattern_match.group(1).decode()
    account = await get_account_by_id(acc_id)
    if not account:
        await event.answer("Account not available!", alert=True)
        return
    user = await get_user(user_id)
    balance = user.get("balance", 0)
    price = account["price"]
    if balance < price:
        text = (
            f"<tg-emoji document_id=\"{EMOTE_NO_BALANCE_ID}\">🚫</tg-emoji><b>လက်ကျန်ငွေမလောက်ပါ</b>\n\n"
            f"AddFunds (ငွေဖြည့်) ပြီးမှ ဆက်လက်လုပ်ဆောင်ပါ"
        )
        buttons = [[Button.inline("AddFund", b"menu_balance", icon=EMOTE_ADD_FUND_ID)]]
        await event.edit(text, parse_mode='html', buttons=buttons)
        return
    await update_balance(user_id, -price)
    order_id = "#" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    await mark_account_as_sold(acc_id, user_id, order_id)
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "phone": account["phone"],
        "price": price,
        "session_string": account["session_string"],
        "created_at": datetime.utcnow()
    }
    await create_order(order_data)
    updated_user = await get_user(user_id)
    new_balance = updated_user.get("balance", 0)
    text = (
        f"<tg-emoji document_id=\"{EMOTE_CHECK_ID}\">✅</tg-emoji> <b>Purchase successful!</b>\n"
        f"Order: <code>{order_id}</code>\n"
        f"Product: Account\n"
        f"Total: {price:,}Ks\n"
        f"Balance: {new_balance:,} Ks\n"
        f"Phone: {account['phone']}\n"
        f"2FA: <code>12345678@Nn</code>\n\n"
        f"<blockquote>Start Telegram login with this phone, then tap Get OTP. The bot checks for about 20 seconds and delivers one code</blockquote>\n\n"
        f"<blockquote>ယခု နံပါတ်နှင့် အကောင့်ဝင်ပါ ထို့နောက် get otpနိပ်၍ otp ရယူပါ ထို့နောက်botမှပေးသည့်otp codeအားရိုက်ထည့်ပါ\n"
        f"2step pswအား 2FAတွင်ပေးထားသည်</blockquote>"
    )
    buttons = [[Button.inline("Get OTP", f"get_otp_{order_id}", icon=EMOTE_GET_OTP_ID)]]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(pattern=b"get_otp_(.+)"))
async def get_otp_handler(event):
    order_id = event.pattern_match.group(1).decode()
    order = await get_order(order_id)
    if not order:
        await event.answer("Order not found!", alert=True)
        return
    await event.answer("Checking OTP from Telegram...", alert=False)
    session_str = order["session_string"]
    phone = order["phone"]
    otp_code = None
    try:
        async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as tc:
            messages = await tc.get_messages(777000, limit=3)
            for msg in messages:
                if msg.text and any(char.isdigit() for char in msg.text):
                    otp_code = msg.text
                    break
    except Exception as e:
        logger.error(f"Error fetching OTP for {phone}: {e}")
    if not otp_code:
        text = f"OTP မရရှိသေးပါ။ Telegram တွင် OTP ပို့ထားခြင်း ရှိမရှိ စစ်ဆေးပြီး Resend ကို နှိပ်ပါ။"
    else:
        text = (
            f"OTP Code: <code>{otp_code}</code>\n"
            f"2step password: <code>12345678@Nn</code>"
        )
    buttons = [
        [Button.inline("Copy OTP", data=f"copy_otp_{order_id}")],
        [Button.inline("Copy 2FA", data=f"copy_2fa")],
        [Button.inline("Resend", f"get_otp_{order_id}", icon=EMOTE_GET_OTP_ID)]
    ]
    await event.respond(text, parse_mode='html', buttons=buttons)

@client.on(events.NewMessage(pattern='/addnumber'))
async def addnumber_handler(event):
    if not is_admin(event.sender_id):
        return
    async with client.conversation(event.sender_id, timeout=60) as conv:
        await conv.send_message("ဖုန်းနံပါတ်ကို ပို့ပေးပါ (ဥပမာ: +959752369511 သို့မဟုတ် +57xxxxxx):")
        phone_resp = await conv.get_response()
        phone = phone_resp.raw_text.strip()
        await conv.send_message("Session String ကို ပို့ပေးပါ (Text သို့မဟုတ် .txt file):")
        sess_resp = await conv.get_response()
        session_string = ""
        if sess_resp.document:
            downloaded = await sess_resp.download_media(bytes)
            session_string = downloaded.decode("utf-8").strip()
        else:
            session_string = sess_resp.raw_text.strip()
        country = "CO"
        price = 1500
        if phone.startswith("+95"):
            country = "MM"
            price = 2000
        elif phone.startswith("+1"):
            country = "US"
            price = 1500
        await add_account(country, phone, session_string, price)
        await event.respond(f"✅ Success! Added phone {phone} under country {country}.")

async def handle_ping(request):
    return web.Response(text="Bot is running successfully!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")

async def main():
    await start_web_server()
    await client.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
