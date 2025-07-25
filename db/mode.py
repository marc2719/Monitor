from .mode import get_rest_mode

request_mode = {
    'private_account': {
        "op": "subscribe",
        "args": [{
            "channel": "account",
        }]
    }
}

mode_data = get_rest_mode()

# mode_json 以字典的形式返回数据
mode_json = { item.get('name'): item for item in mode_data }
