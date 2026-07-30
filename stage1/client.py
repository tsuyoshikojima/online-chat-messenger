import socket

SERVER_ADDRESS = ("127.0.0.1", 9001)

BUFFER_SIZE = 4096

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:

        while True:
            message = input("メッセージを入力してください\n> ")

            message_bytes = message.encode("utf-8")

            client_socket.sendto(message_bytes, SERVER_ADDRESS)

            data_bytes, server_address = client_socket.recvfrom(BUFFER_SIZE)

            print(f"サーバーからデータを受信しました: {data_bytes.decode('utf-8')}")

except KeyboardInterrupt:
    print("\nチャットを終了します")