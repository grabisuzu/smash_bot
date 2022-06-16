# インストールした discord.py を読み込む
import discord
import random
import pandas as pd
import math

# 自分のBotのアクセストークン
TOKEN = ''

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
# 処理完遂時にはembedでメッセージを送信
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    def check(msg):
        return msg.author == message.author

    if message.author.bot:
        return

    # /randomと入力されたとき入力された人の中から2人を抽選する
    if message.content == "/random":
        await message.channel.send('人数を入力してください')
        while True:
            randNum = await client.wait_for("message", check=check)
            if randNum.content.isdecimal():
                break
            else:
                await message.channel.send('数字を入力してください')
        if int(randNum.content)>1:
            randList=[]
            for i in range(int(randNum.content)):
                await message.channel.send(str(i+1)+'人目を入力してください')
                randPlayer = await client.wait_for("message", check=check)
                randList.append(randPlayer.content)
            randSelectNum=random.sample(range(int(randNum.content)), k=2)
            embed = discord.Embed(title="ランダム選択の結果",description="",color=0xe6e6fa)
            embed.add_field(name=randList[randSelectNum[0]],value="一人目")
            embed.add_field(name=randList[randSelectNum[1]],value="二人目")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send('1人やん\n処理を終了します')

    # /buttleと入力されたときレート対戦機能を実行する
    if message.content == '/buttle':
        df = pd.read_csv('E:\py_content\discord_Smash.csv', encoding="shift-jis",index_col=0)
        await message.channel.send('対戦に勝った人を入力してください\nwinner↓')

        wait_message = await client.wait_for("message", check=check)
        win_player=str(wait_message.content)
        # 入力されたプレイヤーが存在するか確認
        name_check=df.query("name==@win_player")
        if len(name_check.index)==0:
            await message.channel.send('存在しないプレイヤーです\n最初からやり直してください')
            return
        await message.channel.send("winnerは "+win_player+" で間違いありませんか？\ny/n")
        player_check = await client.wait_for("message", check=check)
        if "y"==str(player_check.content):            
            win_rate = df.at[str(wait_message.content),"rate"]
            win_win_count = int(df.at[str(wait_message.content),"win"])
            win_count = int(df.at[str(wait_message.content),"count"])

            # 勝者側の対戦回数を増やす
            df.at[str(wait_message.content),"win"]=win_win_count+1
            df.at[str(wait_message.content),"count"]=win_count+1
            df.at[str(wait_message.content),"winper"]=(win_win_count+1)/(win_count+1)

            # 敗者側の処理開始
            await message.channel.send('対戦に負けた人を入力してください\nloser↓')
            wait_message2 = await client.wait_for("message", check=check)
            lose_player=str(wait_message2.content)
            name_check=df.query("name==@lose_player")
            if len(name_check.index)==0:
                await message.channel.send('存在しないプレイヤーです\n最初からやり直してください')
                return
            if win_player==lose_player:
                await message.channel.send('プレイヤーが重複しています\n最初からやり直してください')
                return
            await message.channel.send("loserは "+lose_player+" で間違いありませんか？\ny/n")
            player_check = await client.wait_for("message", check=check)
            if "y"==str(player_check.content):
                lose_rate = df.at[str(wait_message2.content),"rate"]
                lose_win_count = int(df.at[str(wait_message2.content),"win"])
                lose_lose_count = int(df.at[str(wait_message2.content),"lose"])
                lose_count = int(df.at[str(wait_message2.content),"count"])

                df.at[str(wait_message2.content),"lose"] = lose_lose_count+1
                df.at[str(wait_message2.content),"count"]=lose_count+1
                df.at[str(wait_message2.content),"winper"]=lose_win_count/(lose_count+1)

                win=math.ceil(16 + (int(lose_rate) - int(win_rate))*0.04)
                lose=math.floor(-16 + (int(win_rate) - int(lose_rate))*0.04)
                if win<=0:
                    win=1
                if lose>=0:
                    lose= -1
                df.at[str(wait_message.content),"rate"] = win + win_rate
                aa = win + win_rate
                df.at[str(wait_message2.content),"rate"] = lose + lose_rate
                bb = lose + lose_rate
                await message.channel.send("レートを反映します")

                # 日本語が含まれるcsvのためshift-jis
                df.to_csv('E:\py_content\discord_Smash.csv' ,encoding="shift-jis")
                embed = discord.Embed(title="レート対戦の結果",description="",color=0x3cb371)
                embed.add_field(name=str(aa)+"(+"+str(win)+")",value=str(wait_message.content))
                embed.add_field(name=str(bb)+"(+"+str(lose)+")",value=str(wait_message2.content))
                await message.channel.send(embed=embed)

    # /info と入力されたとき任意のプレイヤー情報を送る
    if message.content == "/info":
        df = pd.read_csv('E:\py_content\discord_Smash.csv', encoding="shift-jis",index_col=0)
        await message.channel.send('プレイヤー名を入力してください\nplayer↓')

        wait_message = await client.wait_for("message", check=check)
        player_info=str(wait_message.content)
        # 入力されたプレイヤーが存在するか確認
        name_check=df.query("name==@player_info")
        if len(name_check.index)==0:
            await message.channel.send('存在しないプレイヤーです\n最初からやり直してください')
            return
        
        await message.channel.send('情報を選択してください\nレート : /rate\nメインファイター : /fighter\n試合回数 : /count\n勝率 : /winper')
        while True:
            info_message = await client.wait_for("message", check=check)
            if str(info_message.content)=="/fighter":
                embed = discord.Embed(title=df.at[player_info,"main_fighter"],description=player_info+" さんのメインファイター",color=0xffffff)
                # await message.channel.send(df.at[player_info,"main_fighter"])
                break
            elif str(info_message.content)=="/rate":
                embed = discord.Embed(title=df.at[player_info,"rate"],description=player_info+" さんの現在のレート",color=0xffffff)
                # await message.channel.send(df.at[player_info,"rate"])
                break
            elif str(info_message.content)=="/count":
                embed = discord.Embed(title=(str(df.at[player_info,"count"])+"回"),description=player_info+" さんの現在の対戦回数",color=0xffffff)
                # await message.channel.send(df.at[player_info,"count"])
                break
            elif str(info_message.content)=="/winper":
                embed = discord.Embed(title=str(float(df.at[player_info,"winper"])*100)+"%",description=player_info+" さんの現在の勝率",color=0xffffff)
                # await message.channel.send(str(float(df.at[player_info,"winper"])*100)+"%")
                break
            else:
                await message.channel.send('存在しないコマンドです\n正しいコマンドを入力してください')
        await message.channel.send(embed=embed)

    # /add と入力されたときプレイヤーを追加
    if message.content == "/add":
        df = pd.read_csv('E:\py_content\discord_Smash.csv', encoding="shift-jis",index_col=0)
        await message.channel.send("パスワードを入力してください\npassword↓")
        add_pass = await client.wait_for("message", check=check)
        if str(add_pass.content)!="admin_ssbu":
            await message.channel.send("パスワードが違います")
            return
        await message.channel.send("追加するプレイヤー名を入力してください\nplayer↓")
        new_player = await client.wait_for("message", check=check)
        new_player_check = str(new_player.content)
        name_check=df.query("name==@new_player_check")
        if len(name_check.index)!=0:
            await message.channel.send(new_player_check+" は既に登録されています")
            return
        await message.channel.send("新規登録プレイヤーは "+new_player_check+" で間違いありませんか？\ny/n")
        player_check = await client.wait_for("message", check=check)
        if "y"==str(player_check.content):
            df_fighter = pd.read_csv('E:\py_content\ssbu_fighter.csv', encoding="shift-jis",index_col=0)
            while True:
                await message.channel.send("メインファイターのファイター番号を入力してください(例　マリオ:1, ルキナ:21')\nmain_fighter↓")
                fighter_num = await client.wait_for("message", check=check)
                num_check = str(fighter_num.content)
                name_check=df_fighter.query("number==@num_check")
                if len(name_check.index)==0:
                    await message.channel.send('存在しない番号です')
                else:
                    main = df_fighter.at[str(fighter_num.content),"fighter"]
                    await message.channel.send("ファイターは "+main+" で間違いありませんか？\ny/n↓")
                    player_check = await client.wait_for("message", check=check)
                    if "y"==str(player_check.content):
                        break
            # 新しい行にプレイヤー情報を追加
            df.loc[new_player_check]=[1500,0,0,0,0,main]
            df.to_csv('E:\py_content\discord_Smash2.csv' ,encoding="shift-jis")
            embed = discord.Embed(title=new_player_check, description="登録が完了しました",color=0xfff0f5)
            await message.channel.send(embed=embed)

    # /vip でvipボーダー表示
    if message.content == "/vip":
        import re
        import requests
        #クマメイトを参照
        response = requests.get('https://kumamate.net/vip/')
        response.encoding="utf-8"
        pattern = re.compile('<span class=.vipborder.>(.+)</span>')
        matchObj=pattern.finditer(response.text)
        data=[]
        for i in matchObj:
            data.append(i.group(1))
        embed = discord.Embed(title=data[0],description="現在のVIPボーダー推定値",color=discord.Colour.red())
        await message.channel.send(embed=embed)
    
    # /stage でステージピック処理
    if message.content == "/stage":
        df_stage = pd.read_csv('E:\py_content\ssbu_stage.csv', encoding="shift-jis",index_col=0)
        # pick_stage=["1","2","3","4","5","6","7","8","9"]
        pick_stage_name=[]
        stage_str=""
        for i in range(9):
            pick_stage_name.append([str(i+1)+" : "+df_stage.at[i+1,"stage"]])
        for i in pick_stage_name:
            if len(stage_str)==0:
                stage_str=str(*i)
            else:
                stage_str+="\n"+str(*i)
        await message.channel.send(stage_str+"\n拒否するステージの数字を3つ入力してください(例 : 156, 289)↓")
        rejection_stage = await client.wait_for("message", check=check)
        # 入力が正しかった時ソートして選ばれたステージを削除
        if len(rejection_stage.content)==3 and str.isdigit(str(rejection_stage.content)) and len(rejection_stage.content)==len(set(rejection_stage.content)):
            rejection_num=[int(rejection_stage.content[0]),int(rejection_stage.content[1]),int(rejection_stage.content[2])]
            list.sort(rejection_num,reverse=True)
            for i in range(3):
                del pick_stage_name[rejection_num[i]-1]
            stage_str=""
            for i in pick_stage_name:
                if len(stage_str)==0:
                    stage_str=str(*i)
                else:
                    stage_str+="\n"+str(*i)
            await message.channel.send(stage_str)
            
            while True:
                await message.channel.send("選択するステージの数字を入力してください↓")
                num_stage = await client.wait_for("message", check=check)
                num_check = int(num_stage.content)
                num_check_img = str(num_stage.content)
                name_check=df_stage.query("number==@num_check")
                if len(name_check.index)==0:
                    await message.channel.send("存在しないステージです")
                elif rejection_num[0]==num_check or rejection_num[1]==num_check or rejection_num[2]==num_check:
                    await message.channel.send("拒否されたステージです")
                else:
                    pick_on_stage = df_stage.at[int(num_stage.content),"stage"]
                    break
            embed = discord.Embed(title=pick_on_stage, description="今回のステージとして選ばれました",color=0xdddddd)
            # 画像を表示するための処理
            file = discord.File("E:\py_content\img\stage\\"+num_check_img+".jpg",filename=num_check_img+".jpg")
            embed.set_thumbnail(url="attachment://"+num_check_img+".jpg")
            await message.channel.send(embed=embed,file=file)
        else:
            await message.channel.send("正しくない入力です\nコマンドを入力し直してください↓")
    # /frame_data で Ultimate Frame Data のURLを送信
    if message.content == "/frame_data":
        embed = discord.Embed(title="Ultimate Frame Data",description="フレームデータや判定を見ることができます",color=0xffff00)
        embed.set_author(name="Ultimate Frame Data",url="https://ultimateframedata.com/",icon_url="https://ultimateframedata.com/ogimage.png")
        await message.channel.send(embed=embed)

    if message.content == "/help":
        await message.channel.send("コマンド一覧\n/random : 入力された中からランダムに2人を選択\n/buttle : レート対戦\n/info : プレイヤー情報の表示\n/add : プレイヤーの新規登録\n/vip : 現在のVIPボーダー推定値を表示\n/frame_data : 各ファイターのフレームと判定の確認(外部サイト)\n/stage : ステージ選択")
    
client.run(TOKEN)