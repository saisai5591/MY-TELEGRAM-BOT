import random
import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 設定 Log 系統，用嚟幫你睇清楚 Bot 運行時有無報錯
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 恐怖湯底資料庫 (你可以喺呢度加新故事)
puzzles = [
    {"story": "深夜，畫家獨自喺工作室畫緊一幅全家福。佢畫完媽媽，轉身去飲水，返嚟發現畫入面媽媽嘅表情變咗，變成咗驚恐嘅尖叫。佢以為係自己記錯，繼續畫埋爸爸同細佬。點知每畫完一個，嗰個人物嘅表情都會變，最後佢畫埋自己，成幅畫變成咗佢地滅門慘案當晚嘅畫面。點解？", "answer": "畫家其實喺畫呢幅畫嘅一週前就滅門慘案中死咗。佢係倖存者，但因為受唔住刺激精神崩潰死喺畫室。佢靈魂以為仲未畫完，畫入面嘅「驚恐」係佢死前重現緊全家人被殺嘅絕望記憶。", "keywords": {"鬼": "唔係鬼，畫家係人。", "死": "係，全家人都死咗。", "兇手": "係，畫家要搵出兇手。", "回憶": "係，畫緊嘅係佢死前嘅記憶。"}},
    # ... (其他湯底同上面一樣)
]

MAX_ATTEMPTS = 25 # 設定最多可以猜幾多次

# 開始遊戲函數
async def start_game(update, context, puzzle):
    # 使用 chat_data：確保同一個 Group/對話入面嘅人可以共享進度
    context.chat_data['current_game'] = puzzle
    context.chat_data['attempts'] = MAX_ATTEMPTS
    context.chat_data['found_keys'] = set()
    await update.message.reply_text(f"【全新恐怖海龜湯】：\n{puzzle['story']}\n\n你有 {MAX_ATTEMPTS} 次機會！/reveal 可揭曉。")

# 處理 /play 指令
async def play(update, context):
    game = random.choice(puzzles)
    await start_game(update, context, game)

# 處理 /next 指令
async def next_puzzle(update, context):
    game = random.choice(puzzles)
    await update.message.reply_text("轉下一個恐怖故事...")
    await start_game(update, context, game)

# 處理 /reveal 指令 (揭曉答案)
async def reveal(update, context):
    game = context.chat_data.get('current_game')
    if not game:
        await update.message.reply_text("未開始遊戲，請輸入 /play。")
        return
    await update.message.reply_text(f"【答案揭曉】：\n{game['answer']}")
    context.chat_data['current_game'] = None # 清空遊戲狀態

# 處理玩家提問 (核心邏輯)
async def check_question(update, context):
    game = context.chat_data.get('current_game')
    if not game: return # 如果無遊戲進行中，直接結束
    
    context.chat_data['attempts'] -= 1 # 扣除一次機會
    remaining = context.chat_data['attempts']
    
    if remaining < 0:
        await update.message.reply_text("機會用盡！請用 /next 開下一個湯。")
        return
    
    user_text = update.message.text
    found_key = None
    
    # 檢查輸入嘅問題入面有無關鍵詞
    for keyword, response in game['keywords'].items():
        if keyword in user_text:
            found_key = keyword
            context.chat_data['found_keys'].add(keyword)
            await update.message.reply_text(f"{response} (剩餘: {remaining})")
            break 
    
    # 提示玩家進度
    if len(context.chat_data['found_keys']) >= (len(game['keywords']) - 1) and not found_key:
         await update.message.reply_text("你已經掌握大部分真相，仲差 1-2 個關鍵細節！")
    elif not found_key:
        await update.message.reply_text(f"不相關。(剩餘: {remaining})")

# 主程式入口
if __name__ == '__main__':
    # 從 Render 的環境變數取得 TOKEN
    TOKEN = os.getenv('8806982911:AAGtDR-qiyKRJlSl8mghC484UcR3qzub55M')
    
    # 初始化 Bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    # 設定指令處理器 (Handlers)
    app.add_handler(CommandHandler('play', play))
    app.add_handler(CommandHandler('next', next_puzzle))
    app.add_handler(CommandHandler('reveal', reveal))
    
    # 處理普通文字訊息 (用嚟玩海龜湯)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_question))
    
    print("Bot 已經啟動！")
    app.run_polling()
