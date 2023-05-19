import discord, json, csv, datetime, subprocess, asyncio
from discord.ext import tasks

print(f"[Info] Running...")

"""
MarketAlert 是 CodeRyo 團隊基於 investpy 開發應用於 Discord 上的金融提醒機器人，
開源LICENSE：MIT License
MarketAlert is a financial alert bot developed by the CodeRyo based on investpy for use on Discord.
open source LICENSE: MIT License
"""

with open("config.json") as f:
    config = json.load(f)
    token = config['discord_bot_token']

bot = discord.Client(intents=discord.Intents().all())
reminders = []
msg_list = ""

class Restarter:
    def __init__(self):
        print(f"[Info] Restarter is running...")
        self.restart()
        self.restart_loop.start()

    def restart(self):
        print(f"[Info] Restarting tasks...")
        for reminder in reminders:
            reminder.stop()
        reminders.clear()
        run_tasks()

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=8))))
    async def restart_loop(self):
        self.restart()


class Reminder:
    def __init__(self, target_datetime, event_datetime, event_info):
        self.target_datetime = target_datetime
        self.event_datetime = event_datetime
        self.event_info = event_info
        self.task = self.remind_me

    def start(self):
        self.task.start()

    def stop(self):
        self.task.cancel()

    @tasks.loop(seconds=60)
    async def remind_me(self):
        global msg_list
        if datetime.datetime.now() >= self.target_datetime:
            message = f"```Now: {datetime.datetime.now()}\nAlert: {self.target_datetime}\nEvent: {self.event_datetime}\nName: {self.event_info[7]}\nZone: {self.event_info[4]}\nCurrency: {self.event_info[5]}\nImportance: {self.event_info[6]}\nActual: {self.event_info[8]}\nForecast: {self.event_info[9]}\nPrevious: {self.event_info[10]}```\n"
            while len(msg_list) + len(message) > 2000:
                await asyncio.sleep(1)
            if len(msg_list) + len(message) <= 2000:
                msg_list += message
                print(message)
                self.stop()

class Sendmsg:
    def __init__(self):
        self.send_msg.start()

    @tasks.loop(seconds=1)
    async def send_msg(self):
        global msg_list
        if len(msg_list) > 0:
            await bot.get_guild(779321275730362379).get_thread(1103885928012988417).send(msg_list)
            msg_list = ""

def run_tasks():
    process = subprocess.Popen(["python", "main.py"])
    process.wait()

    with open('./data/calendar.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if row[3] == "Tentative":
                datetime_str = row[2] + "00:00"
                event_datetime = datetime.datetime.strptime(datetime_str, "%d/%m/%Y%H:%M")
            else:
                datetime_str = row[2] + row[3]
                event_datetime = datetime.datetime.strptime(datetime_str, "%d/%m/%Y%H:%M")
            target_datetime = event_datetime - datetime.timedelta(minutes=10)
            reminder = Reminder(target_datetime, event_datetime, row)
            reminders.append(reminder)

    for reminder in reminders:
        reminder.start()

@bot.event
async def on_ready():
    print('目前登入身份：', bot.user)
    game = discord.Game('MarketAlert')
    await bot.change_presence(status=discord.Status.online, activity=game)
    await bot.get_guild(779321275730362379).get_thread(1103885928012988417).send("已上線")
    Restarter()
    Sendmsg()

bot.run(token)