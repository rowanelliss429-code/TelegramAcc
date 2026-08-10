import os
import logging
import random
import string
import asyncio
from aiohttp import web
from datetime import datetime
from telethon import TelegramClient, events, Button
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

# Initialize client as None, will be started in main()
client = TelegramClient("bot_session", API_ID, API_HASH)

# Premium Emotes definitions
EMOTE_WALLET = "<emoji id=5328098344495490329>💳</emoji>"
EMOTE_WELCOME = "🍬"
EMOTE_PRODUCTS = "<emoji id=5359805631320571519>▪️</emoji>"
EMOTE_MY_ORDERS = "<emoji id=5258011929993026890>📦</emoji>"
EMOTE_ACCOUNT = "<emoji id=5323289282499064033>👤</emoji>"
EMOTE_BALANCE = "<emoji id=5404359483155570991>👛</emoji>"
EMOTE_JOIN_CHANNEL = "<emoji id=6113870986484913105>👋</emoji>"
EMOTE_LANGUAGE = "<emoji id=5879585266426973039>🌐</emoji>"
EMOTE_REDEEM = "<emoji id=5359664288241829619>🎁</emoji>"
EMOTE_SELECT_PROD = "<emoji id=4900189275326252171>🖤</emoji>"
EMOTE_TG_ACC = "<emoji id=6257974552379270658>📱</emoji>"
EMOTE_TG_COMM = "<emoji id=5472239203590888751>📩</emoji>"
EMOTE_MYANMAR = "<emoji id=6260246207826759565>🇲🇲</emoji>"
EMOTE_COLOMBIA = "<emoji id=5294111658396895748>🇨🇴</emoji>"
EMOTE_US = "<emoji id=5987769694407368809>🇺🇸</emoji>"
EMOTE_CHOOSE = "<emoji id=6159042351537853617>➡️</emoji>"
EMOTE_TYPE = "<emoji id=5298877105000439431>🏷</emoji>"
EMOTE_PRICE = "<emoji id=6039495948353146588>🔖</emoji>"
EMOTE_STOCK = "<emoji id=5323289282499064033>📦</emoji>"
EMOTE_PAGE = "<emoji id=5197219609970758159>📝</emoji>"
EMOTE_TAP = "<emoji id=5231102735817918643>👇</emoji>"
EMOTE_BEFORE_BUY = "<emoji id=5864114012542736772>🔥</emoji>"
EMOTE_WARNING = "<emoji id=5420323339723881652>⚠️</emoji>"
EMOTE_LOCK = "<emoji id=5296369303661067030>🔒</emoji>"
EMOTE_CHECK = "<emoji id=6114069998089539705>✅</emoji>"
EMOTE_AIRPLANE = "<emoji id=5352587852880302091>✈️</emoji>"
EMOTE_PIN = "<emoji id=6114141543654757519>📌</emoji>"
EMOTE_MEGAPHONE = "<emoji id=5769482310915199790>📢</emoji>"
EMOTE_BACK = "<emoji id=6257789602497572109>⬅️</emoji>"
EMOTE_GET_OTP = "<emoji id=6217723016529316157>💰</emoji>"
EMOTE_NO_BALANCE = "<emoji id=6010086804038884927>🚫</emoji>"
EMOTE_ADD_FUND = "<emoji id=5222040745665379997>💚</emoji>"

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

# Handlers
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    user = await get_user(user_id)
    balance = user.get("balance", 0)
    text = (
        f"{EMOTE_WELCOME}<b>DigitalShopMm မှ ကြိုဆိုပါတယ်</b>\n\n"
        f"🛍Digital Products နှင့် Services များကို ငွေဖြည့်သွင်းပြီး လိုချင်သည့် ပစ္စည်းကို တိုက်ရိုက် လျှင်မြန်စွာဝယ်ယူနိုင်ပါသည်🛍\n\n"
        f"{EMOTE_WALLET}Wallet Balance: {balance:,} Ks"
    )
    buttons = [
        [Button.inline(f"{EMOTE_PRODUCTS} Products", b"menu_products"), Button.inline(f"{EMOTE_MY_ORDERS} My Orders", b"menu_orders")],
        [Button.inline(f"{EMOTE_BALANCE} Balance", b"menu_balance"), Button.inline(f"{EMOTE_ACCOUNT} Account", b"menu_account")],
        [Button.inline(f"{EMOTE_JOIN_CHANNEL} Join Channel", url="https://t.me/your_channel"), Button.inline(f"{EMOTE_LANGUAGE} Language", b"menu_language")],
        [Button.inline(f"{EMOTE_REDEEM} Redeemcode", b"menu_redeem")]
    ]
    await event.respond(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"menu_products"))
async def products_handler(event):
    text = f"{EMOTE_SELECT_PROD}<b>Select a product:</b>"
    buttons = [
        [Button.inline(f"{EMOTE_TG_ACC} Buy Telegram Accounts", b"buy_tg_accounts")],
        [Button.inline(f"{EMOTE_TG_COMM} Buy Telegram Comments", b"buy_tg_comments")],
        [Button.inline(f"{EMOTE_BACK} Back", b"menu_start")]
    ]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"buy_tg_accounts"))
async def tg_accounts_handler(event):
    text = f"{EMOTE_SELECT_PROD}<b>Select a product:</b>"
    buttons = [
        [Button.inline(f"{EMOTE_MYANMAR} +95 Myanmar Account . 2000ks", b"acc_country_mm")],
        [Button.inline(f"{EMOTE_COLOMBIA} +57 Colombia Account . 1500ks", b"acc_country_co")],
        [Button.inline(f"{EMOTE_US} +1 UnitedState Account . 1500ks", b"acc_country_us")],
        [Button.inline(f"{EMOTE_BACK} Back", b"menu_products")]
    ]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"menu_start"))
async def back_to_start(event):
    user_id = event.sender_id
    user = await get_user(user_id)
    balance = user.get("balance", 0)
    text = (
        f"{EMOTE_WELCOME}<b>DigitalShopMm မှ ကြိုဆိုပါတယ်</b>\n\n"
        f"🛍Digital Products နှင့် Services များကို ငွေဖြည့်သွင်းပြီး လိုချင်သည့် ပစ္စည်းကို တိုက်ရိုက် လျှင်မြန်စွာဝယ်ယူနိုင်ပါသည်🛍\n\n"
        f"{EMOTE_WALLET}Wallet Balance: {balance:,} Ks"
    )
    buttons = [
        [Button.inline(f"{EMOTE_PRODUCTS} Products", b"menu_products"), Button.inline(f"{EMOTE_MY_ORDERS} My Orders", b"menu_orders")],
        [Button.inline(f"{EMOTE_BALANCE} Balance", b"menu_balance"), Button.inline(f"{EMOTE_ACCOUNT} Account", b"menu_account")],
        [Button.inline(f"{EMOTE_JOIN_CHANNEL} Join Channel", url="https://t.me/your_channel"), Button.inline(f"{EMOTE_LANGUAGE} Language", b"menu_language")],
        [Button.inline(f"{EMOTE_REDEEM} Redeemcode", b"menu_redeem")]
    ]
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(data=b"acc_country_co"))
async def country_co_handler(event):
    accounts = await get_available_accounts("CO")
    stock_count = len(accounts)
    text = (
        f"{EMOTE_CHOOSE}<b>CHOOSE YOUR TELEGRAM ACCOUNT</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{EMOTE_TYPE}<b>Type:</b> {EMOTE_COLOMBIA} +57\n"
        f"{EMOTE_PRODUCTS} <b>Product:</b> Telegram Account\n"
        f"{EMOTE_PRICE}<b>Price:</b> 1,500 Ks\n"
        f"{EMOTE_STOCK} <b>In stock:</b> {stock_count} accounts\n"
        f"{EMOTE_PAGE} Page 1 of 1\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{EMOTE_TAP}<b>Tap a phone number below to continue.</b>"
    )
    buttons = []
    for acc in accounts[:5]:
        buttons.append([Button.inline(f"{EMOTE_COLOMBIA} {acc['phone']}", f"view_acc_{acc['_id']}")])
    buttons.append([Button.inline(f"{EMOTE_BACK} Back", b"buy_tg_accounts")])
    await event.edit(text, parse_mode='html', buttons=buttons)

@client.on(events.CallbackQuery(pattern=b"view_acc_(.+)"))
async def view_account_handler(event):
    acc_id = event.pattern_match.group(1).decode()
    account = await get_account_by_id(acc_id)
    if not account:
        await event.answer("Account already sold or not available!", alert=True)
        return
    text = (
        f"{EMOTE_BEFORE_BUY}<b>BEFORE YOU BUY</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{EMOTE_PRODUCTS} Telegram Colombia Account\n"
        f"{EMOTE_TYPE} <b>New account</b>\n"
        f"{EMOTE_COLOMBIA} +57\n"
        f"{EMOTE_PRICE} 1,500 Ks\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{EMOTE_WARNING} Telegram restrictions are outside our control.\n"
        f"{EMOTE_LOCK} Request new login OTPs while the Bot remains connected.\n"
        f"{EMOTE_CHECK} Once you successfully log in, the account is under your control.\n"
        f"{EMOTE_AIRPLANE} Change the email and 2FA immediately.\n\n"
        f"Tap “Accept & Buy” to continue.\n\n"
        f"{EMOTE_PIN} <b>PRODUCT DISCLAIMER</b>\n"
        f"Open the linked Telegram channel post and read it before confirming."
    )
    buttons = [
        [Button.inline(f"{EMOTE_MEGAPHONE} Read Disclaimer", url="https://t.me/your_channel")],
        [Button.inline(f"{EMOTE_CHECK} Accept & Buy", f"buy_confirm_{acc_id}")],
        [Button.inline(f"{EMOTE_BACK} Back", b"acc_country_co")]
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
            f"{EMOTE_NO_BALANCE}<b>လက်ကျန်ငွေမလောက်ပါ</b>\n\n"
            f"AddFunds (ငွေဖြည့်) ပြီးမှ ဆက်လက်လုပ်ဆောင်ပါ"
        )
        buttons = [[Button.inline(f"{EMOTE_ADD_FUND} AddFund {EMOTE_ADD_FUND}", b"menu_balance")]]
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
        f"{EMOTE_CHECK} <b>Purchase successful!</b>\n"
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
    buttons = [
        [Button.inline(f"{EMOTE_GET_OTP} Get OTP {EMOTE_GET_OTP}", f"get_otp_{order_id}")],
        [Button.inline(f"{EMOTE_BACK} Main Menu", b"menu_start")]
    ]
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
        [Button.inline(f"📋 Copy OTP", data=f"copy_otp_{order_id}")],
        [Button.inline(f"📋 Copy 2FA", data=f"copy_2fa")],
        [Button.inline(f"🔄 Resend", f"get_otp_{order_id}")],
        [Button.inline(f"{EMOTE_BACK} Main Menu", b"menu_start")]
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

# Aiohttp web server for Render health check
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
    # Start web server
    await start_web_server()
    # Start Telegram client within the same loop
    await client.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
