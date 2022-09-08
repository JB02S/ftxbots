from flask import Flask, request, abort
from bots import bot1

app = Flask(__name__)
confirmationState = input("Most recent type of confirmation signal? UT or DT?")
catcherState = input("Trend catcher state? CD for red or CU for green.")
bot = bot1.Bot(confirmationState, catcherState)
print(bot.botInfo)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        alert_data = str(request.data)[2:-1]
        bot.update(alert_data)
        return 'success', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run()
