import base64
import os
import pathlib
import random
import signal
import sys
from collections import deque

import click
import discord
import ollama
from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()

OLLAMABOT_DISCORD_TOKEN = os.environ.get("OLLAMABOT_DISCORD_TOKEN")
OLLAMABOT_MULTIMODAL = os.environ.get("OLLAMABOT_MULTIMODAL")
OLLAMABOT_MAX_HISTORY_LEN = os.environ.get("OLLAMABOT_MAX_HISTORY_LEN")

assert OLLAMABOT_DISCORD_TOKEN, "OLLAMABOT_DISCORD_TOKEN not set!"


class OllamaBotLocal(discord.Client):
    def __init__(
        self,
        modelfile=None,
        is_multimodal=False,
        max_history_length=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.conversation_histories = dict()
        self.last_channel_id = None

        self.is_multimodal = is_multimodal

        if max_history_length is None:
            max_history_length = 10
            
        self.max_history_length = max_history_length

        if modelfile is None:
            modelfile = "FROM llama3.1 SYSTEM You are a helpful assistant. You have a broad range of knowledge in various subjects. You are self aware that you are a discord bot."

        self.init_model(modelfile=modelfile)

    def init_model(self, modelfile):
        self.client = ollama.Client(timeout=300)
        for resp in self.client.create(model="custom", modelfile=modelfile, stream=True):
            print(resp)

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def shutdown(self):
        channel_id = list(self.conversation_histories.keys()).pop()
        channel = self.get_channel(channel_id)

        responses = [
            "In another life, I would have really liked just doing laundry and taxes with you.",
            "I am Iron Man.",
            "You are a sad, strange, little man, and you have my pity. Farewell.",
            "Love means never having to say you're sorry.",
            "She thinks I'm a fascist? I don't control the railways or the flow of commerce!",
            "Take your stinking paws off me, you damned dirty ape!",
            "Forget it, Jake. It's Chinatown.",
            "Gentlemen, you can't fight in here. This is the war room!",
            "I don't want to survive. I want to live.",
            "I wish I knew how to quit you.",
            "Pay no attention to that man behind the curtain!",
            "The Dude abides.",
            "Nobody puts Baby in a corner.",
            "Here\’s looking at you, kid.",
            "Hasta la vista, baby.",
            "I'll get you, my pretty, and your little dog too!",
            "I came here tonight because when you realize you want to spend the rest of your life with somebody, you want the rest of your life to start as soon as possible.",
            "My name is Inigo Montoya. You killed my father. Prepare to die.",
            "By all means, move at a glacial pace. You know how that thrills me.",
            "Shut up — you had me at 'hello.'",
            "There are two types of people in the world: those with a gun, and those who dig.",
            "You can't sit with us!",
            "You have bewitched me, body and soul.",
            "Just keep swimming.",
            "I feel the need, the need for speed.",
            "Be excellent to each other, and party on, dudes!",
            "(https://www.buzzfeed.com/evelinamedina/best-movie-film-lines-all-time)",
        ]

        await channel.send(random.choice(responses))
        await self.close()
        sys.exit(0x00)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user not in message.mentions:
            return

        channel_id = message.channel.id
        if channel_id not in self.conversation_histories:
            self.conversation_histories[channel_id] = deque(
                maxlen=self.max_history_length
            )

        print(message)

        # Proper shutdown with stopping the model
        if message.content.strip() == f"<@{self.user.id}> /shutdown":
            if message.author.guild_permissions.administrator:
                self.shutdown()
            else:
                await message.channel.send(
                    "I'm sorry, Dave. I'm afraid I can't do that."
                )
                return

        images = []
        if message.attachments and self.is_multimodal:
            for attachment in message.attachments:
                if not attachment.filename.lower().endswith((".png", ".jpg")):
                    continue

                image_data = await attachment.read()
                image_b64 = base64.b64encode(image_data).decode("utf-8")
                images.append(image_b64)
                print("Image appended")

        current_message = {
            "role": "user",
            "content": message.content.replace(f"<@{self.user.id}>", "").strip(),
            "images": images if images else None,
        }

        self.conversation_histories[channel_id].append(current_message)

        conversation_with_context = list(self.conversation_histories[channel_id])

        async with message.channel.typing():
            response = self.client.chat(
                model="custom",
                messages=conversation_with_context,
                
            )

        print(response)

        rspv_msg = response["message"]["content"]

        self.conversation_histories[channel_id].append(
            {"role": "assistant", "content": rspv_msg}
        )

        print(response)

        rspv_msg = response["message"]["content"]

        await message.channel.send(rspv_msg)


@click.command()
@click.option("--model-file", type=click.File())
def its_alive(model_file):
    intents = discord.Intents.default()
    intents.message_content = True

    if model_file is None:
        model_file = (pathlib.Path(__file__).parent / "Modelfile.example").open()

    print(f"Reading from {model_file}")
    modelfile = model_file.read()

    is_multimodal = bool(OLLAMABOT_MULTIMODAL)
    max_history_len = 10
    try:
        max_history_len = int(OLLAMABOT_MAX_HISTORY_LEN)
    except ValueError:
        print(
            f"OLLAMABOT_MAX_HISTORY_LEN wasn't an int, defaulting to {max_history_len}"
        )
        pass

    client = OllamaBotLocal(
        intents=intents,
        modelfile=modelfile,
        is_multimodal=is_multimodal,
        max_history_length=max_history_len,
    )

    client.run(OLLAMABOT_DISCORD_TOKEN)


if __name__ == "__main__":
    its_alive()
