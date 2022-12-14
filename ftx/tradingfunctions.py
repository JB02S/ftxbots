from ftx.rest.client import FtxClient


def calc_sl(price: float, side: str, sl_percent: float) -> float:
    assert side in ('buy', 'sell'), 'side must be buy or sell'
    sl_percent_decimal = sl_percent / 100
    return price + price * sl_percent_decimal if side == 'sell' else price - price * sl_percent_decimal


def calc_tp(price: float, side: str, tp_percent: float) -> float:
    assert side in ('buy', 'sell'), 'side must be buy or sell'
    tp_percent_decimal = tp_percent / 100
    return price - price * tp_percent_decimal if side == 'sell' else price + price * tp_percent_decimal


def calc_pos_size(port: float, entry_price: float, side: str, acc_risk: float, sl: float) -> float:
    assert side in ('buy', 'sell'), 'side must be buy or sell'
    risk_amount = port * acc_risk
    return risk_amount / (sl - entry_price) if side == 'sell' else risk_amount / (entry_price - sl)


def exit_trade(market: str, side: str, client: FtxClient):
    assert side in ('buy', 'sell'), 'side must be buy or sell'
    assert any(i['name'] == f'{market}-PERP' for i in client.get_markets())
    client.cancel_orders(market_name=f'{market}-PERP')

    if side == 'sell':
        client.place_order(
            market=f'{market}-PERP',
            side="buy",
            price=client.get_trades('BTC-PERP')[0]['price'],
            reduce_only=True,
            size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
        )
    else:
        client.place_order(
            market=f'{market}-PERP',
            side="sell",
            price=client.get_trades('BTC-PERP')[0]['price'],
            reduce_only=True,
            size=client.get_positions()[0]['size'] + client.get_positions()[0]['size'] * 2
        )


def enter_buy(market: str, price: float, size: float, client: FtxClient, sl: float = None, tp: float = None):
    assert any(i['name'] == f'{market}-PERP' for i in client.get_markets())

    client.cancel_orders(market_name=f'{market}-PERP')

    client.place_order(
        market=f'{market}-PERP',
        side="buy",
        price=price,
        size=size
    )

    if sl:
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=size + (size * 2),
            type='stop',
            reduce_only=True,
            trigger_price=sl
        )

    if tp:
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=size + (size * 2),
            type='take_profit',
            reduce_only=True,
            trigger_price=tp
        )


def enter_sell(market: str, price: float, size: float, client: FtxClient, sl: float = None, tp: float = None) -> None:
    assert any(i['name'] == f'{market}-PERP' for i in client.get_markets())

    client.cancel_orders(market_name=f'{market}-PERP')

    client.place_order(
        market=f'{market}-PERP',
        side="sell",
        type='limit',
        price=price,
        size=size
    )

    if sl:
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=size + (size * 2),
            type='stop',
            reduce_only=True,
            trigger_price=sl
        )

    if tp:
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=size + (size * 2),
            type='take_profit',
            reduce_only=True,
            trigger_price=tp
        )


def update_sl(market: str, new_sl: float, client: FtxClient):
    open_orders = client.get_conditional_orders(market=f'{market}-PERP')

    for i in client.get_positions():
        if i['future'] == f'{market}-PERP':
            position = i

    if position['side'] == 'buy':
        for i in open_orders:
            if i['type'] == 'stop':
                client.cancel_order(order_id=i['id'])
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=position['size'] + (position['size'] * 2),
            type='stop',
            reduce_only=True,
            trigger_price=new_sl
        )

    if position['side'] == 'sell':
        for i in open_orders:
            if i['type'] == 'stop':
                client.cancel_order(order_id=i['id'])
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=position['size'] + (position['size'] * 2),
            type='stop',
            reduce_only=True,
            trigger_price=new_sl
        )


def update_tp(market: str, new_tp: float, client: FtxClient):
    open_orders = client.get_conditional_orders(market=f'{market}-PERP')

    for i in client.get_positions():
        if i['future'] == f'{market}-PERP':
            position = i

    if position['side'] == 'buy':
        for i in open_orders:
            if i['type'] == 'take_profit':
                client.cancel_order(order_id=i['id'])
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="sell",
            size=position['size'] + (position['size'] * 2),
            type='take_profit',
            reduce_only=True,
            trigger_price=new_tp
        )

    if position['side'] == 'sell':
        for i in open_orders:
            if i['type'] == 'take_profit':
                client.cancel_order(order_id=i['id'])
        client.place_conditional_order(
            market=f'{market}-PERP',
            side="buy",
            size=position['size'] + (position['size'] * 2),
            type='take_profit',
            reduce_only=True,
            trigger_price=new_tp
        )


def set_acc_risk(acc_risk: float, bot) -> None:
    bot.accRisk = acc_risk
