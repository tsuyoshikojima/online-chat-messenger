import json
import socket

from protocol import(
    StatusCode,
    encode_packet
)

from tcp_transport import(
    recv_tcrp_message,
)


SERVER_ADDRESS = ("127.0.0.1", 9001)  # 一旦ローカル通信を想定


while True:
    try:
        operation = int(input(
            "以下の内容から選び番号を入力してください。\n"
            "1. ルームを作成\n"
            "2. ルームに参加\n"
            "> "
        ))

        if operation == 1:    # 一旦ルーム作成のみを実装
            break
    except ValueError:
        print("入力値が間違っています。")
        continue

while True:
    room_name = input(
        "作成もしくは参加するルーム名を入力してください。\n"
        "> "
        ).strip()

    if room_name:
        break

while True:
    user_name = input(
        "ユーザー名を入力してください。\n"
        "> "
        ).strip()

    if user_name:
        break

password = input(
    "パスワードを作成する場合は、パスワードを入力してください。\n"
    "不要な場合は、そのままEnterを押してください。\n"
    "> "
).strip()


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(SERVER_ADDRESS)

        operation_payload = {
            "user_name" : user_name,
            "password" : password if password else None
        }

        operation_payload_json = json.dumps(operation_payload)

        request_packet = encode_packet(
            operation=operation,
            state=0,
            room_name=room_name,
            operation_payload_bytes=operation_payload_json.encode("utf-8")
        )

        client_socket.sendall(request_packet)

        header, room_name_bytes, payload_bytes = recv_tcrp_message(client_socket)   # サーバーからの応答
        response_room_name = room_name_bytes.decode("utf-8")

        if header.operation != operation or header.state != 1 or response_room_name != room_name:      # レスポンスヘッダーの検証
            raise ValueError("不正なレスポンスです")

        if len(payload_bytes) != 1:
            raise ValueError("不正なステータスコードです。")

        status_code = StatusCode(int.from_bytes(payload_bytes,"big"))

        if status_code == StatusCode.SUCCESS:
            header, room_name_bytes, token_bytes = recv_tcrp_message(client_socket)     # サーバーからの応答
            response_room_name = room_name_bytes.decode("utf-8")
            host_token = token_bytes.decode("utf-8")

            if header.operation != operation or header.state != 2 or room_name != response_room_name:      # レスポンスヘッダーの検証
                raise ValueError("不正なレスポンスです")

            print(f"{room_name}を作成しました。")
            print(f"あなたのトークンは{host_token}です。")

        elif status_code == StatusCode.ROOM_ALREADY_EXISTS:
            print("ルームが既に存在します。")

except ConnectionError as error:
    print(f"サーバーとの接続が切れました。: {error}")

except KeyboardInterrupt:
    print("\nチャットを終了します。")