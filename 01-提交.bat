@echo off
:: 切换到 UTF-8 代码页
chcp 65001 >nul
setlocal

:: 设置 Git 显示中文
git config --global core.quotepath false

echo === 正在配置 GitHub 代理 ===
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

echo.
echo === 开始同步代码到 GitHub ===

:: 1. 添加所有变动
git add .

:: 2. 获取提交说明（确保变量名和等号之间没有空格）
echo 请输入本次提交的说明并按回车:
set /p commit_msg=^> 

:: 3. 如果直接回车没有输入，设置一个默认值防止报错
if "%commit_msg%"=="" set commit_msg=Update code at %date% %time%

:: 4. 提交
git commit -m "%commit_msg%"

echo.
echo 正在推送...
git push

echo.
echo === 同步完成！===
pause