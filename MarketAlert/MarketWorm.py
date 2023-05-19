import datetime, os, investpy

""" 
MarketAlert 是 CodeRyo 團隊基於 investpy 開發應用於 Discord 上的金融提醒機器人，
開源LICENSE：MIT License
MarketAlert is a financial alert bot developed by the CodeRyo based on investpy for use on Discord.
open source LICENSE: MIT License
""" 

# =============================================================================
# 檢驗存檔路徑
# =============================================================================
try:
    path_save = os.path.join(os.getcwd(), 'data')
    
    if os.path.exists(path_save) == False: # 檢驗有無存檔資料夾
        os.makedirs(path_save) # 沒有就建立
except Exception as e:
    print(path_save, '路徑出現問題')
    
# =============================================================================
# 撈取資料
# =============================================================================
try:
    # 參數設定
    importances = ['high', 'medium', 'low']
    time_zone = 'GMT +8:00'
    from_date = datetime.datetime.today().strftime('%d/%m/%Y')
    to_date = (datetime.datetime.today() + datetime.timedelta(days=7)).strftime('%d/%m/%Y')

    # 使用api取得資料
    print('[MarketWorm] Running...')
    calendar = investpy.economic_calendar(importances=importances, time_zone=time_zone, from_date=from_date, to_date=to_date)

    print('[MarketWorm] Done...')
    # 資料過濾(過濾沒有重要程度的資料)
    calendar = calendar[calendar['importance'].values != None]

    # 儲存資料
    path = os.path.join(os.getcwd(), 'data', 'calendar.csv')
    calendar.to_csv(path)
except Exception as e:
    print('ERROR:' ,e)