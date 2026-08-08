import json
import socket


from tcp_transport import(
    recv_tcrp_message
)


from protocol import(
    StatusCode,
    encode_packet,
)


from room_manager import (
    RoomManager,
    RoomAlreadyExistsError
)


SERVER_ADDRESS = "0.0.0.0"  # 全てのネットワークインターフェースから受け付ける
SERVER_PORT = 9001


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    print("サーバーを起動します。")

    server_socket.listen(1)

    rooms = RoomManager()

    while True:
        connection, client_address = server_socket.accept()

        try:
            with connection:
                header, room_name_bytes, operation_payload_bytes = recv_tcrp_message(connection=connection)

                if header.operation != 1 or header.state != 0:  # ルーム作成時のヘッダー検証
                    print("不正なルーム作成リクエストです")
                    continue

                room_name = room_name_bytes.decode("utf-8")

                try:
                    operation_payload = json.loads(operation_payload_bytes.decode("utf-8"))  # jsonをPythonの辞書に変換
                    user_name = operation_payload["user_name"]
                    password = operation_payload["password"]

                    if not isinstance(user_name, str) or not user_name.strip():
                        raise ValueError("不正なユーザー名です。")

                    if password is not None and not isinstance(password, str):
                        raise ValueError("passwordが不正です。")

                    status_code = StatusCode.SUCCESS
                    
                except (
                    json.JSONDecodeError,  # 不正なJSON
                    KeyError,  # 必要なキーがない場合
                    TypeError,  # jsonを解析後、辞書でなかった場合など
                    ValueError
                ):
                    status_code = StatusCode.INVALID_REQUEST
                
                if status_code == StatusCode.SUCCESS:
                    # ルーム作成
                    try:
                        host_token = rooms.create_room(
                            room_name=room_name,
                            user_name=user_name,
                            ip_address=client_address[0],  # ポート番号はUDPで通信するときに変わってしまうため不要
                            password=password
                        )

                        print(
                            f"{room_name}の作成に成功しました。\n"
                        )

                    except RoomAlreadyExistsError:
                        status_code = StatusCode.ROOM_ALREADY_EXISTS

                    except ValueError:
                        status_code = StatusCode.INVALID_REQUEST

                response_packet = encode_packet(
                    operation=1,
                    state=1,
                    room_name=room_name,
                    operation_payload_bytes=status_code.to_bytes(
                        length=1,
                        byteorder="big"
                    )
                )

                connection.sendall(response_packet)     # ペイロードにステータスコードを載せてクライアントに送信

                if status_code == StatusCode.SUCCESS:
                    final_packet = encode_packet(
                        operation=1,
                        state=2,
                        room_name=room_name,
                        operation_payload_bytes=host_token.encode("utf-8")
                    )

                    connection.sendall(final_packet)        # トークンを送信

        except ConnectionError as error:
            print(f"クライアントとの接続が切断されました。: {error}")

        except UnicodeDecodeError as error:
            print(f"文字列のデコードに失敗しました。: {error}")

        except ValueError as error:
            print(f"不正なTCRPメッセージを受信しました。: {error}")

        except OSError as error:
            print(f"ソケット通信でエラーが発生しました。: {error}")