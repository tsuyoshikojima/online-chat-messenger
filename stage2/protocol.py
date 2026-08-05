from dataclasses import dataclass


HEADER_SIZE = 32    # プロトコルの仕様でヘッダーは32バイト


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

