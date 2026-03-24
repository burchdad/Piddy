---
name: discord-bot
description: Build Discord bots with discord.py — commands, events, embeds, slash commands, and server management
---

# Discord Bot Development

## Setup

```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

bot.run("TOKEN")
```

## Slash Commands (Application Commands)

```python
from discord import app_commands

@bot.tree.command(name="greet", description="Say hello")
async def greet(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello, {name}!")

# Sync commands on ready
@bot.event
async def on_ready():
    await bot.tree.sync()
```

## Embeds

```python
embed = discord.Embed(
    title="Status Report",
    description="All systems operational",
    color=discord.Color.green(),
)
embed.add_field(name="Uptime", value="99.9%", inline=True)
embed.add_field(name="Latency", value="42ms", inline=True)
embed.set_footer(text="Piddy Bot")
await ctx.send(embed=embed)
```

## Event Handlers

```python
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Process commands after custom handling
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention}!")
```

## Cogs (Modular Commands)

```python
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
```

## Key Patterns
- Use `intents` to declare what events you need (message content requires privileged intent)
- Prefer slash commands over prefix commands for public bots
- Use `discord.ui.View` and `discord.ui.Button` for interactive components
- Rate limits: respect Discord's rate limits, use `asyncio.sleep` when needed
- Permissions: check `commands.has_permissions()` or `app_commands.checks`
- Error handling: `@bot.event async def on_command_error(ctx, error)`
