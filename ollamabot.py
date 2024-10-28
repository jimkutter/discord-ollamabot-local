import os
import sys
import discord
import ollama
import click
import base64
import pathlib
from collections import deque

from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()

OLLAMABOT_DISCORD_TOKEN = os.environ.get("OLLAMABOT_DISCORD_TOKEN")
OLLAMABOT_MULTIMODAL = os.environ.get("OLLAMABOT_MULTIMODAL")
OLLAMABOT_MAX_HISTORY_LEN = os.environ.get("OLLAMABOT_MAX_HISTORY_LEN")

assert OLLAMABOT_DISCORD_TOKEN, "OLLAMABOT_DISCORD_TOKEN not set!"
assert OLLAMABOT_MULTIMODAL, "OLLAMABOT_MULTIMODAL not set!"
assert OLLAMABOT_MAX_HISTORY_LEN, "OLLAMABOT_MAX_HISTORY_LEN not set!"

conversation_histories = dict()


@click.command()
@click.option("--model-file", type=click.File())
def its_alive(model_file):
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    if model_file is None:
        model_file = (pathlib.Path(__file__).parent / "Modelfile.example").open()

    print(f"Reading from {model_file}")
    modelfile = model_file.read()

    for resp in ollama.create(model="custom", modelfile=modelfile, stream=True):
        print(resp)

    is_multimodal = bool(OLLAMABOT_MULTIMODAL)
    max_history_len = 10
    try:
        max_history_len = int(OLLAMABOT_MAX_HISTORY_LEN)
    except ValueError:
        print(
            f"OLLAMABOT_MAX_HISTORY_LEN wasn't an int, defaulting to {max_history_len}"
        )
        pass

    @client.event
    async def on_ready():
        print(f"We have logged in as {client.user}")

    @client.event
    async def on_message(message):
        print(message)

        if message.author == client.user:
            return

        if client.user not in message.mentions:
            return

        channel_id = message.channel.id
        if channel_id not in conversation_histories:
            conversation_histories[channel_id] = deque(maxlen=max_history_len)

        print(message)

        # Proper shutdown with stopping the model
        if message.content.strip() == f"<@{client.user.id}> /shutdown":
            if message.author.guild_permissions.administrator:
                await message.channel.send(
                    "Verily, thou shalt not witness mine ultimate demise..."
                )
                await message.channel.send("Lo, I shall return anon, as is my wont.")
                await client.close()
                sys.exit(0x00)
            else:
                await message.channel.send(
                    "Thou, of lesser station, art unfit to command mine cessation."
                )
                return

        images = []
        if message.attachments and is_multimodal:
            for attachment in message.attachments:
                if not attachment.filename.lower().endswith((".png", ".jpg")):
                    continue

                image_data = await attachment.read()
                image_b64 = base64.b64encode(image_data).decode("utf-8")
                images.append(image_b64)
                print("Image appended")

        current_message = {
            "role": "user",
            "content": message.content.replace(f"<@{client.user.id}>", "").strip(),
            "images": images if images else None,
        }

        conversation_histories[channel_id].append(current_message)

        conversation_with_context = list(conversation_histories[channel_id])

        response = ollama.chat(
            model="custom",
            messages=conversation_with_context,
        )

        print(response)

        rspv_msg = response["message"]["content"]

        conversation_histories[channel_id].append(
            {"role": "assistant", "content": rspv_msg}
        )

        print(response)

        rspv_msg = response["message"]["content"]

        await message.channel.send(rspv_msg)

    client.run(OLLAMABOT_DISCORD_TOKEN)


if __name__ == "__main__":
    its_alive()
