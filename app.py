#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a flask server that work as a webhook for answering 
requests from dialogflow.com conserning cryptocurrency prices in portuguese.
"""

from flask import Flask, render_template
from flask_assistant import Assistant, ask, tell

import requests

# APP CONFIG

app = Flask(__name__)
assist = Assistant(app, '/')

COINMARKET_API_URL = "https://api.coinmarketcap.com/v1/ticker/"

# AVAILABLE_COINS indicates the current available coins for which we can provide information 
AVAILABLE_COINS = (
	"bitcoin",
	"ethereum",
	"ripple",
	"bitcoin-cash",
	"cardano",
	"stellar",
	"neo",
	"litecoin",
	"eos",
	"nem",
)

# AVAILABLE_COINS_AS_STRING will help us to indicates which coins are available
AVAILABLE_COINS_AS_STRING = ', '.join(AVAILABLE_COINS)


# -----------------------

# 
# API CALLS
# 

# this url will render a iframe web demo of the bot
@app.route("/")
def home():
	return render_template('index.html')


# INTENT: hello 
# Will greet the user and tell what we can do
@assist.action('hello')
def hello_intent():
	speech = "Oi! Eu sou o CryptoBot e posso lhe dar o preço atual das seguintes moedas: "
	speech += AVAILABLE_COINS_AS_STRING	
	return tell(speech)


# INTENT: price_of_coin 
# Will receive a coin name and should retrive the price
@assist.action('price_of_coin')
def price_of_coin_intent(coin):

	# check if coin is not in AVAILABLE_COINS
	# if not, then return the list of names of coins available
	if coin not in AVAILABLE_COINS:
		speech = "Desculpe, ainda não conheço essa moeda.. Pergunte-me sobre: "
		speech += AVAILABLE_COINS_AS_STRING	
		return tell(speech)

	# get the information of the coin
	price, change24h = get_coin_price_and_change24h(coin)

	# build response
	speech = "O preço atual da {} é {} USD. Variou {}% nas ultimas 24 horas.".format(coin.upper(), price, change24h)
	return tell(speech)


# -----------------------

# 
# HELPER FUNCTIONS
# 

# this function wil retrun a tuple with the current price in usd and change percent in the last 24h
def get_coin_price_and_change24h(coin):

	coin_info = request_coin_info(coin)

	# check if coin_info is None
	# this means the coin is not available
	if coin_info is None:
		return None

	return coin_info["price_usd"], coin_info["percent_change_24h"]



# This function will return an parsed json object with the info of the coin
# if the coin is not available then it will return None
def request_coin_info(coin):
	
	# check if coin is not in AVAILABLE_COINS
	# if not, then return None
	if coin not in AVAILABLE_COINS:
		return None

	URL = COINMARKET_API_URL + coin
	r = requests.get(URL)

	return r.json()[0]


# -----------------------

# should change for a nginx server for production
if __name__ == "__main__":
	app.run(port=5000)