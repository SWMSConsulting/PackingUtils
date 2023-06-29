from typing import List
from packutils.data.item import Item
from packutils.data.bin import Bin


class PackingVariant:
    """
    Represents a packing variant containing a list of bins and information about unpacked items.

    Attributes:
        bins (List[Bin]): A list of bins in the packing variant.
        unpacked_items (List[Item]): A list of items that failed to be packed.
        error_messages (List[str]): A list of error messages corresponding to unpacked items.
    """

    def __init__(self):
        self.bins: List[Bin] = []
        self.unpacked_items: List[Item] = []
        self.error_messages: List[str] = []

    def add_bin(self, bin: Bin):
        """
        Add a bin to the packing variant.

        Args:
            bin (Bin): The bin to be added.
        """
        self.bins.append(bin)

    def add_unpacked_item(self, item: Item, error_message: str | None):
        """
        Add an unpacked item along with the corresponding error message (if provided).

        Args:
            item (Item): The item that failed to be packed.
            error_message (str | None): The error message describing the reason for the packing failure.
        """
        self.unpacked_items.append(item)
        if error_message is not None:
            self.error_messages.append(error_message)
