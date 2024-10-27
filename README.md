# ollamabot

Run any locally install ollama bot and connect it directly to discord.

## Pre-requisites
* [ollama](https://ollama.com/)
* [rye](https://rye.astral.sh/)
* Ensure you have a [discord bot account](https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro)
* [Ensure ollama runs locally](https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro)

### Geting up and running
* `rye sync`
* Make sure your `.env` is setup (see `env.example`)
* `python ollamabot.py --help`
* `python ollamabot.py --model-file Modelfile.example`