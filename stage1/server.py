import socket

SERVER_PORT = 9001
SERVER_ADDRESS = "0.0.0.0"

BUFFER_SIZE = 4096

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

        print("UDPサーバーを起動します")
        print(f"{SERVER_ADDRESS} : {SERVER_PORT}")

        while True:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)

            print(f"{client_address} から {len(data)}バイト受信しました")

            server_socket.sendto(data, client_address)

            print("クライアントに送り返しました")

except KeyboardInterrupt:
    print("サーバーを停止します")


