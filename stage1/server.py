import socket
import time

from protocol import decode_message


SERVER_PORT = 9001
SERVER_ADDRESS = "0.0.0.0"

BUFFER_SIZE = 4096

CLIENT_TIMEOUT = 30.0

clients: dict[tuple[str, int], float] = {}


def remove_timed_out_clients(clients: dict[tuple[str, int], float]) -> None:
    current_time = time.monotonic()

    timed_out_clients = [address for address, last_seen in clients.items() if current_time - last_seen >= CLIENT_TIMEOUT]

    for address in timed_out_clients:
        del clients[address]
        print(f"{address}をタイムアウトにより削除しました。")
        
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

        print("UDPサーバーを起動します。")
        print(f"{SERVER_ADDRESS} : {SERVER_PORT}")

        # 一定時間データを受信しなかった場合でも、例外を発生させて処理を進める
        server_socket.settimeout(1.0)

        while True:
            try:
                data_bytes, client_address = server_socket.recvfrom(BUFFER_SIZE)

                # 不正なデータが送られてきた場合でもサーバーが停止しないようにする
                try:
                    username, message = decode_message(data_bytes)
                except (ValueError, UnicodeDecodeError) as error:
                    print(f"Error: {error}")
                    continue

                clients[client_address] = time.monotonic()

                print(f"{username} から {len(data_bytes)}バイトのデータを受信しました。")
                print(f"Message: {message}")

                # データを送信してきたクライアント以外の全クライアントにメッセージを送信
                sent_count = 0
                for destination_address in clients:
                    if destination_address != client_address:
                        server_socket.sendto(data_bytes, destination_address)
                        sent_count += 1

                print(f"{sent_count}件のクライアントにメッセージを送信しました。")
            except socket.timeout:
                pass
            finally:
                # 不正なデータが送られても関数を実行できるようにする
                remove_timed_out_clients(clients)
            
except KeyboardInterrupt:
    print("\nサーバーを停止します。")