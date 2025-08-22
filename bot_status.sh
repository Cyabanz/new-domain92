#!/bin/bash

echo "=== Domain92 Discord Bot Status ==="
echo

# Check if bot process is running
if pgrep -f "discord_bot.py" > /dev/null; then
    echo "✅ Bot is RUNNING"
    echo "Process ID: $(pgrep -f discord_bot.py)"
    echo "Memory usage: $(ps -o pid,vsz,rss,comm --no-headers -p $(pgrep -f discord_bot.py))"
else
    echo "❌ Bot is NOT running"
fi

echo
echo "=== Recent Log Entries ==="
if [ -f "bot.log" ]; then
    tail -n 15 bot.log
else
    echo "No log file found"
fi

echo
echo "=== Commands to manage the bot ==="
echo "Start bot: export PATH=\"/home/ubuntu/.local/bin:\$PATH\" && nohup python3 discord_bot.py > bot.log 2>&1 &"
echo "Stop bot:  pkill -f discord_bot.py"
echo "View logs: tail -f bot.log"
echo "Status:    ./bot_status.sh"
echo
echo "=== Discord Bot Commands ==="
echo "!start         - Select server dropdown (with custom emojis!)"
echo "!domain92      - Interactive interface (with subdomain options)"  
echo "!domain92_auto 5 - Create 5 links quickly"
echo "!domain92_subs 3 api,test,demo - Create with specific subdomains"
echo "!mylinks       - View your active domains (3 link limit)"
echo "!removelink    - Remove a specific domain"
echo "!mystats       - View your detailed statistics"
echo "!terminal ls   - Safe terminal commands"
echo "!help_domain92 - Full help"
echo
echo "=== Custom Emojis Added ==="
echo "🎯 Shadow server   - <:IMG_0342:1408216293865164810> (104.243.38.18)"
echo "🎯 PeteZah server  - <:emoji_7:1408297382570889227> (62.72.3.251)"  
echo "🎯 Lunar server    - <:IMG_0347:1408216520034881536> (172.93.101.294)"
echo "🎯 Vapor server    - <:IMG_0346:1408216290752987197> (199.180.255.67)"
echo "🎯 gn-math server  - <:IMG_0345:1408216292414062612> (107.174.34.44)"
echo "🎯 Frogiees Arcade - <:emoji_5:1408292931579678821> (152.53.81.196)"
echo "🎯 ExtremeMath     - <:emoji_6:1408295630727806996> (152.53.38.152)"