@echo off
chcp 65001 >nul
setlocal

git config --global core.quotepath false

echo === 正在配置 GitHub 代理 ===
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

echo.
echo === 正在执行安全回退 (Revert) ===
echo 这将创建一个反向提交来抵消上一次的改动...
echo.

git revert HEAD --no-edit

echo.
echo 正在推送回退记录到 GitHub...
git push

echo.
echo === 回退成功！===
pause