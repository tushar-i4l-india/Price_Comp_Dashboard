@echo off
cd /d "C:\Price_Comp_Dashboard"
git add .
git commit -m "Auto-update: %date% %time%"
git push origin master