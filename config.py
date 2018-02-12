from binance.client import Client


def get_api_public():
    with open("key_public.ignore") as f:
        return f.read()


def get_api_secret():
    with open("key_secret.ignore") as f:
        return f.read()


def get_client():
    return Client(get_api_public(), get_api_secret())


def get_trade_coins():
    return ["ETH", "BCC", "LTC", "ZRX", "BNT", "BAT", "BTG", "NANO",
            "DASH", "DNT", "EOS", "ETC", "FUN", "OMG", "SALT", "SNT",
            "TRX", "XRP", "EVX", "BNB", "VEN", "GTO", "MCO", "NEO",
            "XLM", "QSP", "POE", "ENJ"]