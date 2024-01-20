import cv2
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
from core import user_login, blind_order

app = FastAPI()


@app.post("/upload-qrcode/")
async def create_upload_file(file: UploadFile = File(...)):
    # 读取上传的文件内容为字节流
    contents = await file.read()
    # 将字节流转换为NumPy数组，然后转换为OpenCV图像格式
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    try:
        # 将图像转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        print(e)
        raise HTTPException(detail="上传二维码识别失败", status_code=400)
    # 使用opencv解码二维码
    qr_code_data, _, _ = cv2.QRCodeDetector().detectAndDecode(gray)
    if qr_code_data:
        return {"readCode": qr_code_data.split("=")[-1], "code": 200}
    else:
        return {"readCode": "二维码识别失败", "code": 400}


@app.post("/scanQRCodes", description="扫码", summary="扫码")
async def scan_qr_code(image_id: str, username: str = "15863732088", password: str = "123456"):
    try:
        userinfo, user_id, tenant_id = await user_login(username, password)
    except Exception as e:
        raise HTTPException(detail=f"账号密码不正确{username, password}", status_code=400)
    access_token = userinfo["access_token"]
    driver_id = userinfo["user_id"]
    # truck_list()
    data = await blind_order(username, password, image_id=image_id, access_token=access_token, driver_id=driver_id,
                             user_id=user_id, tenant_id=tenant_id)
    if data:
        return {"detail": "程序执行完成", "message": data}
    return {"detail": "程序执行完成，请登录账号查看", "code": 200}


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000)
