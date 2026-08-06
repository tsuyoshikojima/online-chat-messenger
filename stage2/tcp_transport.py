import socket


from protocol import (
    Header,
    HEADER_SIZE,
    decode_header,
)


def recv_exact_bytes(connection: socket.socket, data_size: int) -> bytes:
    """指定されたデータサイズを受信する"""

    if data_size < 0:
        raise ValueError("データサイズは0以上である必要があります。")

    remaining_size = data_size

    output_data_bytes = bytearray()  # 受信したデータを追加できる可変なバイト列
    
    while remaining_size > 0:
        received_data_bytes = connection.recv(remaining_size)

        if not received_data_bytes:
            raise ConnectionError("データ受信中に切断されました")

        remaining_size -= len(received_data_bytes)  # 残りのデータ量を更新

        output_data_bytes.extend(received_data_bytes)

    return bytes(output_data_bytes)


def recv_tcrp_message(connection: socket.socket) -> tuple[Header, bytes, bytes]:
    """送信されたバイトデータをヘッダー、ルーム名、ペイロードに分割して受信"""

    header_bytes = recv_exact_bytes(
        data_size=HEADER_SIZE,
        connection=connection
    )

    # bodyのパケットを受信するためにheaderを解析する
    header = decode_header(header_bytes)

    room_name_size = header.room_name_size
    operation_payload_size = header.operation_payload_size

    room_name_bytes = recv_exact_bytes(
        data_size=room_name_size,
        connection=connection
    )

    operation_payload_bytes = recv_exact_bytes(
        data_size=operation_payload_size,
        connection=connection
    )

    return header, room_name_bytes, operation_payload_bytes