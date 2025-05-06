# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/21 23:35
@Describe:
'''
# main.py (FastAPI后端)
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,FileResponse
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
# 解决中文文件名编码
from urllib.parse import quote


app = FastAPI()

# 创建上传目录
UPLOAD_DIR = "./static"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 允许所有来源（生产环境建议指定具体域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载静态文件目录
app.mount(UPLOAD_DIR[1:], StaticFiles(directory="static"), name="static")

class FileInfo(BaseModel):
    name: str
    size: int
    modified_time: float

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/files/", response_model=List[FileInfo])
async def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        stat = os.stat(file_path)
        files.append(FileInfo(
            name=filename,
            size=stat.st_size,
            modified_time=stat.st_mtime
        ))
    return files

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"message": "File deleted successfully"}



@app.get("/", response_class=HTMLResponse)
async def main():

    html_path='./index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    #print(html)
    return html

# main.py 后端新增下载端点
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    encoded_filename=quote(filename,safe='')
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"},
    )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8003)