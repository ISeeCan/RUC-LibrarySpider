import requests
import base64
import os
import random
import time
from urllib.parse import urlparse, parse_qs

# 输入参数
originallink = input("原始链接: ")
bookname = input("图书名: ")
totalpage = int(input("总页数: "))  
getPDF = int(input("是否合成PDF（1合成，0跳过）："))
delePNG = int(input("是否删除图片（1删除，0保留）："))
zoom = 50  # 默认的zoom值，未详细证明，请保持不变，对图片质量影响不大

url_parts = urlparse(originallink)
linkparta = f"{url_parts.scheme}://{url_parts.netloc}{url_parts.path.split('Reader.do')[0]}"  

params = parse_qs(url_parts.query)
linkpartb = f"fileid={params['fileid'][0]}"  # 获取fileid的值

# 创建保存图片的文件夹（如果文件夹不存在）
if os.path.exists(bookname):
    raise FileExistsError(f"Error: 文件夹 '{bookname}' 已存在。")
else:
    os.makedirs(bookname)

# 服务端响应
linkmid = "GetPageImg.do?epage="


for page in range(1, totalpage):
    param_string = f"{linkpartb}&page={page}&zoom={zoom}"
    encoded_param = base64.b64encode(param_string.encode("utf-8")).decode("utf-8")
    
    full_url = linkparta + linkmid + encoded_param
    delay = random.uniform(0.2, 1.0) 
    time.sleep(delay)
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()  # 检查请求是否成功
        
        file_name = os.path.join(bookname, f"page{page}.png")
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f"成功保存 {file_name}")
    
    except requests.RequestException as e:
        print(f"请求失败，page={page}: {e}")


from PIL import Image
import os

# PDF合成
if getPDF == 1:
    image_folder = bookname  # 图片路径在bookname文件夹内
    image_files = [f"page{i}.png" for i in range(1, totalpage )]  

    images = []

    for image_file in image_files:
        try:
            image_path = os.path.normpath(os.path.join(image_folder, image_file))
            img = Image.open(image_path) 
            img = img.convert('RGB')  # 转换为RGB格式
            images.append(img)
        except FileNotFoundError:
            print(f"{image_file} 未找到，跳过本页")
            continue

    # 将所有图片合并为一个PDF
    if images:
        output_pdf = os.path.join(bookname, f"{bookname}.pdf") 
        images[0].save(output_pdf, save_all=True, append_images=images[1:], resolution=100.0, quality=95, optimize=True)
        print(f"PDF文件已保存为 {output_pdf}")
    else:
        print("没有图片文件，请检查图片路径和文件名")

    if delePNG == 1:
        for image_file in image_files:
            try:
                os.remove(os.path.join(image_folder, image_file))  
                print(f"{image_file} 已删除")
            except FileNotFoundError:
                print(f"{image_file} 未找到")
else:
    print("跳过PDF合成")
