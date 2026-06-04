import random
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 1. 配置區 - 請確保你的環境變數已設置 TOKEN 和 GROQ_API_KEY
# 如果你係直接喺 Code 填 Key，就將 os.getenv(...) 換成 '你的Key'
TOKEN = os.getenv('8806982911:AAGtDR-qiyKRJlSl8mghC484UcR3qzub55M', '填入你的_TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('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', '填入你的_GROQ_API_KEY')

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# 2. 十個完整長篇故事庫
puzzles = [
    {"story": "深夜，著名畫家獨自喺工作室畫緊一幅全家福。佢畫完媽媽，轉身去飲水，返嚟發現畫入面媽媽嘅表情變咗，變成咗驚恐嘅尖叫。佢以為係自己記錯，繼續畫埋爸爸同細佬。點知每畫完一個，嗰個人物嘅表情都會變，最後佢畫埋自己，成幅畫變成咗一副地獄圖。點解會發生咁詭異嘅事？", "answer": "畫家其實喺一週前經歷咗滅門慘案，佢係唯一倖存者，但因為受唔住極大刺激，精神徹底崩潰，死喺畫室入面。嗰幅「全家福」係佢精神錯亂下，將家人臨死前嘅驚恐記憶用畫筆重現出嚟，最後嗰幅圖係佢自己自殺時嘅絕望寫照。"},
    {"story": "男人每晚 12 點都會收到一通電話，入面傳嚟佢老婆嘅聲音：「我好凍，快啲返嚟接我。」男人每次都心痛欲絕，但佢始終無去接。直到有一晚，佢終於忍唔住，揸車去咗老婆講嘅地方，結果佢失蹤咗。點解？", "answer": "三年前，男人同老婆揸車行經湖邊撞咗落去。老婆被困車廂臨死前打電話求救，但男人自己爬咗上岸生存。三年間佢一直活喺悔疚。嗰晚男人去到湖邊，見到全身濕透嘅老婆（靈體），佢崩潰主動揸車衝入湖入面去「接」老婆，兩人喺湖底變成怨偶。"},
    {"story": "一個男仔好鍾意玩鏡子，有一晚 3 點，佢發現鏡入面嘅自己無跟住佢郁，而係對住佢詭異一笑。第二日，佢失蹤咗。屋企人發現佢鎖咗喺房入面，已經氣絕身亡，死狀係好似自己掐死自己。點解？", "answer": "鏡子係通往「倒影世界」嘅門。嗰晚 3 點替身同男仔交換靈魂，男仔被困入鏡入面。替身為咗徹底抹殺男仔意識，控制住個身軀，令男仔自己掐死自己。"},
    {"story": "商場入面有個假人模特兒，每晚保安巡邏都會覺得佢換咗位置。有一晚，保安發現佢手入面多咗把染血嘅刀，而嗰晚之後，保安再無出現過。點解？", "answer": "呢個假人係一個被活生生封喺水泥入面嘅連續殺人狂，怨氣太重可以郁動。保安好奇觸摸假人，假人將佢殺死，並剝皮將佢整成新嘅假人模型放喺展示位。"},
    {"story": "深夜開車經過一條荒廢隧道，車入面原本得司機一個人。當車駛到隧道一半時，司機從倒後鏡見到後座坐咗一個長髮女人。佢嚇到停低車，回頭一睇，後座咩都無。但當佢再望倒後鏡，個女人仲喺度，而且慢慢向佢靠近。點解？", "answer": "司機早喺隧道入口撞死咗。隧道係陽間同陰間交界。後座嗰個係勾魂使者，化作前女友模樣嚟帶佢走。現實世界架車早已撞毀，司機只係靈魂仲以為開緊車。"},
    {"story": "攝影師鍾意幫人影相。有一日，佢沖曬出一張舊照片，入面影到佢自己身後有一個黑影。之後佢無論去邊，只要影相，相入面一定會有嗰個黑影。最後，佢喺相入面見到自己被殺嘅畫面。點解？", "answer": "黑影係靠吸食生命為生嘅邪靈。閃光燈撕裂咗現實同靈界，邪靈依附喺相度剝削佢陽壽。最後一張相係邪靈預告殺佢嘅畫面，嗰日之後攝影師就被殺。"},
    {"story": "醫院入面有一間長期鎖住嘅病房。深夜，當值護士成日聽到入面有人開心地笑，仲有玩具車喺地下跑嘅聲音。護士開門睇，入面咩都無。點解？", "answer": "病房以前係小兒科，患絕症嘅細路死咗後，靈魂純真唔知自己死咗，以為仲住喺醫院，所以隱形繼續喺入面玩玩具。"},
    {"story": "女孩得到一個精緻嘅洋娃娃屋，入面嘅裝修同佢屋企一模一樣。有一日，佢發現洋娃娃屋入面嘅床上，瞓咗一具細小嘅屍體。女孩打開洋娃娃屋想攞出嚟，結果佢當場嚇到休克。點解？", "answer": "娃娃屋係詛咒連結，娃娃屋發生咩事，現實屋都會發生。屍體係女孩靈體模型。打開屋嗰陣，佢感受到自己嘅死亡過程，原來佢肉身早喺屋企被入屋盜賊殺咗，靈魂被困入去。"},
    {"story": "巴士司機每晚載客，有一晚，車上明明坐滿咗 11 個人，但當佢望返閉路電視，入面永遠只係顯示得 10 個人。最後嗰個乘客，司機從來無見過佢落車。點解？", "answer": "巴士路線曾發生嚴重車禍，全車無生還。司機係倖存者，腦部受創產生集體幻覺。第 11 個人係死者嘅靈魂，閉路電視影唔到，佢亦永遠無落車因為佢唔知自己死咗。"},
    {"story": "一間屋被焊死咗 20 年。警方因為收到異味投訴，將鐵門割開。入面乾淨整潔，餐枱上面擺好晒飯菜，好似啱啱煮好咁。屋主坐喺梳化上面已經化成白骨，但佢嘅頭髮長到蓋住成個梳化。點解？", "answer": "屋主係邪教徒，進行永生儀式絕食 49 日。儀式出錯，佢變詛咒容器，飯菜吸收生氣保持新鮮，頭髮係靈魂橋樑，死後依然生長試圖編織新肉身。"}
]

# 3. 核心遊戲控制邏輯
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("歡迎來到海龜湯！輸入 /play 開始遊戲。")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = random.choice(puzzles)
    context.chat_data.update({'game': game, 'history': [], 'attempts': 20})
    await update.message.reply_text(f"【新遊戲開始】：\n{game['story']}\n\n你有 20 次提問機會，請開始推理！")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'game' not in context.chat_data:
        return
    
    # 次數扣減
    context.chat_data['attempts'] -= 1
    rem = context.chat_data['attempts']

    if rem < 0:
        await update.message.reply_text(f"【機會用盡】：真相係：{context.chat_data['game']['answer']}\n輸入 /play 重新開始。")
        context.chat_data.clear()
        return

    # AI 判斷與生成
    game = context.chat_data['game']
    messages = [
        {"role": "system", "content": f"故事：{game['story']}\n真相：{game['answer']}\n設定：你係專業海龜湯判官。回答必須長篇、懸疑。除「講真相」外，只答係/唔係/無關係。剩餘機會：{rem}。"}
    ] + context.chat_data.get('history', []) + [{"role": "user", "content": update.message.text}]

    try:
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        reply = completion.choices[0].message.content
        context.chat_data.setdefault('history', []).extend([{"role": "user", "content": update.message.text}, {"role": "assistant", "content": reply}])
        await update.message.reply_text(f"{reply}\n\n(餘：{rem})")
    except Exception as e:
        await update.message.reply_text("AI 思考中斷，請重試。")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot 已啟動，請加入群組使用...")
    app.run_polling(drop_pending_updates=True)
