### Telegram-bot

```
A Telegram bot for tracking the status of homework checks on Yandex.Praktikum.
Sends messages when the status is changed - submitted for review, has remarks, approved.
```

### Stack:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

### How to run the project:

Clone the repository and navigate to it in the command line:

```
git clone git@github.com:PashkaVRN/homework_bot.git
```

```
cd homework_bot
```

Create and activate a virtual environment:

```
python -m venv env
```

```
source env/bin/activate
```

Install dependencies from the requirements.txt file:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Set the necessary keys as environment variables (in the .env file):
- Yandex.Praktikum profile token
- Telegram bot token
- Your Telegram ID

Run the project:

```
python homework.py
```