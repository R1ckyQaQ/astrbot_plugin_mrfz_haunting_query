from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import sqlite3
import json
import httpx
import matplotlib.pyplot as plt
import os
plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题


@register("mrfz_query_haunting", "Ricky", "查询抽卡记录插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("mrfz_token_update")
    async def token_update(self, event: AstrMessageEvent,tok:str):
        con=sqlite3.connect("data/mrfz_token.db")
        cur=con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                     id STR PRIMARY KEY,
                     token VARCHAR(100)
                   )''')
        
        idx=event.get_sender_id()
        yield event.plain_result(f"用户的QQ号:{idx}\n")
        yield event.plain_result(f"用户的token:{tok}\n")
        cur.execute(f"SELECT COUNT(*) FROM users WHERE id='{idx}'")
        result=cur.fetchone()
        if(result[0]>0):
            exist=True
        else:
            exist=False
        if(exist):
             cur.execute(f"UPDATE users SET token='{tok}' WHERE id='{idx}'")
        else:
             cur.execute(f"INSERT INTO users (id,token) VALUES('{idx}','{tok}')")
        
        con.commit()
        cur.close() 
        con.close()
        yield event.plain_result(f"成功登记您的TOKEN喵~\n")
    
    @filter.command("mrfz_token_query")
    async def token_query(self,event:AstrMessageEvent):
        con=sqlite3.connect("data/mrfz_token.db")
        cur=con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                     id STR PRIMARY KEY,
                     token VARCHAR(100)
                   )''')
        
        idx=event.get_sender_id()
        yield event.plain_result(f"用户的QQ号:{idx}\n")
        cur.execute(f"SELECT COUNT(*) FROM users WHERE id='{idx}'")
        result=cur.fetchone()
        if(result[0]>0):
            exist=True
        else:
            exist=False
        if(exist):
             cur.execute(f"SELECT token FROM users where id='{idx}'")
             now=cur.fetchall()
             yield event.plain_result(f"您绑定的token为{now[0][0]}\n")
        else:
             yield event.plain_result(f"不存在的ID 请先存一下你的token喵~")
        con.commit()
        cur.close() 
        con.close()
        return
    
    @filter.command("mrfz_haunting_query")
    async def get_query(self,event:AstrMessageEvent,to_query:int):
        con=sqlite3.connect("data/mrfz_token.db")
        cur=con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id STR PRIMARY KEY,
                            token VARCHAR(100)
                        )''')
        idx=event.get_sender_id()
        cur.execute(f"SELECT COUNT(*) FROM users WHERE id='{idx}'")
        result=cur.fetchone()
        if(result[0]>0):
            exist=True
        else:
            yield event.plain_result(f"不存在的TOKEN~")
            return
        
        cur.execute(f"SELECT token FROM users where id='{idx}'")
        now=cur.fetchall()
        tok=now[0][0]

        yield event.plain_result(f"查询抽卡记录中...\n")
        #print (tok)

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://ak.hypergryph.com',
            'Pragma': 'no-cache',
            'Referer': 'https://ak.hypergryph.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        json_data = {
            'token': tok,
            'appCode': 'be36d44aa36bfb5b',
            'type': 1,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post('https://as.hypergryph.com/user/oauth2/v2/grant', headers=headers, json=json_data)
            grantToken=response.json()['data']['token']
        except Exception as e:
            yield event.plain_result("在获取grantTOKEN时出错") 
            return

        #yield event.plain_result(f"获取到grantTOKEN:{grantToken}\n")
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': '',
            'Origin': 'https://ak.hypergryph.com',
            'Pragma': 'no-cache',
            'Referer': 'https://ak.hypergryph.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'token': grantToken,
            'appCode': 'arknights',
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                        'https://binding-api-account-prod.hypergryph.com/account/binding/v1/binding_list',
                    params=params,
                    headers=headers,
                )
            bindinglist=response.json()['data']['list']
        except Exception as e:
             yield event.plain_result(f"在获取bindinglist时出错")
             return
        #yield event.plain_result(f"获取到绑定列表:{json.dumps(bindinglist,ensure_ascii=False)}\n")

        if (len(bindinglist)<=0):
            yield event.plain_result(f"没绑定角色")
            return
        
        #print (bindinglist)
        for game in bindinglist:
            if game["appCode"] == "arknights":
                for account in game["bindingList"]:
                    uid = account["uid"]
                    channel = account["channelName"]
                    nickname = account["nickName"]


                    #debug
                    #yield event.plain_result(f"查询{nickname}的抽卡记录中...\n")

                    headers = {
                        'Accept': '*/*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,zh-TW;q=0.6',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/json;charset=UTF-8',
                        'Origin': 'https://ak.hypergryph.com',
                        'Pragma': 'no-cache',
                        'Referer': 'https://ak.hypergryph.com/',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                    }

                    json_data = {
                        'token': grantToken,
                        'uid': uid,
                    }
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                'https://binding-api-account-prod.hypergryph.com/account/binding/v1/u8_token_by_uid',
                                headers=headers,
                                json=json_data,
                            )
                        u8token=response.json()['data']['token']
                    except Exception as e:
                        yield event.plain_result("在获取U8token时出错")
                        return

                    #yield event.plain_result(f"获取到u8token:{u8token}\n")

                    cookies = {}
                    headers = {
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,zh-TW;q=0.6',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/json',
                        'Origin': 'https://ak.hypergryph.com',
                        'Pragma': 'no-cache',
                        'Referer': 'https://ak.hypergryph.com/user/headhunting',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                        'baggage': 'sentry-environment=production,sentry-release=ak-user-web%401.0.0,sentry-public_key=5d78d1a7ec71b4c3f7f9d08ddc0cf864,sentry-trace_id=90e6bab2fc8049b08dd039196bd48f7e',
                        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sentry-trace': '90e6bab2fc8049b08dd039196bd48f7e-8a60a71f8e158b06',
                        # 'Cookie': 'ak-user-center=nDhVczM4XvenHw3TbAbT9wQfv8IxYLqFT%2BY1EbycPmmXoQFAvGRJRY7YaDclqBwwqlxRkEl7kacFUST1o1tepl2q%2BnbaVLGme5Jb7ZnU%2FU%2Bl7pJWMZ5ngYdpRNcwdE0%2FxCDI8RiQMKKJ6oJgptp35WL9LS83nLuzCHk9eZHjp6EWAuV%2F8u3Nqh%2BQXleZGz%2Bgxw7irXZ6n%2BTpceF3vGHsESo%2FNKsDVrxojvrOp%2B3GJIkqN%2FEBsCutwVjs0xLXhYglsb%2FZzeydVJ78prHQYPyn1j%2Br0m5LFgfr5NYkd8fgOOjE3tHJHtMrA97Bb7Zuq49HA6IYsyAdE5TjnDyN2CyACVmse2Qdn38W3tC9w80TQg%2FmMnaFfPYCvzpQ%2F91IHRLQYSL2VNzD68VlcW3rFNq4A0MUky21il9daQi%2BTXKUN%2B8nQRIvLj9t0P075ocfF49l',
                    }

                    json_data = {
                        'token': u8token,
                        'source_from': '',
                        'share_type': '',
                        'share_by': '',
                    }
                    try:
                        async with httpx.AsyncClient() as client:
                            response =await client.post('https://ak.hypergryph.com/user/api/role/login', cookies=cookies, headers=headers, json=json_data)
                    except Exception as e:
                        yield event.plain_result("登录获取Cookie失败")
                        return

                    if ("ak-user-center" in response.cookies):
                        usercookie=response.cookies["ak-user-center"]
                    else:
                        yield event.plain_result(f"登录获取cookie失败")
                        return
                    
                    #debug
                    #yield event.plain_result(f"获取到用户cookie:{usercookie}\n")

                    if(to_query==1):
                        cgtype="normal"
                    if(to_query==2):
                        cgtype="classic"
                    if(to_query==3):
                        cgtype="anniver_fest"

                    cookies = {
                        'ak-user-center': usercookie,
                    }

                    headers = {
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,zh-TW;q=0.6',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': 'https://ak.hypergryph.com/user/headhunting',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                        'baggage': 'sentry-environment=production,sentry-release=ak-user-web%401.0.0,sentry-public_key=5d78d1a7ec71b4c3f7f9d08ddc0cf864,sentry-trace_id=90e6bab2fc8049b08dd039196bd48f7e',
                        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'x-account-token': tok,
                        'x-role-token': u8token,
                    }

                    params = {
                        'uid': uid,
                        'category': cgtype,
                        'size': '100',
                    }

                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                'https://ak.hypergryph.com/user/api/inquiry/gacha/history',
                                params=params,
                                cookies=cookies,
                                headers=headers,
                            )
                        HISTORY=response.json()
                    except Exception as e:
                        yield event.plain_result("在获取历史记录时出错")
                        return


                    #debug
                    #yield event.plain_result(f"获取到历史记录:{json.dumps(HISTORY,ensure_ascii=False)}\n")

                    num={'3':0,'4':0,'5':0,'6':0}
                    tot=0
                    rare=[]
                    for each in HISTORY['data']['list']:
                        charName=each['charName']
                        rarity=each['rarity']+1
                        if(rarity==6):
                            rare.append(charName)
                        num[str(rarity)]+=1
                        isNew=each['isNew']
                        tot+=1
                    
                    label=['三星','四星','五星','六星']
                    explode=[0,0,0,0]
                    values=[num['3'],num['4'],num['5'],num['6']]
                    colors=['blue','purple','yellow','red']
                    plt.pie(values,explode=explode,labels=label,colors=colors,autopct='%1.1f%%')#绘制饼图
                    plt.title(f'近{tot}抽的抽卡统计')

                    text="您在最近"+str(tot)+"抽中 获得了以下六星干员:\n"
                    for x in rare:
                        text+=str(x)
                        text+="\n"

                    path=os.getcwd()
                    plt.savefig(f"{path}/to_show.png") 
                    chain=[
                        Comp.At(qq=event.get_sender_id()),
                        Comp.Image.fromFileSystem(f"{path}/to_show.png"),
                        Comp.Plain(f"{text}")
                    ]                   
                    yield event.chain_result(chain)

                    plt.clf()
                    os.remove(f"{path}/to_show.png")
                    con.commit()
                    cur.close()
                    con.close()
                   
