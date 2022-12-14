from threading import Thread
from flask import Flask, request, abort
import botmanager

t1 = Thread(target=botmanager.start_price_data_thread)
t1.setDaemon(True)
t1.start()

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        alert_data = str(request.data)[2:-1]
        botmanager.handle_webhook_data(data=alert_data)
        return 'success', 200
    else:
        abort(400)


if __name__ == "__main__":
    app.run()
