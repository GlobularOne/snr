"""
Context for specific mount point
"""

from snr.core.core import path_wrapper

__all__ = (
    "Context",
)


class Context(path_wrapper.PathWrapperBase, path_var_name="_root_directory"):
    """Context for specific mount point

    Context is used to pass information on a mount point around.
    It is used both in payload generation process and extensively by payload.
    It's better than using a simple dictionary because it allows to 
    have depths of knowledge about the mount point (levels), this is required
    because during the payload generation process, the information is discovered in 3 steps
    and this method ensures better access checks

    Attributes:
        level: Current information level about the mount point
    """
    level: int = 0
    _original_target: str
    _device_name: str
    _device_size: int
    _is_device: bool
    _partitions_prefix: str
    _root_directory: str

    def __init__(self, device_name: str):  # pylint: disable=super-init-not-called
        self._device_name = device_name
        self._original_target = device_name

    def to_level_1(self, device_size: int, is_device: bool) -> None:
        """Update the information to level 1

        Args:
            device_size: Size of the device
            is_device: Whatever device_name actually points to a device or is a file
        """
        self.level = 1
        self._device_size = device_size
        self._is_device = is_device

    def to_level_2(self, partitions_prefix: str) -> None:
        """Update the information to level 2

        Args:
            partitions_prefix: Prefix before partitions index
        """
        self.level = 2
        self._partitions_prefix = partitions_prefix

    def to_level_3(self, root_directory: str) -> None:
        """Update information to level 3

        Args:
            root_directory: The path which the partition is mounted
        """
        self.level = 3
        self._root_directory = root_directory

    @property
    def original_target(self) -> str:
        """Original target passed"""
        return self._original_target

    @property
    def device_name(self) -> str:
        """Device name, could be loop"""
        return self._device_name

    @device_name.setter
    def device_name(self, device_name: str) -> None:
        self._device_name = device_name

    @property
    def device_size(self) -> int:
        """Size of the device, could be zero if context is created on a host system"""
        if self.level >= 1:
            return self._device_size
        raise RuntimeError("Context does not yet have device_size")

    @property
    def is_device(self) -> bool:
        """Whatever device_name points to an actual device, not a file"""
        if self.level >= 1:
            return self._is_device
        raise RuntimeError("Context does not yet have is_device")

    @is_device.setter
    def is_device(self, is_device: bool) -> None:
        self._is_device = is_device

    @property
    def partitions_prefix(self) -> str:
        """The prefix in which is needed to access partitions on /dev with device_name"""
        if self.level >= 2:
            return self._partitions_prefix
        raise RuntimeError("Context does not yet have partitions_prefix")

    @property
    def root_directory(self) -> str:
        """The root directory which the context is based on"""
        if self.level >= 3:
            return self._root_directory
        raise RuntimeError("Context does not yet have root_directory")

    def construct_partition_path(self, index: str | int, original_target: bool = False) -> str:
        """Construct a partition file path

        Args:
            index: Partition index in partition table
            original_target: Whatever to use original_target instead of device_name. 
              Use this if you absolutely are sure original_target is not a 
              file and uses the same partition prefix. Defaults to True.

        Returns:
            Path to the requested partition
        """
        if original_target:
            return f"{self.original_target}{self.partitions_prefix}{index}"
        return f"{self.device_name}{self.partitions_prefix}{index}"
