import socket

from protocol import decode_message


SERVER_PORT = 9001
SERVER_ADDRESS = "0.0.0.0"

BUFFER_SIZE = 4096

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

        print("UDPサーバーを起動します。")
        print(f"{SERVER_ADDRESS} : {SERVER_PORT}")

        # 送信してきたクライアントのアドレスを集合として保存する
        clients = set()

        while True:
            data_bytes, client_address = server_socket.recvfrom(BUFFER_SIZE)

            # 不正なデータが送られてきた場合でもサーバーが停止しないようにする
            try:
                username, message = decode_message(data_bytes)
            except (ValueError, UnicodeDecodeError) as error:
                print(f"Error: {error}")
                continue

            clients.add(client_address)

            print(f"{username} から {len(data_bytes)}バイトのデータを受信しました。")
            print(f"Message: {message}")

            # 全クライアントにメッセージを送信
            for destination_address in clients:
                server_socket.sendto(data_bytes, destination_address)

            print("全クライアントにメッセージを送信しました。")

except KeyboardInterrupt:
    print("\nサーバーを停止します。")


