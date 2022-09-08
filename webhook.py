from flask import Flask, request, abort
from bots import bot1

app = Flask(__name__)
bot = bot1.Bot()


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
