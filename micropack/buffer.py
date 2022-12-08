from micropack.protocol import Header, generate_crc


class MessageBuffer:
    def __init__(self, buffer_size: int = 55, header=None, io_handler=None) -> None:
        """
        Creates a new message buffer.
        :param buffer_size: The size of the buffer.
        :param header: The header to use.
        :param io_handler: The IO handler to use.
        """
        self.size = buffer_size
        self.header = header or Header
        self.packet_size = self.size - self.header.size

        self.io_handler = io_handler

    def decode(self, packets: list) -> list:
        """
        Decodes a list of packets into a list of bytes.
        :param packets: The packets to decode.
        """
        payload = b""
        for packet in packets:
            payload += self.get_payload(packet)
        return payload

    def encode(self, message: list) -> list:
        """
        Encodes a list of bytes into a list of packets.
        :param message: The message to encode.
        """
        assert message, "Message cannot be empty"

        packets = []
        packet_id = 1
        packet_count = len(message) // self.packet_size

        if len(message) % self.packet_size != 0:
            packet_count += 1

        for i in range(0, len(message), self.packet_size):
            packet = message[i : i + self.packet_size]
            header = self.header.generate(packet, packet_id, packet_count)
            packets.append(header + packet)
            packet_id += 1
        self.validate_packets(packets)

        return packets

    def get_payload(self, packet):
        """
        Gets the payload from a packet.
        """
        return packet[self.header.size :]

    def validate_packet(self, packet: list, id, count) -> None:
        """
        Validates a packet.
        :param packet: The packet to validate.
        :param id: The id of the packet.
        :param count: The count of the packet.
        """
        payload = self.get_payload(packet)
        crc = generate_crc(payload)
        self.header.validate(packet, [id, count, crc])

    def validate_packets(self, packets: list) -> None:
        """
        Validates a list of packets.
        :param packets: The packets to validate.
        """
        packet_count = len(packets)
        for id, packet in enumerate(packets):
            self.validate_packet(packet, id + 1, packet_count)

    def read(self, purge_on_read=True) -> list:
        """
        Reads a message from the io buffer.
        """
        packets = self.io_handler.read()
        if not packets:
            print("No packets in io buffer")
            return

        expected_packet_count = self.header.get("count", packets[0])

        if len(packets) < expected_packet_count:
            print("Buffer is missing packets")
            return
        elif len(packets) > expected_packet_count:
            print("Buffer has extra packets")
            purge_on_read = True

        if purge_on_read:
            self.io_handler.purge()

        try:
            self.validate_packets(packets)
        except AssertionError as e:
            print(f"File buffer corrupted with error: {e}")
            return

        return packets

    def write(self, packet: list) -> None:
        """
        Writes a message to the io buffer.
        """
        return self.io_handler.write(packet)
