@echo off
REM --- 请把下面的路径和环境名换成你自己的 ---

REM 激活你的conda环境
call D:\Anaconda3\Scripts\activate.bat aichat

REM 用激活环境后的python来运行你的脚本
pythonw main.py

REM 运行结束后暂停，方便你看错误信息（如果出错的话）
pause