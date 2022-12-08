import os


class FileHandler:
    def __init__(self, file_path: str = None) -> None:
        """
        Creates a new file handler.
        :param file_path: The path to the file.
        """
        self.file_path = file_path or "upack.txt"
        if not os.path.exists(self.file_path):
            open(self.file_path, "w").close()

    def read(self) -> list:
        """
        Reads the file.
        File contents are split into packers based on newlines.
        """
        with open(self.file_path, "rb") as file:
            return file.read().split(b"\n\n")[:-1]

    def write(self, packet: list) -> None:
        """
        Writes a packet to the file.
        Packets are separated by two newlines.
        :param packet: The packet to write.
        """
        with open(self.file_path, "ab") as file:
            file.write(packet + b"\n\n")

    def purge(self):
        """
        Purges the file.
        """
        open(self.file_path, "w").close()
