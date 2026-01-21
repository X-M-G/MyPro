@echo off
setlocal
echo === 正在配置 GitHub 代理 ===
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

echo.
echo === 开始同步代码到 GitHub ===
git add .
set /p msg="请输入本次提交的说明: "
git commit -m "%msg%"

echo.
echo 正在推送...
git push
echo === 同步完成！===
pause