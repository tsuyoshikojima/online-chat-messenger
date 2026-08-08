from enum import IntEnum  # 整数として扱える列挙型
from dataclasses import dataclass


HEADER_SIZE = 32    # プロトコルの仕様でヘッダーは32バイト
MAX_ROOM_NAME_SIZE = 255
MAX_OPERATION_PAYLOAD_SIZE = 2 ** 29    # ヘッダーフィールドのサイズは29バイトで2 ** (8 * 29) - 1　バイトまで表現できるが仕様上2**29を最大値とする


class StatusCode(IntEnum):
    SUCCESS = 0  # 成功時
    ROOM_ALREADY_EXISTS = 1  # 作成したいルームが既に存在するとき
    INVALID_REQUEST = 2  # リクエストが不正な場合
    INTERNAL_ERROR = 3  # サーバー側の不具合


# headerが4つの値を持つためクラスとして管理する
@dataclass  # __init__()などをPythonが自動生成
class Header:
    room_name_size: int
    operation: int
    state: int 
    operation_payload_size: int


def validate_header_fields(room_name_size: int, operation: int, state: int, operation_payload_size: int) -> None:
    """ヘッダーフィールドの値が正しいか検証する"""

    if not 1 <= room_name_size <= MAX_ROOM_NAME_SIZE:
        raise ValueError(f"room_name_sizeは1〜{MAX_ROOM_NAME_SIZE}バイトである必要があります。")

    if operation not in {1, 2}:
        raise ValueError("operationは1か2のどちらかである必要があります。")

    if state not in {0, 1, 2}:
        raise ValueError("stateは0〜2である必要があります。")

    if not 0 <= operation_payload_size <= MAX_OPERATION_PAYLOAD_SIZE:
        raise ValueError(f"operation_payload_sizeは0〜{MAX_OPERATION_PAYLOAD_SIZE}バイトである必要があります。")


def decode_header(data: bytes) -> Header:
    if len(data) != HEADER_SIZE:
        raise ValueError("ヘッダーのサイズが正しくありません")
    
    room_name_size = data[0]
    operation = data[1]
    state = data[2]
    operation_payload_size = int.from_bytes(data[3:HEADER_SIZE], byteorder='big')

    validate_header_fields(
        room_name_size=room_name_size,
        operation=operation,
        state=state,
        operation_payload_size=operation_payload_size
    )

    return Header(
        room_name_size=room_name_size,
        operation=operation,
        state=state,
        operation_payload_size=operation_payload_size
    )


def encode_header(room_name_size: int, operation: int, state: int, operation_payload_size: int) -> bytes:
    validate_header_fields(
        room_name_size=room_name_size,
        operation=operation,
        state=state,
        operation_payload_size=operation_payload_size
    )

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


def encode_packet(operation: int, state: int, room_name: str, operation_payload_bytes: bytes) -> bytes:
    """TCPソケットで送信するためのパケットを組み立てる"""

    room_name_bytes = room_name.encode("utf-8")
    room_name_size = len(room_name_bytes)

    operation_payload_size = len(operation_payload_bytes)

    header_bytes = encode_header(
        room_name_size=room_name_size,
        operation=operation,
        state=state,
        operation_payload_size=operation_payload_size
    )

    body_bytes = encode_body(
        room_name=room_name,
        operation_payload_bytes=operation_payload_bytes
    )

    return header_bytes + body_bytes