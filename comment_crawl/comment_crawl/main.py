import os
import aiofiles

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi.responses import HTMLResponse

from comment_crawl.common.const import WAYFAIR_PLATFORM_ID, HOMEDEPOT_PLATFORM_ID
from comment_crawl.util.crawl_util.push_to_redis import push_urls_to_redis_by_platform
from comment_crawl.util.process_input import InputProcessor

from sqlalchemy import create_engine
from comment_crawl.util.db_conn import build_db_info
import redis

# Redis连接
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

"""
echo: 当设置为True时会将orm语句转化为sql语句打印，一般debug的时候可用
pool_size: 连接池的大小，默认为5个，设置为0时表示连接无限制
pool_recycle: 设置时间以限制数据库多久没连接自动断开
"""
DB_INFO = build_db_info()
print("connecting to: ",DB_INFO.get('mysql').get('tidb_from_url'))
g_mysql = create_engine(DB_INFO.get('mysql').get('tidb_from_url'), pool_size=8, pool_recycle=60 * 30)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/file", response_class=HTMLResponse)
async def file_select():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, "templates", "upload.html"), "r", encoding="utf-8") as file:
        content = file.read()
    return content

@app.post("/file/upload")
async def file_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .xlsx and .xls files are allowed.")

    try:
        upload_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(upload_dir, exist_ok=True)
        file_location = os.path.join(upload_dir, file.filename)

        if os.path.exists(file_location):
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid file type. Only .xlsx and .xls files are allowed."}
            )

        # 使用 aiofiles 进行异步写入文件
        async with aiofiles.open(file_location, "wb") as f:
            content = await file.read()  # 异步读取文件
            await f.write(content)  # 异步写入文件

        # 将文件处理任务放入后台任务，避免阻塞
        background_tasks.add_task(process_file, file_location)
        return {"filename": file.filename, "status": "file uploaded successfully"}

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": e.detail})

    except Exception as e:
        # 处理其他通用异常
        return JSONResponse(status_code=500, content={"message": "File upload failed", "error": str(e)})

async def process_file(file_location):
    file_processor = InputProcessor(file_location)
    file_processor.run()


def process_file_test(file_location):
    print("start process file")
    file_processor = InputProcessor(file_location)
    file_processor.run()

if __name__ == '__main__':

    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # process_file_test("downloads/files/wf_test.xlsx")
    # process_file_test("downloads/files/Lowes_test.xlsx")
    # process_file_test("downloads/files/homedepot_test.xlsx")
    # process_file_test("downloads/files/amazon_test.xlsx")
    # process_file_test("downloads/files/walmart_test.xlsx")

    # push_urls_to_redis_by_platform(WAYFAIR_PLATFORM_ID)
    # push_urls_to_redis_by_platform(HOMEDEPOT_PLATFORM_ID)
    pass
    # 定时任务：每天一次
    #schedule.every().days.do(push_urls_to_redis)
