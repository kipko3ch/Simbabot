from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import Database
from games import Game
from datetime import datetime, timedelta
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("mining_app", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = Database()

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Check if the user was referred
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        referred_by = await db.get_user_by_referral_code(referral_code)
        if referred_by and referred_by != user_id:
            await db.add_user(user_id, username, referred_by)
            await db.update_currency(referred_by, 10)  # Bonus for referrer
            await db.update_currency(user_id, 5)  # Bonus for new user
            await client.send_message(referred_by, f"🎉 You earned 10 coins for referring a new user!")
    else:
        await db.add_user(user_id, username)
    
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("💰 Mine"), KeyboardButton("🎮 Games")],
        [KeyboardButton("👥 Refer"), KeyboardButton("💼 Balance")],
        [KeyboardButton("🏆 Leaderboard")]
    ], resize_keyboard=True)
    
    await message.reply("Welcome to the Crypto Mining Bot! Choose an action:", reply_markup=keyboard)

@app.on_message(filters.regex("^💰 Mine$"))
async def mine(client, message):
    user_id = message.from_user.id
    now = datetime.now()
    
    last_mine = await db.get_last_mine(user_id)
    if last_mine and now - last_mine < timedelta(hours=1):
        time_left = timedelta(hours=1) - (now - last_mine)
        await message.reply(f"⏳ You can mine again in {time_left.seconds // 60} minutes.")
        return

    reward = random.randint(5, 15)
    await db.update_currency(user_id, reward)
    await db.set_last_mine(user_id, now)
    
    current_balance = await db.get_user_currency(user_id)
    await message.reply(f"⛏ You've mined {reward} coins!\n💰 Current balance: {current_balance} coins")

@app.on_message(filters.regex("^🎮 Games$"))
async def games_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗿📄✂️ Rock Paper Scissors", callback_data="game_rps")],
        [InlineKeyboardButton("🪙 Coin Flip", callback_data="game_coin_flip")],
        [InlineKeyboardButton("🎲 Dice Roll", callback_data="game_dice_roll")]
    ])
    await message.reply("Choose a game to play:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^game_"))
async def handle_game(client, callback_query):
    game_type = callback_query.data.split("_")[1]
    
    if game_type == "rps":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗿 Rock", callback_data="play_rps_rock"),
             InlineKeyboardButton("📄 Paper", callback_data="play_rps_paper"),
             InlineKeyboardButton("✂️ Scissors", callback_data="play_rps_scissors")]
        ])
        await callback_query.message.reply("Choose your move:", reply_markup=keyboard)
    elif game_type == "coin_flip":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Heads", callback_data="play_coin_flip_heads"),
             InlineKeyboardButton("Tails", callback_data="play_coin_flip_tails")]
        ])
        await callback_query.message.reply("Choose heads or tails:", reply_markup=keyboard)
    elif game_type == "dice_roll":
        result, roll, reward = await Game.play("dice_roll")
        await handle_game_result(callback_query.message, callback_query.from_user.id, "Dice Roll", result, roll, reward)

@app.on_callback_query(filters.regex("^play_"))
async def play_game(client, callback_query):
    game_type, user_choice = callback_query.data.split("_")[1:]
    result, bot_choice, reward = await Game.play(game_type, user_choice)
    await handle_game_result(callback_query.message, callback_query.from_user.id, game_type.upper(), result, bot_choice, reward)

async def handle_game_result(message, user_id, game_name, result, bot_choice, reward):
    await db.add_game_result(user_id, game_name, result, reward)
    if result == "win":
        await db.update_currency(user_id, reward)
        response = f"🎉 You won! Bot chose {bot_choice}. You've earned {reward} coins."
    elif result == "lose":
        response = f"😔 You lost! Bot chose {bot_choice}. Better luck next time!"
    else:
        response = f"🤝 It's a draw! Bot also chose {bot_choice}."
    
    current_balance = await db.get_user_currency(user_id)
    await message.reply(f"{response}\n💰 Current balance: {current_balance} coins")

@app.on_message(filters.regex("^👥 Refer$"))
async def refer(client, message):
    user_id = message.from_user.id
    referral_code, referrals = await db.get_referral_info(user_id)
    await message.reply(f"🔗 Your referral code is: `{referral_code}`\n"
                        f"You have referred {referrals} users.\n"
                        f"Share this code with your friends to earn bonus coins!\n"
                        f"They should send /start {referral_code} to the bot.")

@app.on_message(filters.regex("^💼 Balance$"))
async def check_balance(client, message):
    user_id = message.from_user.id
    current_balance = await db.get_user_currency(user_id)
    await message.reply(f"💰 Your current balance: {current_balance} coins")

@app.on_message(filters.regex("^🏆 Leaderboard$"))
async def show_leaderboard(client, message):
    leaderboard = await db.get_leaderboard()
    response = "🏆 Top 10 Miners:\n\n"
    for i, (username, balance) in enumerate(leaderboard, 1):
        response += f"{i}. {username}: {balance} coins\n"
    await message.reply(response)

async def send_daily_reminder():
    while True:
        # Implement logic to send daily reminders to users
        # This is a placeholder and should be implemented based on your specific requirements
        await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours

async def main():
    await db.init_db()
    await app.start()
    await send_daily_reminder()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())