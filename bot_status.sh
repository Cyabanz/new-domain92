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
echo "!start         - Select server dropdown"
echo "!domain92      - Interactive interface"  
echo "!domain92_auto 5 - Create 5 links quickly"
echo "!terminal ls   - Safe terminal commands"
echo "!help_domain92 - Full help"