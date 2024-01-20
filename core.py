import hashlib
import random
import time
from typing import Optional
from time import sleep

import execjs
import httpx

ctx = execjs.compile("""
var E = function (e) {
    var t, n, r = 0;
    if (0 === e.length) return r;
    for (t = 0; t < e.length; t++) n = e.charCodeAt(t), r = (r << 5) - r + n, r |= 0;
    return r
}
""")


async def queue_info(username, password, access_token, client):
    url = "https://drivermobile.dachebenteng.com/api/blade-queue/reservationqueue/queueInfo?current=1&size=5"
    headers = {
        "Cookie": f"rememberAccount={username}; rememberPwd={password}",
        'blade-auth': f"bearer {access_token}",
        'authorization': 'Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2',
        'accept': '*/*',
        'x-requested-with': 'com.tencent.mm',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://drivermobile.dachebenteng.com/',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    response = await client.get(url=url, headers=headers)
    print(response.json())
    return response.json()["data"]["reservationQueue"]["id"]


async def get_info(image_id, access_token, client):
    # 获取二维码信息
    url = "https://drivermobile.dachebenteng.com/api/blade-queue/queueDeliverySub/scanningCode"
    headers = {
        "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
        "charset": "utf-8",
        "blade-auth": f"bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Host": "drivermobile.dachebenteng.com",
        "Referer": "https://servicewechat.com/wxcb459ae1e3e8f9f2/41/page-frame.html"
    }
    params = {
        "ids": image_id,
        "longitude": "110.126877",
        "latitude": "39.388662",
    }
    response = await client.get(url=url, headers=headers, params=params)
    print("扫描二维码提取信息：", response.json())
    return response.json()


def generate_md5_hash(input_string):
    # 使用 hashlib 库来生成 MD5 哈希
    hash_object = hashlib.md5(input_string.encode())
    return hash_object.hexdigest()


async def get_truck_list(access_token, client):
    url = "https://drivermobile.dachebenteng.com/api/blade-system/bladeTruck/myTruckList?auditFlag=1&current=1&size=-1"
    headers = {
        "Host": "drivermobile.dachebenteng.com",
        "Connection": "keep-alive",
        "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
        "charset": "utf-8",
        "blade-auth": f"bearer {access_token}",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxcb459ae1e3e8f9f2/41/page-frame.html"
    }
    response = await client.get(url=url, headers=headers)
    print(response.json())
    return response.json()


async def save(username, password, materialNo, vehicleno, deptId, access_token, user_id, tenant_id, client):
    data = {
        "varietyOfCoalId": materialNo,
        "vehicleno": vehicleno,
        "plantAreaId": deptId,  # 转龙弯煤矿 id
        "antiepidemicQueueVO": {}
    }
    href = "https://drivermobile.dachebenteng.com/#/epidemic/epidemiclineup"
    i = str(int(time.time() * 1000))
    clientId = "kspt_driver"
    result = "".join([user_id, tenant_id, clientId, href, i])
    c = str(ctx.call("E", result))
    input_hash = f'{{"varietyOfCoalId":"{data["varietyOfCoalId"]}","vehicleno":"{data["vehicleno"]}","plantAreaId":"{data["plantAreaId"]}","antiepidemicQueueVO":{{}}}}' + '&' + c + '&' + i + '&ByTVog4348NQmk7CZbwqr9v8AL6IO2x1'
    sign = generate_md5_hash(input_string=input_hash).upper()
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,de;q=0.7',
        'Authorization': 'Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==',
        'Blade-Auth': f'bearer {access_token}',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json;charset=utf-8',
        'Cookie': f'rememberPwd={password}; rememberAccount={username}; checkboxOnChange=true',
        'Origin': 'https://drivermobile.dachebenteng.com',
        'Pragma': 'no-cache',
        'Referer': 'https://drivermobile.dachebenteng.com/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?1',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'sign': sign,
        'str': c,
        'timestamp': i,
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',

    }
    url = "https://drivermobile.dachebenteng.com/api/blade-queue/reservationqueue/save"
    response = await client.post(url=url, headers=headers,
                                 data=f'{{"varietyOfCoalId":"{data["varietyOfCoalId"]}","vehicleno":"{data["vehicleno"]}","plantAreaId":"{data["plantAreaId"]}","antiepidemicQueueVO":{{}}}}')
    print("排队申请", response.text)


async def sure_queue(username, password, queue_id, access_token, user_id, tenant_id, client):
    url = "https://drivermobile.dachebenteng.com/api/blade-queue/reservationqueue/reservationConverToFormal"
    href = "https://drivermobile.dachebenteng.com/#/epidemic/queue/formalQueue"
    payload = {
        "id": queue_id,
        "formalQueuePosition": f"110.11{random.randint(100, 999)};39.57{random.randint(100, 999)}",
        "isVoiceSend": 0
    }
    i = str(int(time.time() * 1000))
    clientId = "kspt_driver"
    result = "".join([user_id, tenant_id, clientId, href, i])
    c = str(ctx.call("E", result))
    input_hash = f'{{"id":"{payload["id"]}","formalQueuePosition":"{payload["formalQueuePosition"]}","isVoiceSend":0}}&{c}&{i}&ByTVog4348NQmk7CZbwqr9v8AL6IO2x1'
    sign = generate_md5_hash(input_string=input_hash).upper()
    headers = {
        # 'content-length': '87',
        'blade-auth': f'bearer {access_token}',
        'authorization': 'Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2',
        'content-type': 'application/json;charset=utf-8',
        'accept': 'application/json',
        'origin': 'https://drivermobile.dachebenteng.com',
        'x-requested-with': 'com.tencent.mm',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://drivermobile.dachebenteng.com/',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': f'rememberPwd={password}; rememberAccount={username}',
        'str': c,
        'sign': sign,
        'timestamp': i
    }
    response = await client.post(url, headers=headers,
                                 data=f'{{"id":"{payload["id"]}","formalQueuePosition":"{payload["formalQueuePosition"]}","isVoiceSend":0}}')
    print(response.text)


async def get_driver_factory(author, phone, pwd, company, client):
    url = f"https://drivermobile.dachebenteng.com/api/blade-system/tenant/driver-factory-list?account={phone}"
    headers = {
        "blade-auth": f"bearer {author}",
        "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
        "referer": "https://drivermobile.dachebenteng.com/",
        "Cookie": f"rememberAccount={phone}; rememberPwd={pwd}"
    }
    response = await client.get(url=url, headers=headers)
    for data in response.json()["data"]:
        tenant_id = data["tenantId"]
        dept_id = data["deptInfos"][0]["deptId"]
        print(data["deptInfos"][0]["deptId"], data["deptInfos"][0]["deptName"])
        if company == data["deptInfos"][0]["deptName"]:
            return {"tenant_id": tenant_id, "dept_id": dept_id}


async def user_login(username, password):
    async with httpx.AsyncClient() as client:
        # 第一次登录
        url = "https://drivermobile.dachebenteng.com/api/blade-auth/oauth/token"
        headers = {
            "accept": "application/json",
            "login-is": "login",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
            "origin": "https://drivermobile.dachebenteng.com",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://drivermobile.dachebenteng.com/",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        data = {
            "username": username,
            "password": password,
            "type": "account",
            "grant_type": "password",
            "scope": "all",
        }
        auth_response = await client.post(url=url, headers=headers, data=data)
        print("第一次登录", auth_response.json())
        # 获取公司信息
        try:
            company_info = await get_driver_factory(auth_response.json()["access_token"], phone=username, pwd=password,
                                                    company="转龙湾煤矿", client=client)
        except Exception as e:
            print(e, username, password)
        # hintpop
        url = f"https://drivermobile.dachebenteng.com/api/blade-system/user/hintpopup?userId={auth_response.json()['user_id']}"
        headers = {
            "blade-auth": f"bearer {auth_response.json()['access_token']}",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
            "referer": "https://drivermobile.dachebenteng.com/",
            "Cookie": f"rememberAccount={username}; rememberPwd={password}"
        }
        check_response = await client.get(url=url, headers=headers)
        print("hintpop", check_response.json())
        # join-company
        url = "https://drivermobile.dachebenteng.com/api/blade-system/user/join-company"
        headers = {
            "accept": "application/json",
            "blade-auth": f"bearer {auth_response.json()['access_token']}",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
            "referer": "https://drivermobile.dachebenteng.com/",
            "Cookie": f"rememberAccount={username}; rememberPwd={password}"
        }
        data = {
            "account": username,
            "tenantId": company_info["tenant_id"],
            "clientId": "kspt_driver",
            "registerType": "0",
            "userId": auth_response.json()['user_id']
        }
        company_response = await client.post(url=url, headers=headers, json=data)
        print("join-company", company_response.json())
        # 等二次登录需要带第一次登录的token
        url = 'https://drivermobile.dachebenteng.com/api/blade-auth/oauth/token'
        headers = {
            "Host": "drivermobile.dachebenteng.com",
            "Cookie": f"rememberAccount={username}; rememberPwd={password}",
            "tenant-id": company_info["tenant_id"],  # tenantId url是 enant/driver-factory-list
            "blade-auth": f"bearer {auth_response.json()['access_token']}",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
            "dept-id": company_info["dept_id"],  # 龙湖  tenId   url是 enant/driver-factory-list
            "origin": "https://drivermobile.dachebenteng.com",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://drivermobile.dachebenteng.com/",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        # 备用
        payload = f'username={username}&type=account&Tenant-Id=525094&grant_type=password&scope=all'
        auth2_response = await client.post(url, headers=headers, params=payload)
        print(auth2_response.json())
        headers = {
            "accept": "application/json",
            "login-is": "login",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "blade-auth": f"bearer {auth2_response.json()['access_token']}",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5307 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxcb459ae1e3e8f9f2",
            "origin": "https://drivermobile.dachebenteng.com",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://drivermobile.dachebenteng.com/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": f"rememberAccount={username}; rememberPwd={password}"
        }
        url = f"https://drivermobile.dachebenteng.com/api/blade-auth/oauth/check_token?token={auth2_response.json()['access_token']}"
        check_token = await client.post(url=url, headers=headers)
        print("等二次登录需要", check_token.json())
        user_id = check_token.json()["user_id"]
        tenant_id = check_token.json()["tenant_id"]
    return auth2_response.json(), user_id, tenant_id


async def blind_order(username, password, access_token, image_id, driver_id, user_id, tenant_id):
    from datetime import datetime, time
    async with httpx.AsyncClient() as client:
        while True:
            # now = datetime.now()
            # # target_time = time(13, 59, 40)
            # target_time = time(18, 10, 40)
            # print(f"当前时间未{target_time}")
            # if now.time() >= target_time:
            driver_info = await get_info(image_id=image_id, access_token=access_token, client=client)
            if driver_info.get("data"):
                break
            if "已全部绑定" in driver_info.get("msg"):
                return driver_info.get("msg")
            if "请重新登录'" in driver_info.get("msg"):
                return driver_info.get("msg")
        # 获取司机信息
        driver_info_2 = await get_truck_list(access_token, client=client)
        url = "https://drivermobile.dachebenteng.com/api/blade-queue/queueDeliverySub/bindDelivery"
        headers = {
            "Host": "drivermobile.dachebenteng.com",
            "Connection": "keep-alive",
            "authorization": "Basic a3NwdF9kcml2ZXI6c2Fhc19rc3B0X2RyaXZlcg==",
            "blade-auth": f"bearer {access_token}",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/1110005 MMWEBSDK/20230805 MMWEBID/4650 MicroMessenger/8.0.42.2460(0x28002A58) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            "content-type": "application/x-www-form-urlencoded",
            "Referer": "https://servicewechat.com/wxcb459ae1e3e8f9f2/41/page-frame.html",
        }
        data = {
            "id": driver_info["data"]["id"],
            "distributId": driver_info["data"]["id"],
            "driverPhone": driver_info_2["data"]["records"][0]["phone"],  # 无
            "driverIdcard": driver_info_2["data"]["records"][0]["identityCard"],
            "driverName": driver_info_2["data"]["records"][0]["driverName"],
            "vehicleNo": driver_info_2["data"]["records"][0]["truckNo"],
            "driverId": driver_id,
            "deptId": driver_info_2["data"]["records"][0]["createDept"],
            "deliveryNo": "undefined",
            "deliveryId": driver_info["data"]["deliveryId"],
            "carrierName": driver_info["data"]["carrierName"],
            "axles": "8",
            "axlesName": driver_info_2["data"]["records"][0]["extAxlesName"],
            "preamount": "",
            "longitude": f"110.126{random.randint(100, 999)}",  # 经度
            "latitude": f"39.388{random.randint(100, 999)}",  # 维度
        }
        # 绑定二维码
        response = await client.post(url=url, headers=headers, data=data)
        print(response.json())
        await save(username, password, driver_info["data"]["materialNo"],
                   driver_info_2["data"]["records"][0]["truckNo"],
                   driver_info["data"]["deptId"], access_token=access_token, user_id=user_id,
                   tenant_id=tenant_id, client=client)
        sleep(9)
        # 获取排队id
        queue_id = await queue_info(username, password, access_token=access_token, client=client)
        # 确认排队
        await sure_queue(username, password, queue_id=queue_id, access_token=access_token, user_id=user_id,
                         tenant_id=tenant_id, client=client)
