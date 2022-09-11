from flask import Flask, request, abort
from bots import bot1

import threading

host_name = "0.0.0.0"
port = 23336
app = Flask(__name__)

@app.route('/')
def index():
    t2 = bot1.start_bot()
    t2.start()

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        alert_data = str(request.data)[2:-1]
        bot1.handle_webhook_data(data=alert_data)
        return 'success', 200
    else:
        abort(400)


if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()
