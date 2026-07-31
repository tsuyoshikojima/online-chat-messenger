import socket

from protocol import encode_message, decode_message


SERVER_ADDRESS = ("127.0.0.1", 9001)

BUFFER_SIZE = 4096

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:

        print("チャットを開始します。")

        while True:
            username = input("ユーザー名を入力してください。\n> ").strip()

            if not username:
                print("ユーザー名が入力されていません")
                continue

            break

        while True:
            sending_message = input("メッセージを入力してください。\n> ")

            sending_bytes = encode_message(username, sending_message)
            client_socket.sendto(sending_bytes, SERVER_ADDRESS)

            received_bytes, _ = client_socket.recvfrom(BUFFER_SIZE)
            received_username, received_message = decode_message(received_bytes)

            print(
                "メッセージを受信しました。\n"
                f"ユーザー: {received_username}\n"
                f"内容: {received_message}"  
            )

except KeyboardInterrupt:
    print("\nチャットを終了します。")