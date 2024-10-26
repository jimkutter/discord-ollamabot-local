import os
import discord
import ollama
import click

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

OLLAMABOT_DISCORD_TOKEN = os.environ.get("OLLAMABOT_DISCORD_TOKEN")
OLLAMABOT_MODEL = os.environ.get("OLLAMABOT_MODEL")
OLLAMABOT_SYSTEM_PROMPT = os.environ.get("OLLAMABOT_SYSTEM_PROMPT")

assert OLLAMABOT_DISCORD_TOKEN, "OLLAMABOT_DISCORD_TOKEN not set!"
assert OLLAMABOT_MODEL, "OLLAMABOT_MODEL not set!"
assert OLLAMABOT_SYSTEM_PROMPT, "OLLAMABOT_SYSTEM_PROMPT not set!"

messages = list()

@click.command()
@click.option("--model-file", type=click.File("rb"))
def its_alive(model_file):
    global messages
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    if model_file is None:
        modelfile = f"""
        FROM {OLLAMABOT_MODEL}
        SYSTEM {OLLAMABOT_SYSTEM_PROMPT}
        """
    else:
        modelfile = model_file

    ollama.create(model="custom", modelfile=modelfile)

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

        
        print(message)

        response = ollama.chat(
            model="custom",
            messages=[
                            {
                "role": "user",
                "content": message.content,
            },
            ],
        )

        print(response)

        rspv_msg = response["message"]["content"]

        await message.channel.send(rspv_msg)

    client.run(OLLAMABOT_DISCORD_TOKEN)


if __name__ == "__main__":
    its_alive()
