import pytest

from micropack import FileHandler, Header, MessageBuffer


@pytest.fixture
def buffer():
    buffer_size = 55
    header = Header
    io_handler = FileHandler

    return MessageBuffer(buffer_size, header, io_handler)


def test_message_buffer_should_have_correct_attributes(buffer):
    # Given
    buffer_size = 55
    header = Header
    io_handler = FileHandler

    # Then
    assert buffer.size == 55
    assert buffer.header == header
    assert buffer.packet_size == buffer_size - header.size
    assert buffer.io_handler == io_handler


@pytest.mark.parametrize(
    "message, packet_count",
    [
        (bytearray(list(range(0, 150))), 3),
        (bytearray(list(range(0, 52))), 1),
        (bytearray(list(range(0, 55))), 2),
    ],
)
def test_message_buffer_should_encode_message(buffer, message, packet_count):
    # When
    packets = buffer.encode(message)

    # Then
    assert len(packets) == packet_count
    assert isinstance(packets, list)

    for id, packet in enumerate(packets):
        assert len(packet) <= buffer.size
        if len(packet) < buffer.size:
            remaining_bytes = message[
                (id) * (buffer.size) - (buffer.header.size * (id + 1)) :
            ]
            assert len(packet) == len(remaining_bytes)


@pytest.mark.parametrize(
    "message,",
    [
        bytearray(list(range(0, 150))),
        b"This is a test message",
    ],
)
def test_message_buffer_should_decode_message(message, buffer):
    # Given
    packets = buffer.encode(message)

    # When
    decoded_message = buffer.decode(packets)

    # Then
    assert decoded_message == message


def test_message_buffer_should_raise_exception_when_message_is_empty(buffer):
    # Given
    message = bytearray()

    # Then
    with pytest.raises(Exception):
        buffer.encode(message)


@pytest.mark.parametrize(
    "message",
    [
        bytearray(list(range(0, 150))),
        bytearray(list(range(0, 52))),
        bytearray(list(range(0, 55))),
        b"This is a very long test message spanning multiple packets",
    ],
)
def test_message_buffer_should_read_file(buffer, tmp_path, message):
    # Given
    file_path = tmp_path / "test.pack"
    buffer.io_handler = FileHandler(file_path)
    packets = buffer.encode(message)

    # When
    for packet in packets:
        buffer.write(packet)

    # Then
    read_packets = buffer.read()

    assert read_packets == packets
    assert buffer.decode(read_packets) == message
