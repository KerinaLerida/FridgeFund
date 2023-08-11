import discord
from database import SimpleSQLiteDatabase


# Send messages
async def send_message(message,user_message, is_private):
    try:
        response = handle_response(message,user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'MTEzNTYzMTUwMDEwNTI0MDcxMA.GKzrwN.Z3ixF-VMB6j9BvfM7pUCEwN0lZaXXuWE0Z9uCM'
    client = discord.Client(intents=discord.Intents.all())
    database = SimpleSQLiteDatabase('my_database.db')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})")

        # If the user message contains a '$' in front of the text, the bot will answer, else it wont
        if user_message[0] == '$':
            user_message = user_message[1:]  # [1:] Removes the '?'
            await send_message(message,user_message, is_private=False)
        else:
            return

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)

def handle_response(message,strmessage):
    p_message = strmessage.lower()
    author = message.author
    print(author.id)

    if p_message == 'hello':
        return 'Hey there!'

    if p_message == '!help':
        return "`This is a help message that you can modify.`"

    if p_message == 'balance':

        return ("You have " + str(author) + "NPC coins")
    
