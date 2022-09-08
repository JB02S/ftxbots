def calc_sl(price, side, sl_percent):
    if side == 'sell':
        sl = price + price * (sl_percent / 100)
    elif side == 'buy':
        sl = price - price * (sl_percent / 100)
    return sl


def calc_tp(price, side, tp_percent):
    if side == 'sell':
        tp = price - price * (tp_percent / 100)
    elif side == 'buy':
        tp = price + price * (tp_percent / 100)
    return tp


def calc_pos_size(port, entry_price, side, acc_risk, sl):
    risk_amount = port * acc_risk
    if side == 'sell':
        sl_distance = sl - entry_price
    else:
        sl_distance = entry_price - sl
    pos_size = risk_amount / sl_distance
    return pos_size


def exit_trade(market, side, client):
    if side == 'sell':
        client.place_order(
            market=f'{market}-PERP',
            side="buy",
            price=client.get_trades('BTC-PERP')[0]['price'],
            reduce_only=True,
            size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
        )
    elif side == 'buy':
        client.place_order(
            market=f'{market}-PERP',
            side="sell",
            price=client.get_trades('BTC-PERP')[0]['price'],
            reduce_only=True,
            size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
        )


def enter_buy(market, price, size, sl, tp, client):
    client.place_order(
        market=f'{market}-PERP',
        side="buy",
        price=price,
        size=size
    )

    client.place_conditional_order(
        market=f'{market}-PERP',
        side="sell",
        size=size + (size * 2),
        type='stop',
        reduce_only=True,
        trigger_price=sl
    )

    client.place_conditional_order(
        market=f'{market}-PERP',
        side="sell",
        size=size + (size * 2),
        type='take_profit',
        reduce_only=True,
        trigger_price=tp
    )


def enter_sell(market, price, size, sl, tp, client):
    client.place_order(
        market=f'{market}-PERP',
        side="sell",
        type='limit',
        price=price,
        size=size
    )

    client.place_conditional_order(
        market=f'{market}-PERP',
        side="buy",
        size=size + (size * 2),
        type='stop',
        reduce_only=True,
        trigger_price=sl
    )

    client.place_conditional_order(
        market=f'{market}-PERP',
        side="buy",
        size=size + (size * 2),
        type='take_profit',
        reduce_only=True,
        trigger_price=tp
    )


def set_acc_risk(acc_risk, bot):
    bot.accRisk = acc_risk
