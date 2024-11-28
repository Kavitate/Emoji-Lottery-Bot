import json
import discord
import random

def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.critical("The config.json file was not found.")
        raise
    except json.JSONDecodeError:
        logging.critical("config.json is not a valid JSON file.")
        raise
    except Exception as e:
        logging.critical(f"An unexpected error occurred while loading config.json: {e}")
        raise

config = load_config()
discord_bot_token = config["discord_bot_token"]
server_id = config['server_id']
channel_id = config['channel_id']

selected_emoji = '🐬'

class WinnerPick(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'Logged in as {self.user}.')

client = WinnerPick()

# Dictionary to store users who used the correct emoji.
emoji_users = {}

@client.tree.command(name='users', description="Lists users.")
async def users(interaction: discord.Interaction):
    global emoji_users
    emoji_users = {}  # Reset the dictionary to avoid duplicates.

    channel = client.get_channel(int(channel_id))
    if not channel:
        await interaction.response.send_message(f"Channel not found.", ephemeral=True))
        return

    # Retrieve the message history.
    async for message in channel.history(limit=None):
        if selected_emoji in message.content and message.author.id != client.user.id:
            emoji_users[message.author.id] = message.author.name

    if not emoji_users:
        await interaction.response.send_message("No users have used the correct emoji yet.", ephemeral=True)
        return

    user_list = "\n".join([f"{username} (ID: {user_id})" for user_id, username in emoji_users.items()])

    # Save the user list to a .txt file
    with open("user_list.txt", "w") as file:
        file.write(user_list)

    embed = discord.Embed(
        title=f"Correct emoji {selected_emoji} used by:",
        description=user_list,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name='pickwinner', description="Pick a random winner.")
async def pickwinner(interaction: discord.Interaction):
    global emoji_users
    if not emoji_users:
        await interaction.response.send_message(f"No users have used the correct emoji yet.", ephemeral=True)
        return

    # Pick a random winner.
    winner_id, winner_name = random.choice(list(emoji_users.items()))

    embed = discord.Embed(
        title="The winner is:",
        description=f"{winner_name} (ID: {winner_id})",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

def run_discord_bot():
    try:
        client.run(config["discord_bot_token"])
    except Exception as e:
        logging.error(f"An error occurred while running the bot: {e}")
    finally:
        if client:
            asyncio.run(client.close())

if __name__ == "__main__":
    run_discord_bot()
