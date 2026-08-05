from dataclasses import dataclass


HEADER_SIZE = 32    # プロトコルの仕様でヘッダーは32バイト
MAX_ROOM_NAME_SIZE = 255
MAX_OPERATION_PAYLOAD_SIZE = 2 ** 29    # ヘッダーフィールドのサイズは29バイトで2 ** (8 * 29) - 1　バイトまで表現できるが仕様上2**29を最大値とする

# headerが4つの値を持つためクラスとして管理する
@dataclass  # __init__()などをPythonが自動生成
class Header:
    room_name_size: int
    operation: int
    state: int 
    operation_payload_size: int


def decode_header(data: bytes) -> Header:
    if len(data) != HEADER_SIZE:
        raise ValueError("ヘッダーのサイズが正しくありません")
    
    room_name_size = data[0]
    operation = data[1]
    state = data[2]
    operation_payload_size = int.from_bytes(data[3:HEADER_SIZE], byteorder='big')

    return Header(room_name_size, operation, state, operation_payload_size)


def encode_header(room_name_size: int, operation: int, state: int, operation_payload_size: int) -> bytes:
    if room_name_size > 255 or room_name_size <= 0:
        raise ValueError("room_name_sizeは1〜255バイトである必要があります。")

    if operation != 1 and operation != 2:
        raise ValueError("operationは1か2である必要があります。")

    if state != 0 and state != 1 and state != 2:
        raise ValueError("stateは0〜2である必要があります。")

    if operation_payload_size < 0 or operation_payload_size >= (2 ** 29):
        raise ValueError(f"operation_payload_sizeは{2 ** 29 - 1}バイト以下である必要があります")

    room_name_size_bytes = room_name_size.to_bytes(1, byteorder='big')
    operation_bytes = operation.to_bytes(1, byteorder='big')
    state_bytes = state.to_bytes(1, byteorder='big')
    operation_payload_size_bytes = operation_payload_size.to_bytes(29, byteorder='big')

    return room_name_size_bytes + operation_bytes + state_bytes + operation_payload_size_bytes


def encode_body(room_name: str, operation_payload_bytes: bytes) -> bytes:
    """TCPボディを組み立てる"""

    if len(operation_payload_bytes) > MAX_OPERATION_PAYLOAD_SIZE:
        raise ValueError("ペイロードのサイズが大きすぎます。")

    room_name_bytes = room_name.encode("utf-8")

    if not 1 <= len(room_name_bytes) <= MAX_ROOM_NAME_SIZE:
        raise ValueError(f"ルーム名は1〜{MAX_ROOM_NAME_SIZE}バイトである必要があります。")

    return room_name_bytes + operation_payload_bytes


def decode_body(data: bytes, room_name_size: int, operation_payload_size: int) -> tuple[str, bytes]:
    """バイトデータのボディをルーム名とペイロードに分割する"""

    if len(data) != room_name_size + operation_payload_size:
        raise ValueError("ボディサイズとヘッダーフィールドの値が一致しません。")

    room_name_bytes = data[:room_name_size]
    operation_payload_bytes = data[room_name_size:]

    room_name = room_name_bytes.decode("utf-8")

    return room_name, operation_payload_bytes