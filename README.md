# ftxbots
This project uses the FTX REST API for placing trades and receiving information about markets in order to create bots which place trades based on a certain strategy. For particular bots certain indicators are used from tradingview, in these cases notifications for tradingview must be setup and the certain bots will use a webhook to receive alerts.

## Project Aims
This project aims to:
* Make use of a trading strategy in order to place trades (which are hopefully profitable!)
* Store a record of the trades in a database along with other information about the circumstances under which the trade was taken, e.g market volume, in order to determine the best market states for the bot

## Running the bots
To run the bots, you will need to have Python 3+ installed. You will also need to install the requirements in the requirements.txt file. To do this, run the following command while in the project directory (you may need to use `pip3` instead of `pip` depending on your system):
```
pip install -r requirements.txt
```
You will also need to setup a .env file which contains two variables:
```
api_key_main = <your ftx api key>
api_secret_main =  <your ftx api secret key>
```
Once these are setup, run webhook.py to start the bots.

##Bot1
For bot1 you will need a LuxAlgo subscription for the indicators, link to website <a href="https://www.luxalgo.com/">here</a>. Based off of a strategy from Gecko from Lux Algo, strategy video found <a href="https://www.youtube.com/watch?v=GETZTJqxZfU&t=326s">here</a> <br> <br>
Indicator setup
<ul>
    <li>Lux Algo premium, use signals and agility settings sent in optibot15m in LuxAlgo discord server</li>
    <li>Lux Algo SR & Patterns Premium, Turn everything off from levels to projection, set predictive SR to Ranges, 2</li>
    <li>Lux Algo Oscillator Premium, set oscillator to UMACD</li>
</ul>

Notifications setup
<ul>
    <li></li>
</ul>

##Bot2
No setup for bot2 needed, uses relatively simple strategy found <a href="https://www.youtube.com/watch?v=0Q6iENmeUys">here</a>