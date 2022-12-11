import discord
import asyncio
from revChatGPT.revChatGPT import Chatbot
import typing
import functools
import nest_asyncio
import time

#==============================[這裡填入資料]==============================
TOKEN = ''
Email = '' #OpenAI 帳號
Password = ''
channel_id = 
loading = "" #https://cdn.discordapp.com/attachments/938085805182844949/1050810307947274372/SH_Loading_Discord.gif
tick = "" #https://cdn.discordapp.com/attachments/938085805182844949/1050810307683041310/1040573768650731551.png
cross = "" #https://cdn.discordapp.com/attachments/938085805182844949/1050810307326529586/1040573770320052235.png
timeout_sec = 600 #等待OpenAI的秒數
#==============================[這裡填入資料]==============================

class CaptchaSolver:
    @staticmethod
    def solve_captcha(raw_svg):
        # Get the SVG
        svg = raw_svg
        # Save the SVG
        with open("captcha.svg", "w") as f:
            print("Captcha saved to captcha.svg")
            f.write(svg)
        # Get input
        solution = input("Please solve the captcha: ")
        # Return the solution
        return solution

nest_asyncio.apply()
intents = discord.Intents.all()
client = discord.Client(intents=intents)
config = {
    "email": Email,
    "password": Password,
}

chatbot = Chatbot(config,conversation_id=None,request_timeout=600,captcha_solver=CaptchaSolver())

def current_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

#Run sync def in async
async def NotBlocking(SendMessage: typing.Callable, *args, **kwargs) -> typing.Any:
    func = functools.partial(SendMessage, *args, **kwargs)
    return await client.loop.run_in_executor(None, func)

@client.event
async def on_message(message):
    #排除自己的訊息，避免無限循環
    if message.author == client.user:
        return
    if message.channel.id == channel_id:
        await message.add_reaction(loading)
        print("==============================[INFO]==============================")
        print("[INFO] "+"["+current_time()+"] "+"訊息作者: "+message.author.name+"#"+str(message.author.discriminator)+" Discord ID: "+str(message.author.id))
        print("[INFO] "+"["+current_time()+"] "+"訊息內容: "+message.content)
        print("[INFO] "+"["+current_time()+"] "+"正在傳送訊息給OpenAI")
        
        try:
            reply = asyncio.run(NotBlocking(chatbot.get_chat_response,message.content, output="text",))['message']
            print("==============================[SUCCESS]==============================")
            print("[INFO] "+"["+current_time()+"] "+"已成功傳送訊息給OpenAI -- Done")
            print("[INFO] "+"["+current_time()+"] "+"字數: ",len(reply))
            await message.add_reaction(tick)
            #print(reply)
        except Exception as e: 
            print("==============================[ERROR]==============================")
            e = str(e)
            reply = "OpenAI沒有回答這個問題呢,再試一次看看? " + "["+e+"]"
            print("[ERROR] "+"["+current_time()+"] "+"傳送訊息給OpenAI失敗 -- Error")
            print("[ERROR] "+"["+current_time()+"] "+e)
            chatbot.reset_chat()
            chatbot.refresh_headers()
            chatbot.refresh_session()
            await message.remove_reaction(loading,client.user)
            await message.add_reaction(cross)

        reply_len = int(len(reply))
        if (reply_len/1000) > (reply_len//1000):
            reply_len=reply_len+1000
        for i in range (0,reply_len//1000):
            await asyncio.sleep(0.6)
            replymsg = reply[i*1000:i*1000+1000]
            await message.reply(replymsg)
        await message.remove_reaction(loading,client.user)

@client.event
async def on_ready():
    print("\033[H\033[J", end="")
    print('已登入機器人: ')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)