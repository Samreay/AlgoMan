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


def get_coin_name_lookup():
    return {
        "ETH": "Ethereum",
        "BCC": "Bitcoin Cash",
        "LTC": "Litecoin",
        "ZRX": "0x coin",
        "BNT": "Bancor",
        "BAT": "Basic Attention Token",
        "BTG": "Bitcoin Gold",
        "NANO": "Nano coin",
        "DASH": "Dash Coin",
        "DNT": "District0x",
        "EOS": "EOS",
        "ETC": "Ethereum Classic",
        "FUN": "FunFair",
        "OMG": "OmiseGo",
        "SALT": "SALT coin",
        "SNT": "Status Coin",
        "TRX": "Tron Coin",
        "XRP": "Ripple",
        "EVX": "Everex",
        "BNB": "Binance Coin",
        "VEN": "VeChain",
        "GTO": "Gifto",
        "MCO": "Monaco coin",
        "NEO": "Neo coin",
        "XLM": "Stellar coin",
        "QSP": "Quantstamp",
        "POE": "Po.et",
        "ENJ": "Enjin Coin"
    }


def get_trade_coin_names():
    d = get_coin_name_lookup()
    return [d[x] for x in get_trade_coins()]