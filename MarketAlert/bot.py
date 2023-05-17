import discord, json, csv, datetime, subprocess, logging
from discord.ext import tasks

print(f"[Info] Running...")

"""
MarketAlert 是 CodeRyo 團隊基於 investpy 開發應用於 Discord 上的金融提醒機器人，
開源LICENSE：MIT License
MarketAlert is a financial alert bot developed by the CodeRyo based on investpy for use on Discord.
open source LICENSE: MIT License
"""

class Restarter:
    def __init__(self):
        print(f"[Info] Restarter is running...")
        self.restart.start()

    # 設定重啟任務在午夜執行（當地時間）
    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=8))))
    async def restart(self):
        await restart_tasks()

class Reminder:
    def __init__(self, target_datetime, event_datetime, event_name):
        self.target_datetime = target_datetime
        self.event_datetime = event_datetime
        self.event_name = event_name
        self.task = self.remind_me

    def start(self):
        log_msg(f"已新增事件，目前時間為 {datetime.datetime.now()}，預計提醒時間為 {self.target_datetime}，事件時間為 {self.event_datetime}，名稱：{self.event_name}")
        self.task.start()

    def stop(self):
        self.task.cancel()

    # 每60秒執行一次 remind_me 任務
    @tasks.loop(seconds=60)
    async def remind_me(self):
        if datetime.datetime.now() >= self.target_datetime:
            log_msg(f"事件已結束，目前時間為 {datetime.datetime.now()}，預計提醒時間為 {self.target_datetime}，事件時間為 {self.event_datetime}，名稱：{self.event_name}")
            self.stop()

# 設定日誌檔案名稱及層級
log_filename = f"log-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO)

# 設定 Discord 機器人的 intents
intents = discord.Intents().all()
intents.message_content = True

# 從 JSON 檔案中讀取設定
with open("config.json") as f:
    config = json.load(f)
    token = config['discord_bot_token']

bot = discord.Client(intents=intents)

reminders = []

def log_msg(msg):
    # 輸出訊息至控制台並記錄到日誌檔案中
    print(f"{datetime.datetime.now()} - {msg}")
    logging.info(f"{datetime.datetime.now()} - {msg}")

def run_tasks():
    # 執行子進程執行 main.py 腳本
    process = subprocess.Popen(["python", "main.py"])
    process.wait()

    # 讀取 CSV 檔案中的事件資料並創建 Reminder 物件
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
            event_name = row[7]
            target_datetime = event_datetime - datetime.timedelta(minutes=10)
            reminder = Reminder(target_datetime, event_datetime, event_name)
            reminders.append(reminder)

    # 開始所有的提醒
    for reminder in reminders:
        reminder.start()

async def restart_tasks():
    log_msg(f"重新啟動任務中...")
    # 停止所有的提醒
    for reminder in reminders:
        reminder.stop()
    reminders.clear()
    run_tasks()

@bot.event
async def on_ready():
    print('目前登入身份：', bot.user)
    game = discord.Game('MarketAlert')
    await bot.change_presence(status=discord.Status.online, activity=game)
    # await bot.get_guild(779321275730362379).get_thread(1103885928012988417).send("已上線")
    Restarter()
    await restart_tasks()

bot.run(token)