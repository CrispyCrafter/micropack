def generate_crc(bytes: list) -> int:
    """
    Function that accepts a bytearray.
    Bytes are in hex format.
    The function will generate a CRC for the bytearray.
    :param bytes: A list of bytes to generate a CRC for.
    :return: The CRC of the bytearray.
    """
    crc = 0
    for byte in bytes:
        crc = crc ^ byte
    return crc


class HeaderMeta(type):
    def __repr__(cls) -> str:
        """Returns a string representation of the class."""
        return f"{cls.__name__} -> ({cls.headers})"

    def __new__(cls, name, bases, dct):
        """
        Creates a new class.
        :param name: The name of the class.
        :param bases: The bases of the class.
        :param dct: The dictionary of the class.
        """

        cls = super().__new__(cls, name, bases, dct)
        cls.headers = [
            i.split(f"{cls.prefix}_")[-1]
            for i in cls.__dict__.keys()
            if i.startswith(f"{cls.prefix}_")
        ]
        cls.size = len(cls.headers)

        return cls


class Header(metaclass=HeaderMeta):
    prefix = "header"
    header_id = 0
    header_count = 1
    header_crc = 2

    @classmethod
    def generate(cls, packet: list, packet_id: int, packet_count: int) -> list:
        """
        Generates a header for a packet.
        :param packet: The packet to generate a header for.
        :param packet_id: The packet id.
        :param packet_count: The packet count.
        """
        header = bytearray(cls.size)
        header[cls.header_id] = packet_id
        header[cls.header_count] = packet_count
        header[cls.header_crc] = generate_crc(packet)
        return header

    @classmethod
    def get(cls, header, packet):
        """
        Gets a header from a packet.
        :param header: The header to get.
        :param packet: The packet to get the header from.
        """
        pos = getattr(cls, f"{cls.prefix}_{header}")
        return packet[pos]

    @classmethod
    def validate(cls, packet, values):
        """
        Validates a header.
        :param header: The header to validate.
        :param packet: The packet to validate the header from.
        :param value: The value to validate the header against.
        """
        for header, value in zip(cls.headers, values):
            check = cls.get(header, packet)
            assert (
                check == value
            ), f"Invalid header {header}. Expected header {check}, got {value}"
