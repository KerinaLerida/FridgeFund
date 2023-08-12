import discord
from database import SimpleSQLiteDatabase
import logging
import responses


def check_role(name_role, msg):
    verif_role = discord.utils.get(msg.guild.roles, name=name_role)
    if verif_role in msg.author.roles:
        return True
    return False

# Send messages
async def send_message(message, user_message, my_database, ):
    try:
        response = responses.handle_response(message, user_message, my_database)
        if response:
            await message.channel.send(response)

    except Exception as e:
        print(e)
        logging.error(e)


def run_discord_bot():
    TOKEN = 'MTEzNTYzMTUwMDEwNTI0MDcxMA.Gl0PnW.kAilrIdYshfjaN2vEcXJUhurqjbY44-Msm6DM0'
    client = discord.Client(intents=discord.Intents.all())
    my_database = SimpleSQLiteDatabase('my_database.db')
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        logging.info(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # ******************** DEBUG ********************
        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        id_user = str(message.author.id)

        # ************************************************

        if message.channel.name == "🤖╿fridgefund":
            if check_role("Cotisant", message):  # Vérifie : Role Cotisant nécessaire
                # If the user message contains a '$' in front of the text, the bot will answer, else it wont
                if user_message[0] == '$':
                    user_message = user_message[1:]  # [1:] Removes the '?'
                    await send_message(message, user_message, my_database)
                else:
                    return

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)

