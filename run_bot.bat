@echo off

echo Starting Domain92 Discord Bot...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if config file exists
if not exist "config.json" (
    echo Config file not found. Creating from example...
    copy config.json.example config.json
    echo Please edit config.json with your bot token before running again.
    echo You can also set the DISCORD_BOT_TOKEN environment variable instead.
    pause
    exit /b 1
)

REM Check for bot token
if "%DISCORD_BOT_TOKEN%"=="" (
    echo Checking config file for bot token...
    findstr /C:"YOUR_DISCORD_BOT_TOKEN_HERE" config.json >nul
    if %errorlevel%==0 (
        echo Please set your bot token in config.json or as DISCORD_BOT_TOKEN environment variable.
        pause
        exit /b 1
    ) else (
        echo Bot token found in config file.
    )
) else (
    echo Using bot token from environment variable.
)

REM Start the bot
echo Starting Discord bot...
python discord_bot.py

pause