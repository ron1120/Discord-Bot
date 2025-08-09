# bot.py
import os
import subprocess
import discord
from dotenv import load_dotenv

# --- load secrets from .env ---
# .env must contain:
#   DISCORD_TOKEN=your_bot_token
#   CHANNEL_ID=1377709832085180428
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("DISCORD_TOKEN missing in .env")
try:
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
except ValueError:
    raise SystemExit("CHANNEL_ID in .env must be an integer")

# --- config ---
ALLOWED_USERS = set()   # optional: put Discord user IDs allowed to control the device
ADB = "adb"             # or full path, e.g. r"C:\platform-tools\adb.exe"

# --- helpers ---
def run(cmd: str):
    """Run shell cmd; return (returncode, combined_output)."""
    proc = subprocess.run(
        cmd, shell=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return proc.returncode, proc.stdout.strip()

def tap(x, y):
    return run(f'{ADB} shell input tap {int(x)} {int(y)}')

def swipe(x1, y1, x2, y2, ms=300):
    return run(f'{ADB} shell input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(ms)}')

KEYS = {"home": 3, "back": 4, "recents": 187}
def key(name):
    code = KEYS.get(name.lower())
    if code is None:
        return 1, f"Unknown key: {name}. Try one of: {', '.join(KEYS)}"
    return run(f"{ADB} shell input keyevent {code}")

def type_text(text):
    safe = text.replace(" ", "%s")
    return run(f'{ADB} shell input text "{safe}"')

def devices():
    return run(f"{ADB} devices")

# --- discord client ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def authorized(msg: discord.Message) -> bool:
    if CHANNEL_ID and msg.channel.id != CHANNEL_ID:
        return False
    if ALLOWED_USERS and msg.author.id not in ALLOWED_USERS:
        return False
    return True

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ok)")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if not authorized(message):
        return

    content = message.content.strip()

    try:
        # quick single-word commands
        if content == "!home":
            rc, out = key("home")
            await message.reply("✅ Went to Home screen." if rc == 0 else f"❌ Failed.\n```bash\n{out}\n```")
            return
        if content == "!back":
            rc, out = key("back")
            await message.reply("✅ Back." if rc == 0 else f"❌ Failed.\n```bash\n{out}\n```")
            return
        if content == "!recents":
            rc, out = key("recents")
            await message.reply("✅ Recents opened." if rc == 0 else f"❌ Failed.\n```bash\n{out}\n```")
            return

        # parameterized commands
        if content.startswith("!tap "):
            _, x, y = content.split(maxsplit=2)
            rc, out = tap(x, y)

        elif content.startswith("!swipe "):
            parts = content.split()
            if len(parts) not in (5, 6):
                await message.reply("Usage: `!swipe x1 y1 x2 y2 [ms]`")
                return
            x1, y1, x2, y2 = parts[1:5]
            ms = parts[5] if len(parts) == 6 else 300
            rc, out = swipe(x1, y1, x2, y2, ms)

        elif content.startswith("!key "):
            _, name = content.split(maxsplit=1)
            rc, out = key(name)

        elif content.startswith("!type "):
            text = content[len("!type "):]
            rc, out = type_text(text)

        elif content.strip() == "!adb devices":
            rc, out = devices()

        else:
            return  # ignore everything else

        # generic reply
        if not out:
            out = "(no output)"
        if len(out) > 1800:
            out = out[:1800] + "\n...[truncated]"
        await message.reply(f"rc={rc}\n```bash\n{out}\n```")

    except Exception as e:
        await message.reply(f"Error: `{e}`")

client.run(TOKEN)
