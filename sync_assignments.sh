#!/data/data/com.termux/files/usr/bin/bash
cp ~/class-solutions/Assignment/* ~/class-solutions/
git add .
git commit -m "Auto-sync Assignment files"
git pull --rebase
git push origin main

