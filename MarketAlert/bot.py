import discord # Discord API
import json    # json
import csv

""" 
MarketAlert 是 CodeRyo 團隊基於 investpy 開發應用於 Discord 上的金融提醒機器人，
開源LICENSE：MIT License
MarketAlert is a financial alert bot developed by the CodeRyo based on investpy for use on Discord.
open source LICENSE: MIT License
""" 

intents=discord.Intents().all()     # 獲取所有的 Intents 對象
intents.message_content = True      # 允許讀取消息內容

# 讀取 config.json 的設定檔案
with open("config.json") as f:
    config=json.load(f)
    token=config['discord_bot_token']

# Discord 機器人變數設置
bot = discord.Client(intents=intents)

# Discord 機器人狀態設置
@bot.event
async def on_ready():
    print('目前登入身份：',bot.user)
    game = discord.Game('MarketAlert')
    # discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
    await bot.change_presence(status=discord.Status.online, activity=game)

    data = ""

    with open('./data/calendar.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # 將行添加到列表中
            data += ",".join(row) + "\n"
        print(data)

    await bot.get_guild(779321275730362379).get_thread(1103885928012988417).send(data)
    # await discord.utils.get(bot.get_all_channels(), name='bot').send('MarketAlert 已上線' )

# Discord 機器人 TOKEN
bot.run(token)