from protocol import (
    HEADER_SIZE,
    Header,
    decode_header,
    encode_header,
    decode_body,
    encode_body
)


def test_encode_and_decode_header() -> None:
    header_bytes = encode_header(
        room_name_size=45,
        operation=1,
        state=0,
        operation_payload_size=405,
    )

    assert len(header_bytes) == HEADER_SIZE

    header = decode_header(header_bytes)

    assert header == Header(
        room_name_size=45,
        operation=1,
        state=0,
        operation_payload_size=405,
    )


def test_encode_and_decode_body() -> None:
    room_name = "テストルーム"
    room_name_bytes = room_name.encode("utf-8")
    operation_payload_bytes = "Tsuyoshi".encode("utf-8")

    body_bytes = encode_body(room_name, operation_payload_bytes)

    decoded_room_name, decoded_payload_bytes = decode_body(body_bytes, len(room_name_bytes), len(operation_payload_bytes))

    assert room_name == decoded_room_name
    assert operation_payload_bytes == decoded_payload_bytes