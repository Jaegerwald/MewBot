import discord
import os, asyncio
import random, json, re
import traceback
from dotenv import load_dotenv

import util

load_dotenv()
ADMINS = os.getenv("ADMINS").split(",")
for i in range(0, len(ADMINS)):
    ADMINS[i] = int(ADMINS[i])
BANNED_CHANNELS = os.getenv("BANNED_CHANNELS").split(",")
for i in range(0, len(BANNED_CHANNELS)):
    BANNED_CHANNELS[i] = int(BANNED_CHANNELS[i])

responses = []
blocked = []

with open("block.json", "r") as block_file:
    blocked = json.loads(block_file.read())

# ik this code isnt commented but this basically tokenizes the responses :3
def load_responses():
    responses.clear()

    with open("data.json", "r", encoding="utf-8") as data_file:
        data = json.loads(data_file.read())

    for response in data["responses"]:
        response = [
            util.bool_from_dict_or_false(response, "strict"),
            util.list_or_str_to_list(util.empty_list_fallback(response, "trigger")),
            util.list_or_str_to_list(util.empty_list_fallback(response, "trigger_end")),
            util.list_or_int_randint_function(response["happiness"]),
            util.list_or_int_randint_function(response["length"]),
            util.list_or_str_to_list(util.empty_list_fallback(response, "modifiers"))
        ]
        responses.append(response)
class Client(discord.Client):
    async def on_ready(self):
        print("Logged on as", self.user)

    async def reload_data(self, ctx):
        global responses, blocked
        
        message = await ctx.send("-# <a:mew_throbber:1353825035273371729> **Reloading...**")

        backup = responses.copy()
        try:
            with open("block.json", "r") as block_file:
                blocked = json.loads(block_file.read())
            load_responses()
            await message.edit(content="<:mew_check:1353825037966377001> **Reload Succeeded**")
        except Exception as e:
            responses = backup
            await message.edit(content="<:mew_cross:1353825036460363818> **Reload Failed**\n```\n" + traceback.format_exc() + "\n```")

        
    async def toggle_blocked_status(self, ctx, user):
        global blocked
        
        with open("block.json", "r+") as block_file:
            blocked = json.loads(block_file.read())
            if user in blocked:
                blocked.remove(user)
                success_message = await ctx.send(content="<:mew_check:1353825037966377001> **Responses turned on for <@" + str(user) + ">**")
                block_file.seek(0)
                block_file.truncate()
                block_file.write(json.dumps(blocked))
                await asyncio.sleep(5)
                await success_message.delete()
            else:
                blocked.append(user)
                success_message = await ctx.send(content="<:mew_cross:1353825036460363818> **Responses turned off for <@" + str(user) + ">**")
                block_file.seek(0)
                block_file.truncate()
                if json.dumps(blocked) == "":
                    block_file.write("[]")
                else:
                    block_file.write(json.dumps(blocked))
                await asyncio.sleep(5)
                await success_message.delete()
    
    async def purge_messages(self, ctx, amount):
        message = await ctx.send("-# <a:mew_throbber:1353825035273371729> **Purging " + str(amount) + " Messages...**")
        purged = 0
        index = 0
        try:
            async for ctx_message in ctx.history(limit=200):
                if ctx_message.author.id == self.user.id and amount > 0 and index != 0:
                    amount -= 1
                    purged += 1

                    await ctx_message.delete()
                index += 1

            success_message = await message.edit(content="<:mew_check:1353825037966377001> **Purged " + str(purged) + " Messages Successfully**")
            await asyncio.sleep(5)
            await success_message.delete()
        except Exception as e:
            error_message = await message.edit(content="<:mew_cross:1353825036460363818> **Purge Failed**\n```\n" + traceback.format_exc() + "\n```")
            await asyncio.sleep(5)
            await error_message.delete()

    async def on_message(self, message):
        global ping_sillybot
    
        if message.author == self.user:
            return
        
        if message.author.id in ADMINS and message.content.startswith("&") and len(message.content.split(" ")) < 3:
            match message.content[1:].split(" ")[0]:
                case "reload":
                    await self.reload_data(message.channel)
                    return
                case "tokens":
                    token_lists = [responses[i:i+5] for i in range(0,len(responses),5)]
                    for token_list in token_lists:
                        result = "```hs\n"
                        for token in token_list:
                            result += str(token) + "\n"
                        result += "```"
                        await message.channel.send(result)
                    return
                case "purge" | "purrge":
                    try:
                        message_count = int(message.content.split(" ")[1])
                    except:
                        error_message = await message.channel.send("<:mew_cross:1353825036460363818> **Purge Failed, Invalid Argument**")
                        await asyncio.sleep(5)
                        await error_message.delete()
                        return

                    await self.purge_messages(message.channel, message_count)
                    return

        if message.content == "&ignore":
            await self.toggle_blocked_status(message.channel, message.author.id)
            return

        message.content = message.content.lower()
        
        if message.author.id in blocked:
            return
        if message.channel.id in BANNED_CHANNELS:
            return

        for token in responses:
            trigger_match = False
            end_match = True

            for trigger_end in token[2]:
                end_match = message.content.endswith(trigger_end)

            for trigger in token[1]:
                trigger_match = token[0] and re.search("\\b" + trigger + "\\b", message.content) and end_match or token[0] == False and re.search("\\b" + trigger, message.content) and end_match
                if trigger_match:

                    result = util.generate_meow(token[3](), token[4]())

                    for modifier in token[5]:
                        match modifier:
                            case "questions":
                                result += "?" * random.randrange(1, 3)
                            case "question":
                                result += "?"
                            case "exclamations":
                                result += "!" * random.randrange(1, 3)
                            case "exclamation":
                                result += "!"
                            case "ellipsis":
                                result += " " + "." * random.randrange(2, 4)
                            case "pre_ellipsis":
                                result = "." * random.randrange(2, 4) + result
                            case "uppercase":
                                result = result.upper()
                            case "evil":
                                result = result.replace(":3", ">:3")
                            case "enforce_rs":
                                result = result.replace("m", "mr")
                                result = result.replace("r", "r" * random.randrange(2,5))

                    await message.channel.send(result)

            if trigger_match:
                break

intents = discord.Intents.default()
intents.message_content = True

load_responses()

client = Client(intents=intents)
client.run(os.getenv("TOKEN"))