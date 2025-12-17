import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from database import Database
from config import (
    CURRENCY_COINS, 
    CURRENCY_DIAMONDS,
    GUILD_ID,
    EMOJI_COINS,
    EMOJI_DIAMONDS,
    CONVERSION_RATE,
    DUEL_TIMEOUT,
    TRANSFER_FEE,
    BUTTON_TIMEOUT,
    ROLE_COLOR_PRICE,
    ROLE_NAME_PRICE,
    ROLE_CREATE_PRICE,
    PRIVATE_CATEGORY_ID,
    ROOM_RENAME_PRICE,
    ROOM_COLOR_PRICE,
    ROOM_LOG_CHANNEL_ID,
    TRANSFER_LOG_CHANNEL_ID,
    MARRY_PRICE,
    LOVE_CATEGORY_ID,
    LOVE_VOICE_TRANSFER_ID,
    LOVE_ROLE_ID,
    LOVE_LOG_CHANNEL_ID,
    BOT_TOKEN,
)
import random
from typing import Literal

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all()
            # application_id will be auto-detected from token
        )
        self.tree_commands = {}
        self.db = Database()
        self.GUILD = discord.Object(id=GUILD_ID)
        self.love_channels = {}

    async def setup_hook(self):
        try:
            print("Starting command registration...")
            
            # Register regular commands
            self.remove_command('help')  # Remove default help command
            
            # Sync slash commands - sync guild commands first for faster availability
            print("Syncing guild commands...")
            await self.tree.sync(guild=self.GUILD)
            print("Guild commands synced!")
            
            # Also sync global commands (takes longer)
            print("Syncing global commands...")
            await self.tree.sync()
            print("Global commands synced!")
            
            print("\nCommands successfully registered!")
            
            # Check commands
            try:
                global_commands = await self.tree.fetch_commands()
                guild_commands = await self.tree.fetch_commands(guild=self.GUILD)
                
                print("\nGlobal commands:")
                for cmd in global_commands:
                    print(f"  /{cmd.name} - {cmd.description}")
                    
                print("\nServer commands:")
                for cmd in guild_commands:
                    print(f"  /{cmd.name} - {cmd.description}")
            except Exception as e:
                print(f"Warning: Could not fetch command list: {e}")
                
        except discord.errors.Forbidden as e:
            print(f"ERROR: Bot doesn't have permission to sync commands!")
            print(f"Details: {e}")
            print("\nPossible solutions:")
            print("1. Make sure the bot token is correct")
            print("2. Check that you're using the bot's token, not a user token")
            print("3. The application_id will be auto-detected from token")
            print("\nBot will continue running, but commands may not work until synced.")
        except Exception as e:
            print(f"ERROR registering commands: {e}")
            import traceback
            traceback.print_exc()
            print("\nBot will continue running, but commands may not work until synced.")

    async def on_ready(self):
        print(f"\n{'='*50}")
        print(f"Bot {self.user} is ready!")
        print(f"Bot ID: {self.user.id}")
        print(f"{'='*50}\n")
        
        print("List of all servers:")
        for guild in self.guilds:
            is_target = " [TARGET]" if guild.id == GUILD_ID else ""
            print(f"  - {guild.name} (ID: {guild.id}){is_target}")
        
        print("\nFetching registered commands...")
        try:
            guild_commands = await self.tree.fetch_commands(guild=self.GUILD)
            print(f"\nServer commands ({len(guild_commands)}):")
            for cmd in guild_commands:
                print(f"  /{cmd.name} - {cmd.description}")
        except Exception as e:
            print(f"Could not fetch commands: {e}")
        
        print(f"\n{'='*50}")
        print("Bot is online and ready to use!")
        print("Commands should appear in Discord within a few seconds.")
        print(f"{'='*50}\n")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        try:
            # Update statistics only if user is not a bot
            if not member.bot:
                # If user joined a channel
                if after.channel and not before.channel:
                    self.db.update_voice_activity(member.id, member.guild.id, True)
                # If user left a channel
                elif before.channel and not after.channel:
                    self.db.update_voice_activity(member.id, member.guild.id, False)
                # If user switched between channels, do nothing
            
            # If user entered voice transfer channel
            if after.channel and after.channel.id == LOVE_VOICE_TRANSFER_ID:
                # Check if user has a marriage
                marriage = self.db.get_marriage(member.id)
                if marriage:
                    # Create channel
                    category = member.guild.get_channel(LOVE_CATEGORY_ID)
                    if category:
                        partner_id = marriage[1] if marriage[0] == member.id else marriage[0]
                        partner = member.guild.get_member(partner_id)
                        if partner:
                            # Use Discord tags (username) instead of display_name
                            channel_name = f"{member.name} ❤️ {partner.name}"
                            voice_channel = await member.guild.create_voice_channel(
                                name=channel_name,
                                category=category,
                                user_limit=2
                            )
                            await member.move_to(voice_channel)
                            
                            # Remember channel for subsequent deletion
                            self.love_channels[voice_channel.id] = {
                                "creator": member.id,
                                "partner": partner_id
                            }

                            # Log channel creation
                            await send_log(
                                self,
                                "Love room created",
                                f"**Creator:** {member.mention} (`{member.id}`)\n"
                                f"**Partner:** {partner.mention} (`{partner_id}`)\n"
                                f"**Channel:** {voice_channel.mention}",
                                log_type="love",
                                color=0xFF69B4
                            )

            # If user left the channel
            if before.channel and before.channel.id in self.love_channels:
                # If no one is left in the channel
                if len(before.channel.members) == 0:
                    channel_info = self.love_channels[before.channel.id]
                    creator = member.guild.get_member(channel_info["creator"])
                    partner = member.guild.get_member(channel_info["partner"])
                    
                    # Log channel deletion
                    creator_mention = creator.mention if creator else f"<@{channel_info.get('creator')}>"
                    partner_mention = partner.mention if partner else f"<@{channel_info.get('partner')}>"

                    await send_log(
                        self,
                        "Love room deleted",
                        f"**Owners:** {creator_mention} and {partner_mention}\n"
                        f"**Channel:** {before.channel.name}",
                        log_type="love",
                        color=0xFF0000
                    )
                    
                    await before.channel.delete()
                    del self.love_channels[before.channel.id]

        except Exception as e:
            print(f"[ERROR] Error in voice state update: {str(e)}")

    async def on_message(self, message: discord.Message):
        # Increment message counter if message is not from a bot
        if not message.author.bot:
            self.db.increment_messages(message.author.id, message.guild.id)
        await self.process_commands(message)

async def send_log(
    bot: commands.Bot,
    title: str,
    description: str,
    log_type: str = "room",  # room, transfer, or love
    color: int = 0x2b2d31
):
    """
    Send log to a special channel
    log_type: "room" for room logs, "transfer" for transfer logs, "love" for love room logs
    """
    try:
        # Select channel based on log type
        if log_type == "room":
            channel_id = ROOM_LOG_CHANNEL_ID
        elif log_type == "transfer":
            channel_id = TRANSFER_LOG_CHANNEL_ID
        else:  # love
            channel_id = LOVE_LOG_CHANNEL_ID
            
        log_channel = bot.get_channel(channel_id)
        
        if log_channel:
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=embed)
    except Exception as e:
        print(f"[ERROR] Failed to send {log_type} log: {str(e)}")

bot = Bot()

@bot.tree.command(
    name="avatar",
    description="Shows user avatar"
)
@app_commands.guilds(bot.GUILD)  # Register as server command for faster sync
@app_commands.describe(
    user="Select user whose avatar you want to view"
)
async def avatar(interaction: discord.Interaction, user: discord.User):
    avatar_url = user.display_avatar.url
    
    embed = discord.Embed(
        title=f"Avatar of {user.name}"
    )
    embed.set_image(url=avatar_url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="balance",
    description="Shows user balance"
)
@app_commands.guilds(bot.GUILD)  # Register as server command for faster sync
@app_commands.describe(
    user="Select user (optional)"
)
async def balance(
    interaction: discord.Interaction, 
    user: discord.User = None
):
    # If user is not specified, show command author's balance
    target_user = user if user else interaction.user
    user_balance = bot.db.get_balance(target_user.id)
                                                                                                                                                                                                                                                                                            
    embed = discord.Embed(
        title="Current Balance —",
        description=target_user.name,
        color=0x2b2d31
    )
    
    embed.add_field(
        name=f"⠀⠀{CURRENCY_COINS}:⠀⠀",
        value=f"```⠀{user_balance['coins']}⠀```",
        inline=True
    )
    
    embed.add_field(
        name=f"⠀⠀{CURRENCY_DIAMONDS}:⠀⠀",
        value=f"```⠀{user_balance['diamonds']}⠀```",
        inline=True
    )
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="addm",
    description="Add currency to user"
)
@app_commands.guilds(bot.GUILD)  # Use GUILD from bot instance
@app_commands.describe(
    user="Select user",
    currency_type="Select currency type",
    amount="Amount of currency to add"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name=CURRENCY_COINS, value="coins"),
    app_commands.Choice(name=CURRENCY_DIAMONDS, value="diamonds")
])
async def addm(
    interaction: discord.Interaction,
    user: discord.User,
    currency_type: app_commands.Choice[str],
    amount: int
):
    # Check administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You don't have permission to use this command!",
            ephemeral=True
        )
        return

    if amount <= 0:
        await interaction.response.send_message(
            "Amount must be a positive number!",
            ephemeral=True
        )
        return

    new_balance = bot.db.add_currency(user.id, currency_type.value, amount)
    
    currency_name = CURRENCY_COINS if currency_type.value == "coins" else CURRENCY_DIAMONDS
    current_amount = new_balance["coins"] if currency_type.value == "coins" else new_balance["diamonds"]
    
    await interaction.response.send_message(
        f"Added {amount} {currency_name} to {user.name}\n"
        f"Current balance: {current_amount} {currency_name}",
        ephemeral=True
    )

@bot.tree.command(
    name="banner",
    description="Shows user banner"
)
@app_commands.guilds(bot.GUILD)  # Add registration for specific server
@app_commands.describe(
    user="Select user whose banner you want to view"
)
async def banner(interaction: discord.Interaction, user: discord.User):
    # Get full user information
    user = await bot.fetch_user(user.id)
    
    # Check if user has a banner
    if user.banner is None:
        await interaction.response.send_message(
            f"User {user.name} doesn't have a banner",
            ephemeral=True
        )
        return
    
    banner_url = user.banner.url
    
    embed = discord.Embed(
        title=f"Banner of {user.name}"
    )
    embed.set_image(url=banner_url)
    
    await interaction.response.send_message(embed=embed)

class CoinflipView(discord.ui.View):
    def __init__(self, amount: int, user_balance: dict, user: discord.User):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.amount = amount
        self.user_balance = user_balance
        self.user = user
        self.result = random.choice(["Heads", "Tails"])

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.secondary)
    async def heads_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_game(interaction, "Heads")

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.secondary)
    async def tails_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_game(interaction, "Tails")

    async def process_game(self, interaction: discord.Interaction, choice: Literal["Heads", "Tails"]):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        if choice == self.result:
            win_amount = self.amount * 2
            new_balance = bot.db.add_currency(interaction.user.id, "coins", win_amount)
            embed = discord.Embed(
                title="Coin Flip",
                description=f"<@{interaction.user.id}>, it landed on {self.result},\nYou won {win_amount} {EMOJI_COINS}",
                color=0x2b2d31
            )
        else:
            new_balance = bot.db.add_currency(interaction.user.id, "coins", -self.amount)
            embed = discord.Embed(
                title="Coin Flip",
                description=f"<@{interaction.user.id}>, it landed on {self.result},\nYou lost {self.amount} {EMOJI_COINS}",
                color=0x2b2d31
            )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        # Send message without view to remove buttons
        await interaction.response.edit_message(embed=embed, view=None)

@bot.tree.command(
    name="coinflip",
    description="Play coin flip"
)
@app_commands.describe(
    amount="Bet amount (50 to 50000)"
)
@app_commands.guilds(bot.GUILD)
async def coinflip(interaction: discord.Interaction, amount: int):
    if amount < 50 or amount > 50000:
        await interaction.response.send_message(
            "Bet must be between 50 and 50000 coins!",
            ephemeral=True
        )
        return

    user_balance = bot.db.get_balance(interaction.user.id)
    if user_balance["coins"] < amount:
        await interaction.response.send_message(
            f"You don't have enough {CURRENCY_COINS} for this bet!",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Coin Flip",
        description=f"<@{interaction.user.id}>, choose\nthe side you want to\nbet your {amount} {EMOJI_COINS} on",
        color=0x2b2d31
    )
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    view = CoinflipView(amount, user_balance, interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(
    name="convert",
    description=f"Convert {CURRENCY_DIAMONDS} to {CURRENCY_COINS}"
)
@app_commands.describe(
    amount=f"Amount of {CURRENCY_DIAMONDS} to convert"
)
@app_commands.guilds(bot.GUILD)
async def convert(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message(
            f"Amount of {CURRENCY_DIAMONDS} must be a positive number!",
            ephemeral=True
        )
        return

    # Check user balance
    user_balance = bot.db.get_balance(interaction.user.id)
    if user_balance["diamonds"] < amount:
        await interaction.response.send_message(
            f"You don't have enough {CURRENCY_DIAMONDS} to convert!",
            ephemeral=True
        )
        return

    # Calculate amount of coins user will receive
    coins_to_receive = amount * CONVERSION_RATE

    # Remove stars and add coins
    bot.db.add_currency(interaction.user.id, "diamonds", -amount)
    new_balance = bot.db.add_currency(interaction.user.id, "coins", coins_to_receive)

    embed = discord.Embed(
        title="Currency Conversion",
        description=f"<@{interaction.user.id}>, you successfully converted:\n{amount} {EMOJI_DIAMONDS} ➜ {coins_to_receive} {EMOJI_COINS}",
        color=0x2b2d31
    )

    embed.add_field(
        name=f"⠀⠀{CURRENCY_COINS}:⠀⠀",
        value=f"```⠀{new_balance['coins']}⠀```",
        inline=True
    )
    
    embed.add_field(
        name=f"⠀⠀{CURRENCY_DIAMONDS}:⠀⠀",
        value=f"```⠀{new_balance['diamonds']}⠀```",
        inline=True
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

class DuelView(discord.ui.View):
    def __init__(self, amount: int, challenger: discord.User, target: discord.User):
        super().__init__(timeout=DUEL_TIMEOUT)
        self.amount = amount
        self.challenger = challenger
        self.target = target
        self.result = None
        self.message = None

    async def on_timeout(self):
        # Create embed for timeout
        embed = discord.Embed(
            title="Duel",
            description=f"<@{self.challenger.id}>, no one responded\nto your duel",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.challenger.display_avatar.url)
        
        # Check if message exists
        if self.message:
            try:
                await self.message.edit(embed=embed, view=None)
            except discord.NotFound:
                pass  # Ignore error if message was deleted

    @discord.ui.button(label="Join", style=discord.ButtonStyle.blurple)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("This is not your duel!", ephemeral=True)
            return

        # Check both players' balance
        challenger_balance = bot.db.get_balance(self.challenger.id)
        target_balance = bot.db.get_balance(self.target.id)

        if challenger_balance["coins"] < self.amount or target_balance["coins"] < self.amount:
            await interaction.response.edit_message(
                content="One of the players doesn't have enough coins for the duel!",
                embed=None,
                view=None
            )
            return

        # Determine winner
        winner = random.choice([self.challenger, self.target])
        loser = self.target if winner == self.challenger else self.challenger

        # Update balances
        bot.db.add_currency(winner.id, "coins", self.amount)
        bot.db.add_currency(loser.id, "coins", -self.amount)

        # Create embed with result
        embed = discord.Embed(
            title="Duel",
            description=f"<@{winner.id}> won {self.amount} {EMOJI_COINS}",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=winner.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("This is not your duel!", ephemeral=True)
            return

        # Create embed for decline
        embed = discord.Embed(
            title="Duel",
            description=f"<@{self.target.id}> declined the duel",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.target.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=None)

@bot.tree.command(
    name="duel",
    description="Challenge a player to a duel"
)
@app_commands.describe(
    user="Select player for duel",
    amount="Bet amount"
)
@app_commands.guilds(bot.GUILD)
async def duel(interaction: discord.Interaction, user: discord.User, amount: int):
    if user.id == interaction.user.id:
        await interaction.response.send_message(
            "You cannot challenge yourself to a duel!",
            ephemeral=True
        )
        return

    if amount < 50:
        await interaction.response.send_message(
            "Minimum bet is 50 coins!",
            ephemeral=True
        )
        return

    # Check challenger's balance
    challenger_balance = bot.db.get_balance(interaction.user.id)
    if challenger_balance["coins"] < amount:
        await interaction.response.send_message(
            f"You don't have enough {CURRENCY_COINS} for this bet!",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Duel",
        description=f"<@{interaction.user.id}> created a duel for\n{amount} {EMOJI_COINS} with user\n<@{user.id}>",
        color=0x2b2d31
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    view = DuelView(amount, interaction.user, user)
    await interaction.response.send_message(embed=embed, view=view)
    
    # Save message after sending
    view.message = await interaction.original_response()

@bot.tree.command(
    name="give",
    description=f"Transfer currency to another user"
)
@app_commands.guilds(bot.GUILD)  # Register as server command for faster sync
@app_commands.describe(
    user="Select user",
    currency_type="Select currency type",
    amount="Amount to transfer"
)
@app_commands.choices(currency_type=[
    app_commands.Choice(name=CURRENCY_COINS, value="coins"),
    app_commands.Choice(name=CURRENCY_DIAMONDS, value="diamonds")
])
async def give(
    interaction: discord.Interaction,
    user: discord.User,
    currency_type: app_commands.Choice[str],
    amount: int
):
    try:
        # Check if user is trying to transfer currency to themselves
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "You cannot transfer currency to yourself!",
                ephemeral=True
            )
            return

        # Check amount validity
        if amount <= 0:
            await interaction.response.send_message(
                "Amount must be a positive number!",
                ephemeral=True
            )
            return

        # Get sender's balance
        sender_balance = bot.db.get_balance(interaction.user.id)
        
        # Determine currency type and emoji
        currency_name = CURRENCY_COINS if currency_type.value == "coins" else CURRENCY_DIAMONDS
        emoji = EMOJI_COINS if currency_type.value == "coins" else EMOJI_DIAMONDS
        
        # Check if there are enough funds
        if sender_balance[currency_type.value] < amount:
            await interaction.response.send_message(
                f"You don't have enough {currency_name} to transfer!",
                ephemeral=True
            )
            return

        # Calculate fee
        fee = int(amount * TRANSFER_FEE / 100)
        amount_after_fee = amount - fee

        # Execute transfer
        bot.db.add_currency(interaction.user.id, currency_type.value, -amount)
        bot.db.add_currency(user.id, currency_type.value, amount_after_fee)

        # Send message to sender
        embed = discord.Embed(
            title="Transfer Completed",
            description=(
                f"You transferred {amount} {emoji}\n"
                f"Fee: {fee} {emoji}\n"
                f"Recipient: {user.mention}"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Send message to recipient
        try:
            receiver_embed = discord.Embed(
                title="Currency Received",
                description=(
                    f"From: {interaction.user.mention}\n"
                    f"Amount: {amount_after_fee} {emoji}"
                ),
                color=0x2b2d31
            )
            receiver_embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await user.send(embed=receiver_embed)
        except:
            pass  # If recipient has DMs disabled

        # Send log
        log_embed = discord.Embed(
            title=f"{currency_name} Transfer",
            description=(
                f"**From:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                f"**To:** {user.mention} (`{user.id}`)\n"
                f"**Amount:** {amount} {emoji}\n"
                f"**Fee:** {fee} {emoji}\n"
                f"**Received:** {amount_after_fee} {emoji}"
            ),
            color=0x2b2d31,
            timestamp=discord.utils.utcnow()
        )
        log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await send_log(
            bot,
            f"{currency_name} Transfer",
            log_embed.description,
            log_type="transfer",
            color=0x2b2d31
        )

    except Exception as e:
        print(f"[ERROR] Error in give command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred during transfer: {str(e)}",
            ephemeral=True
        )

class RolesView(discord.ui.View):
    def __init__(self, user: discord.User, roles: list):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.user = user
        self.roles = roles
        
        # Create buttons for each role
        for i in range(min(len(roles), 5)):
            button = discord.ui.Button(
                label=str(i + 1),
                style=discord.ButtonStyle.secondary,
                custom_id=str(i),
                row=0
            )
            button.callback = self.button_callback
            self.add_item(button)
        
        # Add "Back" button
        back_button = discord.ui.Button(
            label="Back",
            style=discord.ButtonStyle.red,
            row=1
        )
        back_button.callback = self.back_button_callback
        self.add_item(back_button)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        # Get pressed button index
        button_idx = int(interaction.data["custom_id"])
        if button_idx >= len(self.roles):
            return

        role_id, is_enabled, is_owner = self.roles[button_idx]
        role = interaction.guild.get_role(role_id)
        if role:
            new_state = not is_enabled
            bot.db.toggle_role(self.user.id, role_id, interaction.guild.id, new_state)
            
            try:
                if new_state:
                    await self.user.add_roles(role)
                else:
                    await self.user.remove_roles(role)

                # Update role list
                self.roles = bot.db.get_user_roles(self.user.id, interaction.guild.id)
                
                # Update embed
                description = "Your personal roles:\n\n"
                for i, (r_id, r_enabled, r_owner) in enumerate(self.roles[:5], 1):
                    r = interaction.guild.get_role(r_id)
                    if r:
                        status = "🟢" if r_enabled else "🔴"
                        owner_tag = " (owner)" if r_owner else ""
                        description += f"{i}) {r.mention}{owner_tag} {status}\n"

                embed = discord.Embed(
                    title="Inventory",
                    description=description,
                    color=0x2b2d31
                )
                embed.set_thumbnail(url=self.user.display_avatar.url)
                
                await interaction.response.edit_message(embed=embed, view=self)

            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot doesn't have enough permissions to manage roles!",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"An error occurred: {str(e)}",
                    ephemeral=True
                )

    async def back_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Inventory",
            description=f"Which inventory do you want\nto view?",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=InventoryView(self.user))

class InventoryView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.user = user

    @discord.ui.button(label="Personal Roles", style=discord.ButtonStyle.secondary)
    async def roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        try:
            # Get user's role list
            user_roles = bot.db.get_user_roles(self.user.id, interaction.guild.id)
            
            if not user_roles:
                await interaction.response.send_message(
                    "You don't have personal roles!",
                    ephemeral=True
                )
                return

            description = "Your personal roles:\n\n"
            for i, (role_id, is_enabled, is_owner) in enumerate(user_roles[:5], 1):
                role = interaction.guild.get_role(role_id)
                if role:
                    status = "🟢" if is_enabled else "🔴"
                    owner_tag = " (owner)" if is_owner else ""
                    description += f"{i}) {role.mention}{owner_tag} {status}\n"

            embed = discord.Embed(
                title="Inventory",
                description=description,
                color=0x2b2d31
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)
            
            # Create new view and pass role list to it
            view = RolesView(self.user, user_roles)
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"Error displaying roles: {e}")
            await interaction.response.send_message(
                "An error occurred while loading roles!",
                ephemeral=True
            )

    @discord.ui.button(label="Personal Rooms", style=discord.ButtonStyle.secondary)
    async def rooms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        try:
            # Get user's room list
            rooms = bot.db.get_user_rooms(self.user.id, interaction.guild.id)
            
            if not rooms:
                await interaction.response.send_message(
                    "You don't have personal rooms!",
                    ephemeral=True
                )
                return

            description = "Your personal rooms:\n\n"
            for room_id, voice_id, role_id, name, is_owner, is_coowner in rooms:
                voice_channel = interaction.guild.get_channel(voice_id)
                if voice_channel:
                    status = "👑" if is_owner else "⭐" if is_coowner else "👤"
                    description += f"{status} {voice_channel.mention}\n"

            embed = discord.Embed(
                title="Inventory",
                description=description,
                color=0x2b2d31
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            print(f"[ERROR] Error in rooms_button: {str(e)}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )

    @discord.ui.button(label="Items", style=discord.ButtonStyle.secondary)
    async def items_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        # Here will be item display logic
        embed = discord.Embed(
            title="Inventory",
            description="Your items:",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed)

@bot.tree.command(
    name="inventory",
    description="View your inventory"
)
@app_commands.guilds(bot.GUILD)
async def inventory(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Inventory",
        description=f"Which inventory do you want\nto view?",
        color=0x2b2d31
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    view = InventoryView(interaction.user)
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()

class RoleManagerView(discord.ui.View):
    def __init__(self, user: discord.User, role_id: int):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.user = user
        self.role_id = role_id

    @discord.ui.button(label="Change Color", style=discord.ButtonStyle.secondary)
    async def color_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your role!", ephemeral=True)
            return

        # Check balance
        user_balance = bot.db.get_balance(interaction.user.id)
        if user_balance["coins"] < ROLE_COLOR_PRICE:
            await interaction.response.send_message(
                f"Not enough coins! Required: {ROLE_COLOR_PRICE} {EMOJI_COINS}",
                ephemeral=True
            )
            return

        # Create modal window for color input
        class ColorModal(discord.ui.Modal, title="Change Role Color"):
            color = discord.ui.TextInput(
                label="Enter color in HEX format",
                placeholder="#ff0000",
                min_length=7,
                max_length=7
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    color_str = str(self.color)
                    if not color_str.startswith('#'):
                        await interaction.response.send_message(
                            "Color must start with #!",
                            ephemeral=True
                        )
                        return

                    color_int = int(color_str[1:], 16)
                    role = interaction.guild.get_role(self.view.role_id)
                    
                    # Deduct fee and change color
                    bot.db.add_currency(interaction.user.id, "coins", -ROLE_COLOR_PRICE)
                    await role.edit(color=discord.Color(color_int))
                    
                    embed = discord.Embed(
                        title="Role Management",
                        description=f"Role {role.mention} color successfully changed!\nDeducted {ROLE_COLOR_PRICE} {EMOJI_COINS}",
                        color=discord.Color(color_int)
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=embed)
                
                except ValueError:
                    await interaction.response.send_message(
                        "Invalid color format!",
                        ephemeral=True
                    )

        modal = ColorModal()
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Change Name", style=discord.ButtonStyle.secondary)
    async def name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your role!", ephemeral=True)
            return

        # Check balance
        user_balance = bot.db.get_balance(interaction.user.id)
        if user_balance["coins"] < ROLE_NAME_PRICE:
            await interaction.response.send_message(
                f"Not enough coins! Required: {ROLE_NAME_PRICE} {EMOJI_COINS}",
                ephemeral=True
            )
            return

        # Create modal window for name input
        class NameModal(discord.ui.Modal, title="Change Role Name"):
            name = discord.ui.TextInput(
                label="Enter new role name",
                min_length=1,
                max_length=100
            )

            async def on_submit(self, interaction: discord.Interaction):
                role = interaction.guild.get_role(self.view.role_id)
                
                # Deduct fee and change name
                bot.db.add_currency(interaction.user.id, "coins", -ROLE_NAME_PRICE)
                await role.edit(name=str(self.name))
                
                embed = discord.Embed(
                    title="Role Management",
                    description=f"Role {role.mention} name successfully changed!\nDeducted {ROLE_NAME_PRICE} {EMOJI_COINS}",
                    color=role.color
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                await interaction.response.send_message(embed=embed)

        modal = NameModal()
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Assign Role", style=discord.ButtonStyle.secondary)
    async def give_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your role!", ephemeral=True)
            return

        class GiveModal(discord.ui.Modal, title="Assign Role"):
            user_id = discord.ui.TextInput(
                label="Enter user ID or @mention",
                min_length=1
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    target_id = ''.join(filter(str.isdigit, str(self.user_id)))
                    target_user = await interaction.guild.fetch_member(int(target_id))
                    role = interaction.guild.get_role(self.view.role_id)
                    
                    await target_user.add_roles(role)
                    bot.db.add_user_role(target_user.id, role.id, interaction.guild.id, is_owner=False)
                    
                    embed = discord.Embed(
                        title="Role Management",
                        description=f"Role {role.mention} assigned to {target_user.mention}",
                        color=role.color
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=embed)
                
                except (ValueError, discord.NotFound):
                    await interaction.response.send_message(
                        "User not found!",
                        ephemeral=True
                    )

        modal = GiveModal()
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete Role", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your role!", ephemeral=True)
            return

        role = interaction.guild.get_role(self.role_id)
        bot.db.delete_role(role.id, interaction.guild.id)
        await role.delete()
        
        embed = discord.Embed(
            title="Role Management",
            description="Role successfully deleted!",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

        # Add log before deletion
        await send_log(
            bot,
            "Room deleted",
            f"**Name:** {room_data['name']}\n"
            f"**Owner:** {interaction.user.mention} (`{interaction.user.id}`)",
            log_type="room",
            color=0xED4245  # Red color for deletion
        )

class RoleListView(discord.ui.View):
    def __init__(self, user: discord.User, roles: list):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.user = user
        self.roles = roles
        
        # Create buttons for each role
        for i, (role_id, _, is_owner) in enumerate(roles[:5]):
            if is_owner:  # Show only roles where user is owner
                button = discord.ui.Button(
                    label=f"Role {i+1}",
                    style=discord.ButtonStyle.secondary,
                    custom_id=str(role_id),
                    row=0
                )
                button.callback = self.role_button_callback
                self.add_item(button)

    async def role_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return

        role_id = int(interaction.data["custom_id"])
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message("Role not found!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Role Management",
            description=f"Select action for role {role.mention}",
            color=role.color
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        view = RoleManagerView(interaction.user, role_id)
        await interaction.response.edit_message(embed=embed, view=view)

@bot.tree.command(
    name="role",
    description="Manage personal roles"
)
@app_commands.describe(
    action="Select action"
)
@app_commands.choices(action=[
    app_commands.Choice(name="create", value="create"),
    app_commands.Choice(name="manage", value="manage")
])
@app_commands.guilds(bot.GUILD)
async def role(
    interaction: discord.Interaction,
    action: app_commands.Choice[str]
):
    if action.value == "manage":
        # Get user's role list
        roles = bot.db.get_user_roles(interaction.user.id, interaction.guild.id)
        owned_roles = [(role_id, is_enabled, is_owner) for role_id, is_enabled, is_owner in roles if is_owner]

        if not owned_roles:
            await interaction.response.send_message(
                "You don't have personal roles that you own!",
                ephemeral=True
            )
            return

        description = "Your personal roles:\n\n"
        for i, (role_id, is_enabled, _) in enumerate(owned_roles[:5], 1):
            role = interaction.guild.get_role(role_id)
            if role:
                status = "🟢" if is_enabled else "🔴"
                description += f"{i}) {role.mention} {status}\n"

        embed = discord.Embed(
            title="Role Management",
            description=description,
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        view = RoleListView(interaction.user, owned_roles)
        await interaction.response.send_message(embed=embed, view=view)

    elif action.value == "create":
        # Check user balance
        user_balance = bot.db.get_balance(interaction.user.id)
        if user_balance["coins"] < ROLE_CREATE_PRICE:
            await interaction.response.send_message(
                f"Not enough coins! Required: {ROLE_CREATE_PRICE} {EMOJI_COINS}",
                ephemeral=True
            )
            return

        # Create modal window for role creation
        class CreateRoleModal(discord.ui.Modal, title="Create Role"):
            name = discord.ui.TextInput(
                label="Role Name",
                min_length=1,
                max_length=100
            )
            color = discord.ui.TextInput(
                label="Role Color in HEX format",
                placeholder="#ff0000",
                min_length=7,
                max_length=7
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    color_str = str(self.color)
                    if not color_str.startswith('#'):
                        await interaction.response.send_message(
                            "Color must start with #!",
                            ephemeral=True
                        )
                        return

                    color_int = int(color_str[1:], 16)
                    
                    # Deduct fee for role creation
                    bot.db.add_currency(interaction.user.id, "coins", -ROLE_CREATE_PRICE)
                    
                    new_role = await interaction.guild.create_role(
                        name=str(self.name),
                        color=discord.Color(color_int),
                        reason=f"Personal role created by {interaction.user.name}"
                    )
                    
                    # First add role to database
                    bot.db.add_role(
                        role_id=new_role.id,
                        guild_id=interaction.guild.id,
                        owner_id=interaction.user.id
                    )
                    
                    # Then assign role to user
                    await interaction.user.add_roles(new_role)

                    embed = discord.Embed(
                        title="Create Role",
                        description=f"Role {new_role.mention} successfully created!\nDeducted {ROLE_CREATE_PRICE} {EMOJI_COINS}",
                        color=new_role.color
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    await interaction.response.send_message(embed=embed)

                except ValueError:
                    await interaction.response.send_message(
                        "Invalid color format!",
                        ephemeral=True
                    )
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "Bot doesn't have enough permissions to create role!",
                        ephemeral=True
                    )

        modal = CreateRoleModal()
        await interaction.response.send_modal(modal)

@bot.tree.command(
    name="addroom",
    description="Create private room [ADMIN]"
)
@app_commands.describe(
    name="Room name",
    owner="Room owner ID"
)
@app_commands.guilds(bot.GUILD)
async def addroom(
    interaction: discord.Interaction,
    name: str,
    owner: str
):
    # Check administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You don't have permission to use this command!",
            ephemeral=True
        )
        return

    try:
        # Get category
        category = interaction.guild.get_channel(PRIVATE_CATEGORY_ID)
        if not category:
            await interaction.response.send_message(
                "Category for private rooms not found!",
                ephemeral=True
            )
            return

        # Get owner
        try:
            owner_id = int(''.join(filter(str.isdigit, owner)))
            owner_member = await interaction.guild.fetch_member(owner_id)
            if not owner_member:
                raise ValueError
        except (ValueError, discord.NotFound):
            await interaction.response.send_message(
                "Specified owner not found!",
                ephemeral=True
            )
            return

        # Create role with same name as room
        role = await interaction.guild.create_role(
            name=name,
            reason=f"Role for private room {name}"
        )

        # Assign role to owner
        await owner_member.add_roles(role)

        # Create channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
                connect=False
            ),
            role: discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=True
            ),
            owner_member: discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=True,
                mute_members=True,
                deafen_members=True,
                move_members=True,
                manage_channels=True
            )
        }

        voice_channel = await interaction.guild.create_voice_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            reason=f"Private room created for {owner_member.name}"
        )

        # Save information to database
        bot.db.add_private_room(
            room_id=voice_channel.id,  # Use voice channel ID as primary
            voice_id=voice_channel.id,
            role_id=role.id,
            guild_id=interaction.guild.id,
            owner_id=owner_member.id,
            name=name
        )

        embed = discord.Embed(
            title="Private room created",
            description=(
                f"**Owner:** {owner_member.mention}\n"
                f"**Voice channel:** {voice_channel.mention}\n"
                f"**Access role:** {role.mention}"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=owner_member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

        # Add log after successful creation
        await send_log(
            bot,
            "New room created",
            f"**Name:** {name}\n"
            f"**Owner:** {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"**Text channel:** {text_channel.mention}\n"
            f"**Voice channel:** {voice_channel.mention}",
            log_type="room",
            color=0x57F287  # Green color for creation
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "Bot doesn't have enough permissions to create channels or roles!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"An error occurred while creating room: {str(e)}",
            ephemeral=True
        )

class UserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: str):
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        print(f"[DEBUG] UserSelect callback triggered by {interaction.user}")
        if self.view is not None:
            try:
                print(f"[DEBUG] Calling handle_user_select with user {self.values[0]}")
                await self.view.handle_user_select(interaction, self.values[0])
            except Exception as e:
                print(f"[ERROR] Error in UserSelect callback: {str(e)}")
                await interaction.response.send_message(
                    f"An error occurred while processing selection: {str(e)}",
                    ephemeral=True
                )

    async def handle_user_select(self, interaction: discord.Interaction, selected_user: discord.User):
        print(f"[DEBUG] handle_user_select started. Action: {self.action}")
        
        if interaction.user.id != self.user.id:
            print(f"[DEBUG] User mismatch: {interaction.user.id} != {self.user.id}")
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return

        if self.action == "give_access":
            print(f"[DEBUG] Processing give_access for user {selected_user}")
            try:
                room_data = bot.db.get_room_data(self.room_id)
                print(f"[DEBUG] Room data: {room_data}")
                
                if not room_data:
                    await interaction.response.send_message("Room not found!", ephemeral=True)
                    return

                # Check invitation permissions
                member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
                print(f"[DEBUG] Member data: {member_data}")
                
                if not member_data or (not member_data["is_owner"] and not member_data["is_coowner"]):
                    await interaction.response.send_message(
                        "Only owner and co-owners can invite users!",
                        ephemeral=True
                    )
                    return

                # Check if user is already in room
                existing_member = bot.db.get_member_data(selected_user.id, self.room_id)
                print(f"[DEBUG] Existing member data: {existing_member}")
                
                if existing_member:
                    await interaction.response.send_message(
                        "This user is already in the room!",
                        ephemeral=True
                    )
                    return

                print("[DEBUG] Creating invite embed and view")
                # Create invitation
                invite_embed = discord.Embed(
                    title="Room Invitation",
                    description=(
                        f"{interaction.user.mention} invites you\n"
                        f"to join the room {room_data['name']}"
                    ),
                    color=0x2b2d31
                )
                invite_embed.set_thumbnail(url=interaction.user.display_avatar.url)

                invite_view = RoomInviteView(
                    room_name=room_data['name'],
                    inviter=interaction.user,
                    room_id=self.room_id,
                    role_id=room_data['role_id'],
                    guild_id=interaction.guild_id
                )

                print("[DEBUG] Sending initial response")
                try:
                    # First send response to original interaction
                    await interaction.response.defer(ephemeral=True)
                    
                    print("[DEBUG] Sending DM to user")
                    # Try to send invitation
                    await selected_user.send(embed=invite_embed, view=invite_view)
                    
                    print("[DEBUG] Updating original message")
                    # Update original message
                    success_embed = discord.Embed(
                        title="Room Management",
                        description=f"Invitation sent to user {selected_user.mention}",
                        color=0x2b2d31
                    )
                    success_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    
                    # Remove select
                    for item in self.children[:]:
                        if isinstance(item, discord.ui.UserSelect):
                            self.remove_item(item)
                    
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        embed=success_embed,
                        view=self
                    )
                    
                    # Add log
                    await send_log(
                        bot,
                        "Room invitation sent",
                        f"**Room:** {room_data['name']}\n"
                        f"**Sender:** {interaction.user.mention} ({interaction.user.id})\n"
                        f"**Recipient:** {selected_user.mention} ({selected_user.id})",
                        color=0xFEE75C  # Yellow color for awaiting response
                    )
                    
                except discord.Forbidden:
                    print("[DEBUG] Failed to send DM - Forbidden")
                    await interaction.followup.send(
                        f"Failed to send invitation. User {selected_user.mention} has DMs disabled.",
                        ephemeral=True
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to send invite: {str(e)}")
                    await interaction.followup.send(
                        f"An error occurred while sending invitation: {str(e)}",
                        ephemeral=True
                    )

            except Exception as e:
                print(f"[ERROR] Error in give_access: {str(e)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

        elif self.action == "remove_access":
            # ... code for removing access ...
            pass

        elif self.action == "add_coowner":
            # ... code for adding co-owner ...
            pass

        elif self.action == "remove_coowner":
            # ... code for removing co-owner ...
            pass

class RoomInviteView(discord.ui.View):
    def __init__(self, room_name: str, inviter: discord.User, room_id: int, role_id: int, guild_id: int):
        super().__init__(timeout=300)
        self.room_name = room_name
        self.inviter = inviter
        self.room_id = room_id
        self.role_id = role_id
        self.guild_id = guild_id

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            guild = bot.get_guild(self.guild_id)
            if not guild:
                await interaction.response.send_message("Failed to find server!", ephemeral=True)
                return

            role = guild.get_role(self.role_id)
            if not role:
                await interaction.response.send_message("Failed to find role!", ephemeral=True)
                return

            member = await guild.fetch_member(interaction.user.id)
            if not member:
                await interaction.response.send_message("Failed to find you on the server!", ephemeral=True)
                return
            
            await member.add_roles(role)
            bot.db.add_room_member(interaction.user.id, self.room_id, self.guild_id)
            
            embed = discord.Embed(
                title="Invitation Accepted",
                description=f"You joined the room {self.room_name}",
                color=0x2b2d31
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            try:
                notify_embed = discord.Embed(
                    title="Invitation Accepted",
                    description=f"{interaction.user.mention} accepted your invitation to the room {self.room_name}",
                    color=0x2b2d31
                )
                await self.inviter.send(embed=notify_embed)
            except:
                pass

            # Add log
            await send_log(
                bot,
                "Room Invitation Accepted",
                f"**Room:** {self.room_name}\n"
                f"**Invited by:** {self.inviter.mention} ({self.inviter.id})\n"
                f"**Accepted by:** {interaction.user.mention} ({interaction.user.id})",
                color=0x57F287  # Green color for acceptance
            )

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Invitation Declined",
            description=f"You declined the invitation to the room {self.room_name}",
            color=0x2b2d31
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        try:
            notify_embed = discord.Embed(
                title="Invitation Declined",
                description=f"{interaction.user.mention} declined your invitation to the room {self.room_name}",
                color=0x2b2d31
            )
            await self.inviter.send(embed=notify_embed)
        except:
            pass

        # Add log
        await send_log(
            bot,
            "Room Invitation Declined",
            f"**Room:** {self.room_name}\n"
            f"**Invited by:** {self.inviter.mention} ({self.inviter.id})\n"
            f"**Declined by:** {interaction.user.mention} ({interaction.user.id})",
            color=0xED4245  # Red color for decline
        )

class RoomManagerView(discord.ui.View):
    def __init__(self, user: discord.User, room_id: int):
        super().__init__(timeout=BUTTON_TIMEOUT)
        self.user = user
        self.room_id = room_id
        self.action = None

    @discord.ui.button(label="Grant Access", style=discord.ButtonStyle.secondary)
    async def give_access_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Check invitation permissions
        member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
        if not member_data or (not member_data["is_owner"] and not member_data["is_coowner"]):
            await interaction.response.send_message(
                "Only owner and co-owners can invite users!",
                ephemeral=True
            )
            return

        # Clear previous selects
        for item in self.children[:]:
            if isinstance(item, discord.ui.UserSelect):
                self.remove_item(item)

        # Add select for user selection
        self.action = "give_access"
        select = UserSelect("Select user to invite")
        self.add_item(select)

        embed = discord.Embed(
            title="Inviting User",
            description=f"@{interaction.user.name}, select\nuser you want to\ninvite to the room",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Revoke Access", style=discord.ButtonStyle.secondary)
    async def remove_access_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Clear previous selects
        for item in self.children[:]:
            if isinstance(item, discord.ui.UserSelect):
                self.remove_item(item)

        # Add select for user selection
        self.action = "remove_access"
        select = UserSelect("Select user to remove access")
        self.add_item(select)

        embed = discord.Embed(
            title="Removing User",
            description=f"@{interaction.user.name}, select\nuser you want to\nremove from the room",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Member List", style=discord.ButtonStyle.secondary)
    async def members_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        try:
            room_data = bot.db.get_room_data(self.room_id)
            if not room_data:
                await interaction.response.send_message("Room not found!", ephemeral=True)
                return

            members = bot.db.get_room_members(self.room_id)
            
            description = f"Room Members {room_data['name']}:\n\n"
            
            for user_id, is_owner, is_coowner, total_time, last_join in members:
                member = interaction.guild.get_member(user_id)
                if member:
                    # Convert time
                    current_time = total_time
                    if last_join:
                        try:
                            # Convert time string to UTC datetime
                            last_join_dt = discord.utils.parse_time(last_join).replace(tzinfo=None)
                            current_time += (discord.utils.utcnow().replace(tzinfo=None) - last_join_dt).total_seconds()
                        except:
                            # In case of error use only total_time
                            pass
                        
                    hours = int(current_time // 3600)
                    minutes = int((current_time % 3600) // 60)
                    seconds = int(current_time % 60)
                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    
                    # Add status
                    if is_owner:
                        status = "👑 Owner"
                    elif is_coowner:
                        status = "⭐ Co-owner"
                    else:
                        status = "👤 Member"
                    
                    description += f"{status} {member.mention} - {time_str}\n"

            embed = discord.Embed(
                title="Member List",
                description=description,
                color=0x2b2d31
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            print(f"[ERROR] Error in members_button: {str(e)}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Check modification permissions
        member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
        if not member_data or not member_data["is_owner"]:
            await interaction.response.send_message(
                "Only owner can change room name!",
                ephemeral=True
            )
            return

        # Check balance
        balance = bot.db.get_balance(interaction.user.id)
        if balance["coins"] < ROOM_RENAME_PRICE:
            await interaction.response.send_message(
                f"Not enough coins! Required: {ROOM_RENAME_PRICE} {EMOJI_COINS}",
                ephemeral=True
            )
            return

        class RenameModal(discord.ui.Modal, title="Change Name"):
            new_name = discord.ui.TextInput(
                label=f"New Name (Cost: {ROOM_RENAME_PRICE} {EMOJI_COINS})",
                min_length=1,
                max_length=32
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    room_data = bot.db.get_room_data(self.view.room_id)
                    if not room_data:
                        await interaction.response.send_message("Room not found!", ephemeral=True)
                        return

                    # Deduct coins
                    bot.db.add_currency(interaction.user.id, "coins", -ROOM_RENAME_PRICE)

                    # Get channels and role
                    voice_channel = interaction.guild.get_channel(room_data["voice_id"])
                    role = interaction.guild.get_role(room_data["role_id"])

                    # Update names
                    await voice_channel.edit(name=str(self.new_name))
                    await role.edit(name=str(self.new_name))

                    # Update in database
                    bot.db.update_room_name(self.view.room_id, str(self.new_name))

                    embed = discord.Embed(
                        title="Room Management",
                        description=f"Room name changed to: {self.new_name}\nDeducted: {ROOM_RENAME_PRICE} {EMOJI_COINS}",
                        color=0x2b2d31
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    await interaction.response.edit_message(embed=embed, view=self.view)

                    # Add log after successful change
                    await send_log(
                        bot,
                        "Room name changed",
                        f"**Old Name:** {room_data['name']}\n"
                        f"**New Name:** {self.new_name}\n"
                        f"**Owner:** {interaction.user.mention} (`{interaction.user.id}`)",
                        log_type="room",
                        color=0x3498DB  # Blue color for changes
                    )

                except Exception as e:
                    await interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

        modal = RenameModal()
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Change Color", style=discord.ButtonStyle.secondary)
    async def color_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Check modification permissions
        member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
        if not member_data or not member_data["is_owner"]:
            await interaction.response.send_message(
                "Only owner can change role color!",
                ephemeral=True
            )
            return

        # Check balance
        balance = bot.db.get_balance(interaction.user.id)
        if balance["coins"] < ROOM_COLOR_PRICE:
            await interaction.response.send_message(
                f"Not enough coins! Required: {ROOM_COLOR_PRICE} {EMOJI_COINS}",
                ephemeral=True
            )
            return

        class ColorModal(discord.ui.Modal, title="Change Color"):
            color = discord.ui.TextInput(
                label=f"New Color (HEX format, e.g.: #ff0000)\nCost: {ROOM_COLOR_PRICE} {EMOJI_COINS}",
                min_length=7,
                max_length=7,
                placeholder="#ffffff"
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    room_data = bot.db.get_room_data(self.view.room_id)
                    if not room_data:
                        await interaction.response.send_message("Room not found!", ephemeral=True)
                        return

                    # Check color format
                    color_str = str(self.color)
                    if not color_str.startswith('#') or len(color_str) != 7:
                        await interaction.response.send_message(
                            "Invalid color format! Use HEX format (#ff0000)",
                            ephemeral=True
                        )
                        return

                    try:
                        color_int = int(color_str[1:], 16)
                    except ValueError:
                        await interaction.response.send_message(
                            "Invalid color format!",
                            ephemeral=True
                        )
                        return

                    # Deduct coins
                    bot.db.add_currency(interaction.user.id, "coins", -ROOM_COLOR_PRICE)

                    # Change role color
                    role = interaction.guild.get_role(room_data["role_id"])
                    await role.edit(color=discord.Color(color_int))

                    embed = discord.Embed(
                        title="Room Management",
                        description=f"Role color changed to: {color_str}\nDeducted: {ROOM_COLOR_PRICE} {EMOJI_COINS}",
                        color=color_int
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    await interaction.response.edit_message(embed=embed, view=self.view)

                    # Add log after successful change
                    await send_log(
                        bot,
                        "Room role color changed",
                        f"**Room:** {room_data['name']}\n"
                        f"**Owner:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                        f"**New Color:** #{hex(color_int)[2:].upper()}",
                        log_type="room",
                        color=color_int  # Use selected color
                    )

                except Exception as e:
                    await interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

        modal = ColorModal()
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Add Co-owner", style=discord.ButtonStyle.secondary)
    async def add_coowner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Check modification permissions
        member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
        if not member_data or not member_data["is_owner"]:
            await interaction.response.send_message(
                "Only owner can assign co-owners!",
                ephemeral=True
            )
            return

        # Clear previous selects
        for item in self.children[:]:
            if isinstance(item, discord.ui.UserSelect):
                self.remove_item(item)

        # Add select for user selection
        self.action = "add_coowner"
        select = UserSelect("Select user to assign as co-owner")
        self.add_item(select)

        embed = discord.Embed(
            title="Adding Co-owner",
            description=f"@{interaction.user.name}, select\nuser you want to\nassign as co-owner",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Remove Co-owner", style=discord.ButtonStyle.secondary)
    async def remove_coowner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your room!", ephemeral=True)
            return

        # Check modification permissions
        member_data = bot.db.get_member_data(interaction.user.id, self.room_id)
        if not member_data or not member_data["is_owner"]:
            await interaction.response.send_message(
                "Only owner can remove co-owners!",
                ephemeral=True
            )
            return

        # Clear previous selects
        for item in self.children[:]:
            if isinstance(item, discord.ui.UserSelect):
                self.remove_item(item)

        # Add select for user selection
        self.action = "remove_coowner"
        select = UserSelect("Select co-owner to remove")
        self.add_item(select)

        embed = discord.Embed(
            title="Removing Co-owner",
            description=f"@{interaction.user.name}, select\nco-owner you want to\nremove",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def handle_user_select(self, interaction: discord.Interaction, selected_user: discord.User):
        print(f"[DEBUG] handle_user_select started. Action: {self.action}")
        
        if interaction.user.id != self.user.id:
            print(f"[DEBUG] User mismatch: {interaction.user.id} != {self.user.id}")
            await interaction.response.send_message("This is not your menu!", ephemeral=True)
            return

        if self.action == "give_access":
            print(f"[DEBUG] Processing give_access for user {selected_user}")
            try:
                room_data = bot.db.get_room_data(self.room_id)
                print(f"[DEBUG] Room data: {room_data}")
                
                if not room_data:
                    await interaction.response.send_message("Room not found!", ephemeral=True)
                    return

                # Check if user is already in room
                existing_member = bot.db.get_member_data(selected_user.id, self.room_id)
                print(f"[DEBUG] Existing member data: {existing_member}")
                
                if existing_member:
                    await interaction.response.send_message(
                        "This user is already in the room!",
                        ephemeral=True
                    )
                    return

                print("[DEBUG] Creating invite embed and view")
                # Create invitation
                invite_embed = discord.Embed(
                    title="Room Invitation",
                    description=(
                        f"{interaction.user.mention} invites you\n"
                        f"to join the room {room_data['name']}"
                    ),
                    color=0x2b2d31
                )
                invite_embed.set_thumbnail(url=interaction.user.display_avatar.url)

                invite_view = RoomInviteView(
                    room_name=room_data['name'],
                    inviter=interaction.user,
                    room_id=self.room_id,
                    role_id=room_data['role_id'],
                    guild_id=interaction.guild_id
                )

                print("[DEBUG] Sending initial response")
                try:
                    # First send response to original interaction
                    await interaction.response.defer(ephemeral=True)
                    
                    print("[DEBUG] Sending DM to user")
                    # Try to send invitation
                    await selected_user.send(embed=invite_embed, view=invite_view)
                    
                    print("[DEBUG] Updating original message")
                    # Update original message
                    success_embed = discord.Embed(
                        title="Room Management",
                        description=f"Invitation sent to user {selected_user.mention}",
                        color=0x2b2d31
                    )
                    success_embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    
                    # Remove select
                    for item in self.children[:]:
                        if isinstance(item, discord.ui.UserSelect):
                            self.remove_item(item)
                    
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        embed=success_embed,
                        view=self
                    )
                    
                    # Add log
                    await send_log(
                        bot,
                        "Room invitation sent",
                        f"**Room:** {room_data['name']}\n"
                        f"**Sender:** {interaction.user.mention} ({interaction.user.id})\n"
                        f"**Recipient:** {selected_user.mention} ({selected_user.id})",
                        color=0xFEE75C  # Yellow color for awaiting response
                    )
                    
                except discord.Forbidden:
                    print("[DEBUG] Failed to send DM - Forbidden")
                    await interaction.followup.send(
                        f"Failed to send invitation. User {selected_user.mention} has DMs disabled.",
                        ephemeral=True
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to send invite: {str(e)}")
                    await interaction.followup.send(
                        f"An error occurred while sending invitation: {str(e)}",
                        ephemeral=True
                    )

            except Exception as e:
                print(f"[ERROR] Error in give_access: {str(e)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

        elif self.action == "remove_access":
            # ... code for removing access ...
            pass

        elif self.action == "add_coowner":
            # ... code for adding co-owner ...
            pass

        elif self.action == "remove_coowner":
            # ... code for removing co-owner ...
            pass

@bot.tree.command(
    name="room",
    description="Manage private rooms"
)
@app_commands.guilds(bot.GUILD)
async def room(interaction: discord.Interaction):
    try:
        # Get user's room list
        rooms = bot.db.get_user_rooms(interaction.user.id, interaction.guild_id)
        
        if not rooms:
            await interaction.response.send_message(
                "You don't have private rooms!",
                ephemeral=True
            )
            return

        # Create list for room selection
        options = []
        for room_id, voice_id, role_id, name, is_owner, is_coowner in rooms:
            options.append(
                discord.SelectOption(
                    label=name,
                    value=str(room_id),
                    description="Your private room",
                    emoji="👑" if is_owner else "⭐" if is_coowner else "👤"
                )
            )

        class RoomSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="Select room to manage",
                    min_values=1,
                    max_values=1,
                    options=options
                )

            async def callback(self, interaction: discord.Interaction):
                try:
                    room_id = int(self.values[0])
                    room_data = bot.db.get_room_data(room_id)
                    
                    if not room_data:
                        await interaction.response.send_message(
                            "Room not found!",
                            ephemeral=True
                        )
                        return

                    embed = discord.Embed(
                        title="Room Management",
                        description=f"Select action for room {room_data['name']}",
                        color=0x2b2d31
                    )
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    
                    view = RoomManagerView(interaction.user, room_id)
                    await interaction.response.edit_message(embed=embed, view=view)
                except Exception as e:
                    print(f"[ERROR] Error in room select callback: {str(e)}")
                    await interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

        class RoomSelectView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=BUTTON_TIMEOUT)
                self.add_item(RoomSelect())

        embed = discord.Embed(
            title="Room Management",
            description="Select room to manage",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(
            embed=embed,
            view=RoomSelectView(),
            ephemeral=True
        )

    except Exception as e:
        print(f"[ERROR] Error in room command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(
    name="marry",
    description="Propose to another player"
)
@app_commands.describe(
    user="Select player"
)
@app_commands.guilds(bot.GUILD)
async def marry(interaction: discord.Interaction, user: discord.User):
    try:
        # Check if user is trying to marry themselves
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "You cannot marry yourself!",
                ephemeral=True
            )
            return

        # Check if user is already married
        proposer_marriage = bot.db.get_marriage(interaction.user.id)
        if proposer_marriage:
            await interaction.response.send_message(
                "You are already married!",
                ephemeral=True
            )
            return

        # Check if second user is already married
        target_marriage = bot.db.get_marriage(user.id)
        if target_marriage:
            await interaction.response.send_message(
                "This user is already married!",
                ephemeral=True
            )
            return

        # Check balance
        balance = bot.db.get_balance(interaction.user.id)
        if balance["coins"] < MARRY_PRICE:
            await interaction.response.send_message(
                f"For marriage you need {MARRY_PRICE} {EMOJI_COINS}!",
                ephemeral=True
            )
            return

        class MarryView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.button(emoji="💍", style=discord.ButtonStyle.green)
            async def accept_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                if button_interaction.user.id != user.id:
                    await button_interaction.response.send_message(
                        "This is not your proposal!",
                        ephemeral=True
                    )
                    return

                try:
                    # Deduct money
                    bot.db.add_currency(interaction.user.id, "coins", -MARRY_PRICE)
                    
                    # Register marriage
                    bot.db.add_marriage(interaction.user.id, user.id)

                    # Assign role to both users
                    love_role = button_interaction.guild.get_role(LOVE_ROLE_ID)
                    if love_role:
                        await interaction.user.add_roles(love_role)
                        await user.add_roles(love_role)

                    success_embed = discord.Embed(
                        title="💕 New Marriage!",
                        description=(
                            f"{interaction.user.mention} and {user.mention} are now married!\n"
                            f"Deducted: {MARRY_PRICE} {EMOJI_COINS}"
                        ),
                        color=0xFF69B4
                    )
                    await button_interaction.response.edit_message(embed=success_embed, view=None)

                    # Send log
                    await send_log(
                        bot,
                        "New Marriage",
                        f"**Users:** {interaction.user.mention} and {user.mention}\n"
                        f"**Cost:** {MARRY_PRICE} {EMOJI_COINS}\n"
                        f"**Role:** {love_role.mention if love_role else 'Not configured'}",
                        log_type="love",  # Changed from "room" to "love"
                        color=0xFF69B4
                    )

                except discord.Forbidden:
                    await button_interaction.response.send_message(
                        "Bot doesn't have enough permissions to assign role!",
                        ephemeral=True
                    )
                except Exception as e:
                    print(f"[ERROR] Error in marriage accept: {str(e)}")
                    await button_interaction.response.send_message(
                        f"An error occurred: {str(e)}",
                        ephemeral=True
                    )

            @discord.ui.button(emoji="💔", style=discord.ButtonStyle.red)
            async def decline_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                if button_interaction.user.id != user.id:
                    await button_interaction.response.send_message(
                        "This is not your proposal!",
                        ephemeral=True
                    )
                    return

                decline_embed = discord.Embed(
                    title="💔 Proposal Declined",
                    description=f"{user.mention} declined the proposal {interaction.user.mention}",
                    color=0xFF0000
                )
                await button_interaction.response.edit_message(embed=decline_embed, view=None)

        embed = discord.Embed(
            title="💝 Marriage Proposal",
            description=(
                f"{interaction.user.mention} makes a proposal to {user.mention}!\n"
                f"Cost: {MARRY_PRICE} {EMOJI_COINS}"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, view=MarryView())

    except Exception as e:
        print(f"[ERROR] Error in marry command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(
    name="divorce",
    description="Divorce current partner"
)
@app_commands.guilds(bot.GUILD)
async def divorce(interaction: discord.Interaction):
    try:
        # Check if there is a marriage
        marriage = bot.db.get_marriage(interaction.user.id)
        if not marriage:
            await interaction.response.send_message(
                "You are not married!",
                ephemeral=True
            )
            return

        # Get partner ID
        partner_id = marriage[1] if marriage[0] == interaction.user.id else marriage[0]
        partner = interaction.guild.get_member(partner_id)

        # Remove marriage
        bot.db.remove_marriage(marriage[0], marriage[1])

        # Remove role from both
        love_role = interaction.guild.get_role(LOVE_ROLE_ID)
        if love_role:
            await interaction.user.remove_roles(love_role)
            if partner:
                await partner.remove_roles(love_role)

        embed = discord.Embed(
            title="💔 Divorce",
            description=(
                f"{interaction.user.mention} divorces from "
                f"{partner.mention if partner else f'<@{partner_id}>'}"
            ),
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed)

        # Send log
        await send_log(
            bot,
            "Divorce",
            f"**Initiator:** {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"**Partner:** {partner.mention if partner else f'<@{partner_id}>'} (`{partner_id}`)",
            log_type="love",  # Changed from "room" to "love"
            color=0xFF0000
        )

    except Exception as e:
        print(f"[ERROR] Error in divorce command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred: {str(e)}",
            ephemeral=True
        )

@bot.tree.command(
    name="online",
    description="Shows user activity statistics"
)
@app_commands.describe(
    user="Select user (optional)"
)
@app_commands.guilds(bot.GUILD)  # Add this decorator
async def online(interaction: discord.Interaction, user: discord.User = None):
    try:
        target_user = user if user else interaction.user
        stats = bot.db.get_user_stats(target_user.id, interaction.guild.id)
        
        # Convert seconds to hours, minutes and seconds
        total_seconds = stats["voice_time"]
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        embed = discord.Embed(
            title="User Statistics",
            description=target_user.mention,
            color=0x2b2d31
        )
        
        embed.add_field(
            name="Time in voice channels",
            value=f"```{hours:02d}:{minutes:02d}:{seconds:02d}```",
            inline=False
        )
        
        embed.add_field(
            name="Messages sent",
            value=f"```{stats['messages']}```",
            inline=False
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"[ERROR] Error in online command: {str(e)}")
        await interaction.response.send_message(
            f"An error occurred: {str(e)}",
            ephemeral=True
        )


async def main():
    async with bot:
        await bot.start(BOT_TOKEN)  # Use token from config

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
    except Exception as e:
        print(f"An error occurred: {e}") 