from protocol import (
    HEADER_SIZE,
    Header,
    decode_header,
    encode_header,
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