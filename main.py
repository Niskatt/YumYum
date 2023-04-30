import discord
from discord.ext import commands
import json
import os
import asyncio


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='/', intents=intents)
client.remove_command('help')

recipes = {}

# Event-Handler, der aufgerufen wird, wenn der Bot startet
@client.event
async def on_ready():
    print('Der Bot ist bereit.')
    client.loop.create_task(ping_bot()) # Task starten
  
# asynchrone Funktion, die den Bot alle 2 Minuten anpingt
async def ping_bot():
    await client.wait_until_ready() # warten, bis der Bot bereit ist

    while not client.is_closed():
        await client.change_presence(activity=discord.Game(name="Ping!"))
        await asyncio.sleep(120) # 2 Minuten warten

# Laden der Rezepte beim Start des Bots
try:
    with open('recipes.json', 'r') as f:
        recipes = json.load(f)
except FileNotFoundError:
    print('Keine gespeicherten Rezepte gefunden.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/rezept_hinzufügen'):
        await rezept_hinzufügen(message.channel, message.author)
    elif message.content.startswith('/rezept_liste'):
        await rezept_liste(message.channel)
    elif message.content.startswith('/rezept_bearbeiten'):
        await rezept_bearbeiten(message.channel, message.author)
    elif message.content.startswith('/rezept_lesen'):
        await rezept_lesen(message.channel, message.author)  
    elif message.content.startswith('/hilfe'):
        await hilfe(message.channel)

# Speichern der Rezepte beim Herunterfahren des Bots
def save_recipes():
    with open('recipes.json', 'w') as f:
        json.dump(recipes, f)

@client.command()
async def rezept_hinzufügen(channel, author):
    await channel.send(f'{author.mention}, gib bitte den Namen des Rezepts ein:')
    def check_name(m):
        return m.author == author and m.channel == channel
    name_msg = await client.wait_for('message', check=check_name)
    recipe_name = name_msg.content

    if recipe_name in recipes:
        await channel.send(f'{author.mention}, ein Rezept mit diesem Namen existiert bereits.')
        return

    await channel.send(f'{author.mention}, gib bitte die Zubereitung des Rezepts ein:')
    def check_zubereitung(m):
        return m.author == author and m.channel == channel
    zubereitung_msg = await client.wait_for('message', check=check_zubereitung)
    recipe_zubereitung = zubereitung_msg.content

    recipes[recipe_name] = recipe_zubereitung
    with open("recipes.json", "w") as f:
        json.dump(recipes, f)

    await channel.send(f'{author.mention}, das Rezept wurde erfolgreich hinzugefügt.')

@client.command()
async def rezept_liste(channel):
    if not recipes:
        await channel.send('Es wurden noch keine Rezepte hinzugefügt.')
        return

    recipe_list = 'Liste der verfügbaren Rezepte:\n\n'
    for name in recipes.keys():
        recipe_list += f'{name}\n'
    await channel.send(recipe_list)


@client.command()
async def hilfe(ctx):
    # Get all commands registered with the bot
    command_list = [command.name for command in client.commands]
  
    # Format the command list as a string
    command_string = '\n'.join(command_list)

    # Send the list of commands to the user
    await ctx.send(f'Folgende Befehle sind verfügbar:\n{command_string}')

@client.command()
async def rezept_bearbeiten(channel, author):
    await channel.send(f'{author.mention}, gib bitte den Namen des Rezepts ein, das du bearbeiten möchtest:')
    def check_name(m):
        return m.author == author and m.channel == channel
    name_msg = await client.wait_for('message', check=check_name)
    recipe_name = name_msg.content

    if recipe_name not in recipes:
        await channel.send(f'{author.mention}, ein Rezept mit diesem Namen existiert nicht.')
        return

    await channel.send(f'{author.mention}, gib bitte die neue Zubereitung des Rezepts ein:')
    def check_zubereitung(m):
        return m.author == author

@client.command()
async def rezept_lesen(channel, author):
    await channel.send(f'{author.mention}, gib bitte den Namen des Rezepts ein, dessen Zubereitung du abrufen möchtest:')
    def check_name(m):
        return m.author == author and m.channel == channel
    name_msg = await client.wait_for('message', check=check_name)
    recipe_name = name_msg.content

    if recipe_name not in recipes:
        await channel.send(f'{author.mention}, es existiert kein Rezept mit diesem Namen.')
        return

    await channel.send(f'{author.mention}, die Zubereitung von {recipe_name} lautet:')
    await channel.send(recipes[recipe_name])

 
# Speichern der Rezepte beim Herunterfahren des Bots
@client.event
async def on_shutdown():
    print('Speichere Rezepte...')
    save_recipes()

client.run(os.environ['Discord_Token'])
