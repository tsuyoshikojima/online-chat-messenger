import selectors # 複数のソケットを同時に監視するためのモジュール
import socket
import time
from typing import cast

from protocol import encode_message, decode_message


SERVER_ADDRESS = ("127.0.0.1", 9001)
BUFFER_SIZE = 4096

CLIENT_COUNT = 1000
MESSAGE_COUNT = 10

REGISTRATION_INTERVAL = 0.005 # UDPの受信バッファがあふれる可能性があるため1クライアント登録するたびに待つ時間
REGISTRATION_WAIT = 1.0 # 全ての登録データを送った後、サーバー側の処理を待つ時間

RECEIVE_TIMEOUT = 10.0 # 期待するパケットを受信できなくても最大10秒でテストを終了する


def main() -> None:
    clients: list[socket.socket] = [] # 作成したUDPソケットを保存するための空のリスト
    selector = selectors.DefaultSelector() # 複数のソケットを監視するためのオブジェクト

    try:
        print(f"{CLIENT_COUNT}個のクライアントを作成します。")

        # クライアントソケットを作成し、リストに保存
        for _ in range(CLIENT_COUNT):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.bind(("127.0.0.1", 0))
            clients.append(client_socket)

        print("クライアントをサーバーに登録します")

        # 登録データを作成しサーバーに送信
        for index, client_socket in enumerate(clients):
            # 登録データを作成
            registration_data = encode_message(f"load_user_{index}", "__register__")

            client_socket.sendto(registration_data, SERVER_ADDRESS)

            time.sleep(REGISTRATION_INTERVAL)

        time.sleep(REGISTRATION_WAIT)

        for index, client_socket in enumerate(clients):
            client_socket.setblocking(False) # ソケットにデータが届いていなくても次の処理に進めるようにする

            # セレクターにソケットを登録
            selector.register(
                client_socket, # セレクターに登録するソケット
                selectors.EVENT_READ,  # ソケットが読み取り可能なったかを監視する
                data=index # ソケットと一緒にクライアント番号を管理する
            )

        # 予想されるパケット数を計算する
        expected_packets = MESSAGE_COUNT * (CLIENT_COUNT - 1)

        print()
        print("負荷テストを開始します")
        print(f"クライアント数: {CLIENT_COUNT}")
        print(f"送信メッセージ数: {MESSAGE_COUNT}")
        print(f"予想リレーパケット数: {expected_packets}")

        # 送信者と受信記録を準備する
        sender_socket = clients[0] # 最初に作成したクライアントを送信者とする
        test_username = "load-test-sender"

        received_packets: set[tuple[int, str]] = set() # 受信結果を保存する集合

        # 測定開始時刻
        start_time = time.perf_counter()

        # メッセージの数だけサーバーに送信する
        for message_number in range(MESSAGE_COUNT):
            sending_data = encode_message(test_username, f"load-message-{message_number}")
            sender_socket.sendto(sending_data, SERVER_ADDRESS)

        deadline = start_time + RECEIVE_TIMEOUT # 受信期限

        # パケットを受信する
        while len(received_packets) < expected_packets and time.perf_counter() < deadline:
            remaining_time = deadline - time.perf_counter() # 残り時間

            # 読み取り可能なソケットの情報を変数に保存
            events = selector.select(
                timeout=min(
                    0.1, 
                    max(0.0, remaining_time)
                    )
            ) 

            for key, _ in events:
                client_socket = cast(socket.socket, key.fileobj) # ソケットを取得
                client_index = key.data # クライアント番号を取得

                while True:
                    try:
                        received_data, _ = client_socket.recvfrom(BUFFER_SIZE)
                    except BlockingIOError:
                        # ノンブロッキングモードでは、受信データがなくなるとBlockingIOErrorを返す
                        break

                    try:
                        username, message = decode_message(received_data)
                    except (ValueError, UnicodeDecodeError):
                        continue

                    if username == test_username and message.startswith("load-message-"):
                        # 負荷テスト用データであった場合保存する
                        received_packets.add((client_index, message))

        end_time = time.perf_counter() # 終了時刻

        elapsed_time = end_time - start_time # 負荷テストにかかった時間
        received_count = len(received_packets) # 受信したパケットの数
        missing_count = expected_packets - received_count # 届かなかったパケット数

        packets_per_second = received_count / elapsed_time if elapsed_time > 0 else 0.0 # １秒あたりに受信したパケット数

        loss_rate = missing_count / expected_packets * 100 if expected_packets > 0 else 0.0 # 未受信率

        print()
        print("負荷テスト結果")
        print("-----------------------------------")
        print(f"経過時間: {elapsed_time:.3f}秒")
        print(f"予想パケット数: {expected_packets}")
        print(f"受信パケット数: {received_count}")
        print(f"未受信パケット数: {missing_count}")
        print(f"未受信率: {loss_rate:.2f}%")
        print(f"処理速度: {packets_per_second:,.0f}パケット/秒")

        if received_count == expected_packets and packets_per_second >= 10000:
            print("判定: 10000パケット/秒を達成しました。")
        elif packets_per_second >= 10000:
            print("判定: 処理速度は達成しましたが、未受信パケットがあります。")
        else:
            print("判定: 10000パケット/秒には達しませんでした。")

    finally:
        selector.close() # ソケット監視に使ったリソースを解放

        for client_socket in clients:
            # 作成した全ての疑似クライアントを終了する
            client_socket.close()

if __name__ == "__main__":
    main()
