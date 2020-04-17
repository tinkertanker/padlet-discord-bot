import discord
from discord.ext import commands
import asyncio
import requests
from bs4 import BeautifulSoup
import json
import datetime as dt
import time
from dotenv import load_dotenv
import os


load_dotenv()
token = os.getenv('TOKEN')
padlet_appid = os.getenv('APPID')


with open("config_main.json") as json_file:
    vals = json.load(json_file)
padlet_url = vals['Padlet']['URL']
t_delay = vals['Discord']['Time between loop']  # in minutes
bot_call = vals['Discord']['Bot Mention']
valid_channels = vals['Discord']['Channels']['allowed']
posting_channel = vals['Discord']['Channels']['posting-channel']


client = commands.Bot(command_prefix=bot_call)


def get_author_name(author_id):
    author_response = requests.get(
        f'https://padlet.com/api/0.9/users/public_profile?user_id={author_id}',
        headers={'Content-Type': 'application/json',
                 'App-Id': padlet_appid})
    if author_response.status_code == 200:
        author_name = author_response.json()['data'][0]['name']
    else:
        author_name = "Anonymous"
    return author_name

async def embed_generator(channel, in_list):
    for data in in_list:
        author_name = get_author_name(data['author_id'])
        post_title = data['subject']
        post_body = BeautifulSoup(data['body'], "html.parser").get_text('\n')
        if len(post_body) > 200:
            post_body = post_body[:196] + "..."
        post_url = padlet_url + "/wish/" + str(data['id'])

        embed = discord.Embed(title=post_title, url=post_url, color=0x29ad6f)
        embed.set_author(name=author_name)
        if data['attachment'] != "":
            attach_name = str(data['attachment'])[str(data['attachment']).rfind('/') + 1:]
            embed.description = f"[{attach_name}]({data['attachment']})"
            if attach_name[-4:] in ['.png', '.jpg', '.gif', '.svg', 'jpeg']:
                embed.set_thumbnail(url=data['attachment'])
        if len(post_body) > 0:
            embed.add_field(name=author_name + " wrote:", value=post_body, inline=False)
        embed.timestamp = data['updated_at']
        await channel.send(embed=embed)


async def background_timer():
    await client.wait_until_ready()
    channel = client.get_channel(posting_channel)
    while not client.is_closed():
        start = time.time()
        response = requests.get(
            f'https://padlet.com/api/0.9/public_posts?padlet_url={padlet_url}',
            headers={'Content-Type': 'application/json',
                     'App-Id': padlet_appid})
        if response:
            if response.status_code == 200:
                extract_data = response.json()['data']
                relevant_data = []
                for post in extract_data:
                    post['updated_at'] = dt.datetime.strptime(post['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if post['updated_at'] > (dt.datetime.utcnow() - dt.timedelta(minutes=t_delay)):
                        relevant_data.append(post)
                if len(relevant_data) > 5:
                    num_posts = len(relevant_data)
                    contrib_list = list(set([get_author_name(x['author_id']) for x in relevant_data]))
                    if len(contrib_list) > 3:
                        contrib_str = ', '.join(contrib_list[0:2])
                        contrib_str += ", and more."
                    else:
                        contrib_str = ', '.join(contrib_list[:-1])
                        try:
                            contrib_str[-2] += " and "
                        except:
                            print("list index probably out of range")
                        contrib_str = contrib_str + contrib_list[len(contrib_list)-1] + "."
                    await channel.send(content=f"{num_posts} new posts have been made by {contrib_str}")
                    trunc_data = relevant_data[:3]
                    await embed_generator(channel, trunc_data)
                    await channel.send(content="... and more! \n All posts are on https://padlet.tk.sg/swift2020submissions")
                elif len(relevant_data) > 0:
                    await embed_generator(channel, relevant_data)
            else:
                print("There is no content, or the endpoint has permanently moved.")
                print(response.status_code)
        else:
            print("There has been an error in processing this request.")
            print(response.status_code)
        n_delay = (t_delay * 60) - (time.time() - start)
        await asyncio.sleep(n_delay)  # asyncio.sleep takes delay in seconds


async def submissions_counter():
    response = requests.get(f'https://padlet.com/api/0.9/public_posts?padlet_url={padlet_url}',
                            headers={'Content-Type': 'application/json',
                                     'App-Id': padlet_appid})
    if response:
        if response.status_code == 200:
            extract_data = response.json()['data']
            user_list = [x['author_id'] for x in extract_data]
            submissions_count = len(set(user_list))
            print(submissions_count)
            return submissions_count
        else:
            print("There is no content, or the endpoint has permanently moved.")
            print(response.status_code)
    else:
        print("There has been an error in processing this request.")
        print(response.status_code)


@client.command(name="hello", description="Salutations, from your best friend Paddie to you :)")
async def hello(ctx):
    "Salutations, from your best friend Paddie to you :)"
    if str(ctx.channel) in valid_channels:
        await ctx.send("Hi!")
    else:
        await ctx.send("I am not welcome here :(")


@client.command(aliases=['submissions'], name="submission",
                description="Gives number of unique users who have posted on the padlet")
async def _submissions(ctx):
    "Gives number of unique users who have posted on the padlet"
    if str(ctx.channel) in valid_channels:
        submissions_count = await submissions_counter()
        await ctx.send(f"""Number of submissions: {submissions_count}""")


client.loop.create_task(background_timer())
client.run(token)
