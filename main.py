import discord
import requests
import asyncio

TOKEN = "MTQ3OTYwNjA3Mzg2NTI3NzU5NA.GraT-O.WCmUW8TbgeP0XNoOxNneFMI_43uJc-gjrx0pj4"
API_KEY = "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"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

memory = {}

# ---------- STATUS ----------
async def status_loop():
    await client.wait_until_ready()

    statuses = [
        ("AI canlı yayında 🤖", discord.ActivityType.streaming),
        ("Soruları analiz ediyorum ⚡", discord.ActivityType.watching),
        ("Kullanıcılarla sohbet 💬", discord.ActivityType.playing),
        ("Premium AI mod 🔥", discord.ActivityType.listening),
    ]

    while not client.is_closed():
        for text, type_ in statuses:
            try:
                await client.change_presence(
                    status=discord.Status.online,
                    activity=discord.Activity(
                        type=type_,
                        name=text,
                        url="https://twitch.tv/discord"
                    )
                )
            except:
                pass

            await asyncio.sleep(10)

# ---------- READY ----------
@client.event
async def on_ready():
    print("BOT AKTİF")
    asyncio.create_task(status_loop())

# ---------- MESSAGE ----------
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if client.user not in message.mentions:
        return

    user_id = str(message.author.id)

    soru = message.content.replace(f"<@{client.user.id}>","").replace(f"<@!{client.user.id}>","").strip()

    if not soru:
        await message.channel.send("Bir şey yaz 🙂")
        return

    if user_id not in memory:
        memory[user_id] = [
            {
                "role": "system",
                "content": (
                    "Sen Türkçe konuşan bir Discord botsun. "
                    "Arkadaş gibi konuş, kısa ve net cevap ver, emoji kullan ama abartma."
                )
            }
        ]

    memory[user_id].append({"role": "user", "content": soru})
    memory[user_id] = memory[user_id][-15:]

    await message.channel.typing()

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": memory[user_id],
                "temperature": 0.7
            }
        )

        data = r.json()

        if "error" in data:
            await message.channel.send("API HATASI ❌")
            return

        cevap = data["choices"][0]["message"]["content"]

        memory[user_id].append({"role": "assistant", "content": cevap})

        await message.channel.send(cevap[:1900])

    except Exception as e:
        print(e)
        await message.channel.send("Hata oluştu ❌")

client.run(TOKEN)
