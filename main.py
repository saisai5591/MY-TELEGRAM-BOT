import random
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 1. 配置區 - 請確保你的環境變數已設置 TOKEN 和 GROQ_API_KEY
# 如果你係直接喺 Code 填 Key，就將 os.getenv(...) 換成 '你的Key'
import os
import os
# ... (前面嘅 import 同設定唔變)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'attempts' not in context.chat_data: return
    
    user_text = update.message.text
    context.chat_data['attempts'] -= 1
    rem = context.chat_data['attempts']

    # 核心邏輯：叫 AI 判斷真相
    # 我幫你加咗「如果真相被還原，請用【遊戲結束：真相還原】開頭」
    system_prompt = (
        "你係海龜湯嘅判官。請根據故仔判斷玩家係咪已經還原咗真相。"
        "如果玩家講中咗關鍵真相，請你回覆【遊戲結束：真相還原】並詳細解說。"
        "否則，只可以回答「係」、「唔係」或者「無關」。"
    )
    
    # 呢度假設你用緊 OpenAI/Groq 嘅 chat completion
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"故仔: {context.chat_data['game']['story']}。玩家提問: {user_text}"}
        ]
    )
    
    reply = response.choices[0].message.content
    
    # 自動偵測係咪贏咗
    if "【遊戲結束：真相還原】" in reply:
        await update.message.reply_text(f"🎉 恭喜！{reply}")
        del context.chat_data['attempts'] # 清除遊戲狀態
    else:
        # 剩餘次數提示
        warning = ""
        if rem <= 2: warning = f"⚠️ 只剩最後 {rem} 次機會！"
        await update.message.reply_text(f"{warning}\n{reply}\n(剩餘: {rem})")

# 唔好寫死個 Key，改做讀取你喺 Render 設定嘅變數
TOKEN = os.getenv('TOKEN')
GROQ_API_KEY = os.getenv('OPENAI_API_KEY') # 留意返，呢度改咗做 OPENAI_API_KEY 配合 openai 套件


client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# 2 故事 
puzzles = [
    {
        "story": "深夜，一間豪華公寓入面，男主人倒喺血泊中，屋入面嘅四部時鐘分別指住唔同時間。報警嘅女人聲淚俱下，話自己啱啱返屋企。警察到場後，女人卻被即時逮捕，唔係因為佢殺咗人，而係佢犯咗另外一個更離譜嘅罪。點解？",
        "answer": "真相：女人其實係一個專業嘅「時間犯罪者」。佢殺咗男主人後，故意將四部時鐘調校到唔同嘅時間，造成佢喺唔同地點都有「不在場證明」嘅假象。然而，警察發現四部時鐘嘅機械結構全部被佢拆過，因為佢為咗製造假證供，拆毀咗成棟大廈嘅時間同步系統，導致當時整棟大廈嘅電子鎖同保安系統全部失效，造成極大混亂，呢個係重大公共設施破壞罪。女人嘅目的係為咗掩蓋佢喺嗰段「缺失嘅時間」入面，非法侵入咗男主人嘅私人保險庫，盜取咗可以毀滅全球金融秩序嘅加密代碼，佢唔係為咗錢，係為咗一場精心策劃嘅金融恐怖襲擊。"
    },
    {
        "story": "地鐵站入面，一個男人喺月台邊緣行嚟行去，望住隧道入面嘅黑洞。隨住列車入站，佢突然跳咗落去，但並冇自殺。車長煞車不及，全車震動。奇怪嘅係，事後閉路電視顯示，佢跳落去嗰刻，月台上面竟然有第二個人喺度鼓掌。點解？",
        "answer": "真相：嗰個男人係一名極限表演藝術家，而嗰條地鐵隧道入面有一條專門通往地下藝術畫廊嘅隱秘入口。男人係為咗進行一個名為「消失與重現」嘅行為藝術，嗰條「黑洞」其實係佢同地下組織合謀開鑿嘅逃生通道。至於月台上鼓掌嘅人，係該藝術展嘅策展人，亦係唯一知情者。佢鼓掌唔係因為想佢死，而係因為男人成功喺列車撞擊前一秒，利用磁力裝置吸附喺列車底部，並喺列車過彎時精準跳入隱秘隧道。成件事係一場針對社會冷漠嘅反諷行為藝術，嗰個「死者」其實早就安排咗替身喺車廂尾部假扮乘客，令公眾以為發生咗慘劇，從而引發對城市安全同藝術邊界嘅討論。"
    },
    {
        "story": "深山入面有一間古老嘅教堂，牧師每晚都會喺神像前獻祭一隻活羊。村入面嘅人一直覺得好平安，直到有一日，牧師突然喺神像前自殺，村入面嘅人隨即開始集體失蹤，死狀極慘。點解？",
        "answer": "真相：嗰隻活羊其實係村莊入面嘅「容器」。村莊入面隱藏住一隻遠古嘅邪神，需要不斷吞噬活物嘅靈魂嚟維持封印。牧師其實係守護封印嘅最後一代術士，佢每日獻祭活羊，係透過儀式將村民嘅「惡念」注入羊入面，並殺死羊嚟將呢啲惡念消除。當牧師發現自己壽命將盡，無法再壓制呢股力量，又冇人可以繼承呢個詛咒，佢選擇自殺嚟強制令神像封印失效。封印解開後，累積咗幾十年嘅村民惡念瞬間爆發，由心入面控制咗村民，令佢哋發狂並互相殘殺，最終導向滅亡。牧師嘅自殺，係因為佢意識到呢個循環已經無法拯救任何人，佢想將真相透過死亡帶入地獄。"
    },
    {
        "story": "畫廊入面，一幅名為《無人之境》嘅畫作，每日都會多出一個黑色嘅人影。直到第 100 日，畫作突然消失，而畫廊嘅保安亦都隨之人間蒸發。點解？",
        "answer": "真相：嗰幅畫係一個活嘅「視覺陷阱」。畫家利用咗一種未經證實嘅「量子成像技術」，將受害者嘅意識困喺畫入面。嗰啲黑色人影，其實係之前失蹤嘅保安，佢哋因為好奇觸摸咗畫作，意識被強制提取並壓縮入畫布嘅微觀結構入面。每過一日，畫布就會因為容納咗新嘅意識而產生形態變化，顯現出人影。第 100 日係容量嘅極限，畫作啟動咗「重寫機制」，將整幅畫連同畫廊入面最後一個觀察者（即係保安）一齊吸收，將畫廊變成一個「空白」嘅維度入口。保安並唔係逃走咗，而係成為咗畫入面第 101 個黑色人影，而畫作嘅消失，係因為它已經轉移到下一個受害者身邊繼續吸食意識。"
    },
    {
        "story": "郵輪喺大海上航行，船長發現所有旅客同船員都喺同一時間失蹤，唯獨佢一個人仲喺駕駛室入面，手上面拎住一個壞咗嘅收音機。收音機入面不斷傳出佢自己嘅聲音。點解？",
        "answer": "真相：這艘船其實係處於一個「時間循環監獄」。船長原本係一名犯下嚴重戰爭罪行嘅將領，佢被判處「無限輪迴」嘅懲罰。嗰部收音機，係佢過往無數次循環入面唯一保存落嚟嘅遺物，記錄咗佢喺每一次輪迴入面所做嘅錯誤決定。喺每一次循環開始時，佢都會唔小心啟動收音機，導致時空產生擾動，將船上所有「意識過於薄弱」嘅人直接從現實中抹除。船長係唯一嘅囚犯，船上面其他人其實係由佢腦入面嘅記憶碎片具現化出嚟嘅「NPC」。每一次當佢嘗試改變結局時，記憶碎片就會因為無法負荷而崩塌，導致「失蹤」。佢永遠被困喺呢個寂靜嘅循環入面，不斷聽住自己喺唔同時間線嘅懺悔，直到佢徹底崩潰為止。"
    }
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
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(CommandHandler("next", next_puzzle))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
