def encode_message(username: str, message: str) -> bytes:
    username_bytes = username.encode("utf-8")

    username_size = len(username_bytes)

    # プロトコルによりusernamelenは1バイトのため、255バイトまでしか表現できない
    if username_size > 255:
        raise ValueError("ユーザー名が長すぎます")

    # username_sizeはint型なのでbytesに変換
    username_size_bytes = username_size.to_bytes(length=1, byteorder="big", signed=False)

    message_bytes = message.encode("utf-8")

    return username_size_bytes + username_bytes + message_bytes


def decode_message(data: bytes) -> tuple[str, str]:
    if len(data) < 1:
        raise ValueError("受信データが不足しています")
    
    # 先頭の1バイトからusernameの長さを取得
    username_size = data[0]

    # 受信したデータがusernamelenとusernameを含んでいるか確認
    if len(data) < 1 + username_size:
        raise ValueError("ユーザー名のデータが不足しています")

    username_bytes = data[1:username_size + 1]
    username = username_bytes.decode("utf-8")

    message_bytes = data[username_size + 1:]
    message = message_bytes.decode("utf-8")

    return username, message