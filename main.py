import random
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# 1. 恐怖題庫 (含長篇故事、長篇答案、關鍵字)
puzzles = [
    {
        "story": "深夜，畫家獨自喺工作室畫緊一幅全家福。佢畫完媽媽，轉身去飲水，返嚟發現畫入面媽媽嘅表情變咗，變成咗驚恐嘅尖叫。佢以為係自己記錯，繼續畫埋爸爸同細佬。點知每畫完一個，嗰個人物嘅表情都會變，最後佢畫埋自己，成幅畫變成咗一幅地獄圖。點解？",
        "answer": "其實畫家早就喺畫呢幅畫嘅一週前死咗。佢係一家人滅門慘案中嘅倖存者，但因為受唔住刺激而精神崩潰，死喺畫室入面。佢嘅靈魂一直覺得自己仲未畫完，所以每晚都出嚟畫。佢畫入面嘅嗰種「驚恐表情」，其實係佢死前最後一刻，腦海入面重現緊全家人被兇手殺死嗰一瞬間嘅殘酷記憶。嗰幅畫，係佢臨死前對呢個世界最絕望嘅控訴。",
        "keywords": {"鬼": "唔係鬼，畫家係人。", "死": "係，全家人都死咗。", "兇手": "係，畫家要搵出兇手。", "地獄": "唔相關。", "回憶": "係，畫緊嘅係佢死前嘅記憶。"}
    },
    {
        "story": "男人每晚 12 點都會收到一通電話，入面傳嚟佢老婆嘅聲音：「我好凍，快啲返嚟接我。」男人每次都心痛欲絕，但佢始終無去接。直到有一晚，佢終於忍唔住，揸車去咗老婆講嘅地方，結果佢失蹤咗。點解？",
        "answer": "三年前，男人同老婆一齊揸車行經湖邊，因為大霧撞咗落去。老婆被困車廂入面，臨死前打電話求救，但男人自己爬咗上岸生存落嚟。三年間，男人一直活喺悔疚之中。嗰啲電話，其實係佢老婆嘅冤魂從湖底打上嚟嘅召喚。嗰晚男人去到湖邊，見到全身濕透、皮膚慘白嘅老婆喺湖面伸出手，佢終於崩潰，主動揸車衝入湖入面，打算去湖底「接」返佢老婆，最後佢哋喺湖底變成咗一對怨偶。",
        "keywords": {"老婆": "係，佢死咗。", "死": "係，三年前就死咗。", "湖": "係，湖入面係關鍵。", "失蹤": "係，男人亦都唔見咗。", "車": "係，佢揸車去嗰度。" }
    },
    {
        "story": "一個男仔好鍾意玩鏡子，有一晚 3 點，佢發現鏡入面嘅自己無跟住佢郁，而係對住佢詭異一笑。第二日，佢失蹤咗。屋企人發現佢鎖咗喺房入面，已經氣絕身亡，死狀係好似自己掐死自己。點解？",
        "answer": "嗰面鏡子唔係普通嘢，係一扇通往「倒影世界」嘅門。嗰晚 3 點係陰氣最重嘅時候，鏡入面嘅替身成功同現實世界嘅男仔交換咗靈魂。男仔被困入鏡入面，眼睜睜睇住自己嘅肉身俾個替身搶走。鏡中男仔無力反抗，只能喺絕望中崩潰；而外面嘅替身，為咗徹底抹殺男仔嘅意識，控制住個身軀，令男仔嘅手自己掐住自己嘅喉嚨，直至窒息，徹底完成呢場詭異嘅取代儀式。",
        "keywords": {"鏡": "係，鏡入面有嘢。", "笑": "係，鏡入面嘅影像唔係佢。", "失蹤": "係，佢困喺鏡度。", "掐": "係，佢被自己掐死。", "替身": "係，鏡入面嘅嘢走咗出嚟。"}
    },
    {
        "story": "商場入面有個假人模特兒，每晚保安巡邏都會覺得佢換咗位置。有一晚，保安發現佢手入面多咗把染血嘅刀，而嗰晚之後，保安再無出現過。點解？",
        "answer": "呢個商場以前係一個屠宰場，後來改建。嗰個假人其實係一個被活生生封喺水泥入面嘅連續殺人狂，佢嘅怨氣太重，令佢嘅屍體可以喺夜深人靜嗰陣活動。嗰晚，保安太好奇，伸手去觸摸假人，點知假人竟然郁咗，將佢殺死。假人殺人之後，將保安嘅屍體剝皮，用特殊藥水整成新嘅假人模型，放喺同一個展示位，變成咗「新嘅陳列品」，永遠留喺商場入面。",
        "keywords": {"假人": "係，佢係殺手。", "保安": "係，保安俾人殺咗。", "血": "係，保安嘅血。", "刀": "係，武器。", "新": "係，保安變咗新嘅假人。"}
    },
    {
        "story": "深夜開車經過一條荒廢隧道，車入面原本得司機一個人。當車駛到隧道一半時，司機從倒後鏡見到後座坐咗一個長髮女人。佢嚇到停低車，回頭一睇，後座咩都無。但當佢再望倒後鏡，個女人仲喺度，而且慢慢向佢靠近。點解？",
        "answer": "司機根本無意識到，佢喺隧道入口嗰陣已經撞死咗。嗰條隧道係陽間同陰間嘅交界。車後座嗰個女人，係勾魂使者，佢嘅形態會根據死者生前最掛住嘅人嚟變化。因為司機生前最遺憾係無見到佢前女友最後一面，所以死後被勾魂使者化作前女友嘅模樣，慢慢靠近佢，喺佢回頭那一刻，將佢嘅靈魂帶走。而現實世界嗰架車，其實早已撞毀喺隧道口，只係佢嘅殘存意識仲以為自己開緊車。",
        "keywords": {"隧道": "係，地點關鍵。", "女人": "係，佢係引路嘅鬼。", "倒後鏡": "係，倒後鏡先睇到真相。", "司機": "係，佢一早死咗。", "意外": "係，隧道口發生過車禍。"}
    },
    {
        "story": "攝影師鍾意幫人影相。有一日，佢沖曬出一張舊照片，入面影到佢自己身後有一個黑影。之後佢無論去邊，只要影相，相入面一定會有嗰個黑影。最後，佢喺相入面見到自己被殺嘅畫面。點解？",
        "answer": "嗰個黑影係一個靠吸食「生命」為生嘅古老邪靈。攝影師影相嗰陣，閃光燈嘅強光會短暫撕裂現實同靈界嘅屏障，令邪靈可以攝入鏡頭入面。嗰啲相，其實係攝影師嘅「遺照」。邪靈一直透過照片嚟剝削佢嘅陽壽。喺最後一張相入面，邪靈唔再隱藏，直接顯現出佢撕裂攝影師喉嚨嘅畫面，預告咗佢嘅死期，嗰日之後，攝影師就失蹤咗，只係剩低嗰張充滿血跡嘅照片。",
        "keywords": {"相": "係，照片係關鍵。", "黑影": "係，冤魂。", "殺": "係，攝影師死咗。", "兇殺案": "係，同呢單案有關。", "跟蹤": "係，鬼一直跟住佢。"}
    },
    {
        "story": "醫院入面有一間長期鎖住嘅病房。深夜，當值護士成日聽到入面有人開心地笑，仲有玩具車喺地下跑嘅聲音。護士開門睇，入面咩都無。點解？",
        "answer": "呢間病房以前係小兒科，一個患絕症嘅細路喺度過咗最後嘅時光。佢喺呢度過身後，靈魂太過純真，根本唔知自己已經死咗，佢以為自己仲喺醫院接受治療，只係醫生同護士忙緊，無人陪佢玩。嗰啲笑聲同玩具車聲，係佢喺靈界嘅玩樂。每當有護士入去，佢就會隱形，因為佢驚俾人鬧佢嘈喧巴閉，所以護士永遠見唔到佢，但佢其實一直喺度。",
        "keywords": {"醫院": "係。", "細路": "係，鬼魂係細路。", "笑": "係，細路玩得好開心。", "玩具車": "係，佢玩緊玩具。", "死": "係，佢死咗好多年。"}
    },
    {
        "story": "女孩得到一個精緻嘅洋娃娃屋，入面嘅裝修同佢屋企一模一樣。有一日，佢發現洋娃娃屋入面嘅床上，瞓咗一具細小嘅屍體。女孩覺得好奇，打開洋娃娃屋想攞出嚟，結果佢當場嚇到休克。點解？",
        "answer": "嗰個洋娃娃屋係一場詛咒。每當洋娃娃屋發生咩事，現實嘅屋都會發生咩事。嗰具細小嘅屍體，係女孩自己嘅「靈體模型」。當佢打開屋嗰一刻，佢透過詛咒連結，清楚感受到自己肉體嘅死亡過程。現實入面，佢屋企嘅床上面，佢嘅肉身其實早已經俾入屋打劫嘅賊殺咗，而佢嘅靈魂被困喺娃娃屋裏面，成為咗呢個詛咒裝置嘅一部分。",
        "keywords": {"洋娃娃屋": "係，關鍵物品。", "屍體": "係，係女孩自己。", "預言": "係，屋會預測未來。", "休克": "係，嚇死。", "屋企": "係，同洋娃娃屋連結。"}
    },
    {
        "story": "巴士司機每晚載客，有一晚，車上明明坐滿咗 11 個人，但當佢望返閉路電視，入面永遠只係顯示得 10 個人。最後嗰個人，司機從來無見過佢落車。點解？",
        "answer": "呢架巴士嘅路線曾經發生過嚴重車禍，全車乘客無一生還。司機係唯一倖存者，但因為腦部受創，佢產生咗「集體幻覺」。嗰第 11 個人，係嗰場車禍入面死得最慘嘅乘客，佢嘅靈魂一直唔肯走，每晚都會返嚟坐喺嗰個固定位置。閉路電視顯示唔到佢，係因為佢係靈體。而嗰位乘客由始至終都無落車，係因為佢根本唔知自己已經死咗，仲以為緊返緊屋企。",
        "keywords": {"巴士": "係，地點。", "閉路電視": "係，顯示唔到。", "鬼": "係，乘客係鬼。", "11個人": "係，司機覺得有11人。", "意外": "係，以前發生過車禍。"}
    },
    {
        "story": "一間屋被焊死咗 20 年。警方因為收到異味投訴，將鐵門割開。入面乾淨整潔，餐枱上面擺好晒飯菜，好似啱啱煮好咁。屋主坐喺梳化上面已經化成白骨，但佢嘅頭髮長到蓋住成個梳化。點解？",
        "answer": "屋主係一個邪教徒，佢喺度進行緊一場「永生儀式」。佢將自己鎖喺屋入面，準備絕食 49 日嚟達到飛升。但儀式出咗錯，佢死咗，但個身體變成咗一個詛咒容器。呢度嘅「飯菜」其實係供奉俾邪神嘅供品，經過 20 年依然新鮮，係因為吸收咗屋主死後所剩餘嘅所有生氣。而佢嘅頭髮繼續長，係因為嗰個邪教嘅詛咒——頭髮係連結靈魂同身體嘅橋樑，即使肉身腐爛，頭髮依然會喺儀式失敗嘅憤恨下，不斷生長，試圖編織成一個新嘅肉身。",
        "keywords": {"焊死": "係，出唔到去。", "飯菜": "係，新鮮。", "白骨": "係，屋主。", "頭髮": "係，死後繼續生。", "詛咒": "係，屋入面有邪力。"}
    }
]

MAX_ATTEMPTS = 25

# 啟動遊戲嘅輔助函數
async def start_game(update, context, puzzle):
    context.user_data['current_game'] = puzzle
    context.user_data['attempts'] = MAX_ATTEMPTS
    context.user_data['found_keys'] = set()
    await update.message.reply_text(
        f"【恐怖海龜湯】：\n{puzzle['story']}\n\n"
        f"你有 {MAX_ATTEMPTS} 次提問機會！\n"
        f"如果想認輸或揭曉答案，請輸入 /reveal。"
    )

async def play(update, context):
    game = random.choice(puzzles)
    await start_game(update, context, game)

async def next_puzzle(update, context):
    game = random.choice(puzzles)
    await update.message.reply_text("正在開啟下一個恐怖故事...")
    await start_game(update, context, game)

async def reveal(update, context):
    game = context.user_data.get('current_game')
    if not game:
        await update.message.reply_text("無遊戲進行緊，請用 /play 開始。")
        return
    await update.message.reply_text(f"【答案揭曉】：\n{game['answer']}")
    context.user_data['current_game'] = None

async def check_question(update, context):
    game = context.user_data.get('current_game')
    if not game:
        await update.message.reply_text("請先輸入 /play 開始遊戲。")
        return
    
    # 檢查次數
    context.user_data['attempts'] -= 1
    remaining = context.user_data['attempts']
    
    if remaining < 0:
        await update.message.reply_text("機會用盡！請用 /next 開下一個湯，或者 /reveal 睇答案。")
        return
    
    user_text = update.message.text
    found_key = None
    
    # 檢查有無關鍵字
    for keyword, response in game['keywords'].items():
        if keyword in user_text:
            found_key = keyword
            context.user_data['found_keys'].add(keyword)
            await update.message.reply_text(f"{response} (剩餘: {remaining})")
            break 
    
    # 90% 提示邏輯
    total_keys = len(game['keywords'])
    found_count = len(context.user_data['found_keys'])
    if found_count >= (total_keys - 1) and not found_key:
         await update.message.reply_text("你已經掌握大部分真相，仲差 1-2 個關鍵細節！")
    elif not found_key:
        await update.message.reply_text(f"不相關。(剩餘: {remaining})")
if __name__ == '__main__':
    # 新增：開一個背景 Web Server
    threading.Thread(target=run_web).start()
    
    # 原本嗰段 bot 啟動碼
    TOKEN = '8806982911:AAGtDR-qiyKRJlSl8mghC484UcR3qzub55M'  # 記得填返你個 Token
    # ... (下面照舊)
if __name__ == '__main__':
    # 【注意】一定要填入你個 Token
    TOKEN = '8806982911:AAGtDR-qiyKRJlSl8mghC484UcR3qzub55M' 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('play', play))
    app.add_handler(CommandHandler('next', next_puzzle))
    app.add_handler(CommandHandler('reveal', reveal))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_question))
    
    print("Bot 已經啟動！")
    app.run_polling()
