import pytest

from micropack.protocol import Header, HeaderMeta, generate_crc


def test_header_should_have_correct_attributes():
    assert Header.prefix == "header"
    assert Header.headers == ["id", "count", "crc"]
    assert Header.size == 3


def test_header_should_have_correct_repr():
    assert repr(Header) == "Header -> (['id', 'count', 'crc'])"


def test_header_should_have_correct_new():
    # Given
    class TestHeader(metaclass=HeaderMeta):
        prefix = "test"
        test_id = 0
        test_count = 1
        test_crc = 2
        test_dummy = 3

    assert TestHeader.prefix == "test"
    assert TestHeader.headers == ["id", "count", "crc", "dummy"]
    assert TestHeader.size == 4


@pytest.mark.parametrize(
    "packet, packet_id, packet_count",
    [
        (bytearray([1, 2, 3, 4, 5]), 1, 2),
        (b"This is a test string", 1, 1),
    ],
)
def test_header_should_have_correct_generate(packet, packet_id, packet_count):
    # Given
    header = Header.generate(packet, packet_id, packet_count)
    crc = generate_crc(packet)
    message = header + packet

    # Then
    assert header == bytearray([packet_id, packet_count, crc])
    Header.validate(message, [packet_id, packet_count, crc])
