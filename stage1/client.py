import socket
import threading

from protocol import encode_message, decode_message


SERVER_ADDRESS = ("127.0.0.1", 9001)

BUFFER_SIZE = 4096


def receive_messages(client_socket: socket.socket) -> None:
    """データの受信処理と表示をする"""

    while True:
        try:
            received_bytes, _ = client_socket.recvfrom(BUFFER_SIZE)

            received_username, received_message = decode_message(received_bytes)

            print(
                "\n\nメッセージを受信しました。\n"
                f"ユーザー: {received_username}\n"
                f"内容: {received_message}\n"  
            )

        except (ValueError, UnicodeDecodeError) as error:
            print(f"不正なデータを受信しました: {error}")

        except OSError:
            # ソケットが閉じられて受信できなくなった場合
            break


try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:

        print("チャットを開始します。")

        while True:
            username = input("ユーザー名を入力してください。\n> ").strip()

            if not username:
                print("ユーザー名が入力されていません")
                continue

            break

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
        receive_thread.start()

        print("メッセージを入力してください。")

        while True:
            sending_message = input("> ")

            try:
                sending_bytes = encode_message(username, sending_message)
            except ValueError as error:
                print(f"メッセージを送信出来ません: {error}")
                continue

            if len(sending_bytes) > BUFFER_SIZE:
                print(
                    "送信データが大きすぎます。"
                    f"最大{BUFFER_SIZE}バイト、"
                    f"現在{len(sending_bytes)}バイトです。"
                )
                continue

            client_socket.sendto(sending_bytes, SERVER_ADDRESS)

except KeyboardInterrupt:
    print("\nチャットを終了します。") 