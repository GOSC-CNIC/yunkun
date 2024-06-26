class BaseConfig:
    KEYS = ()

    def to_dict(self):
        raise NotImplemented('to_dict')

    @classmethod
    def from_dict(cls, data: dict):
        raise NotImplemented('from_dict')

    def __eq__(self, other):
        if type(self) is not type(other):
            return False

        for key in self.KEYS:
            if getattr(self, key) != getattr(other, key):
                return False

        return True


class ServerConfig(BaseConfig):
    KEY_CPU = 'vm_cpu'
    KEY_RAM = 'vm_ram'
    KEY_DISK_SIZE = 'vm_systemdisk_size'
    KEY_FLAVOR_ID = 'vm_flavor_id'           # 针对阿里云，服务端规格ID
    KEY_PUBLIC_IP = 'vm_public_ip'
    KEY_IMAGE_ID = 'vm_image_id'
    KEY_IMAGE_NAME = 'vm_image_name'        # 不重要，不需要放到KEYS中
    KEY_NETWORK_ID = 'vm_network_id'
    KEY_NETWORK_NAME = 'vm_network_name'    # 不重要，不需要放到KEYS中
    KEY_AZONE_ID = 'vm_azone_id'
    KEY_AZONE_NAME = 'vm_azone_name'       # 可用区名称是可变的，不重要，不需要放到KEYS中
    KEYS = (KEY_CPU, KEY_RAM, KEY_DISK_SIZE, KEY_PUBLIC_IP, KEY_IMAGE_ID, KEY_NETWORK_ID, KEY_AZONE_ID, KEY_FLAVOR_ID)

    def __init__(
            self, vm_cpu: int,
            vm_ram: int,
            systemdisk_size: int,
            flavor_id: str,
            public_ip: bool,
            image_id: str,
            image_name: str,
            network_id: str,
            network_name: str,
            azone_id: str,
            azone_name: str
    ):
        """
        :param vm_cpu
        :param vm_ram: GiB
        :param systemdisk_size: Gib
        :param public_ip: 是否是公网ip
        :param image_id:
        :param image_name:
        :param network_id:
        :param network_name:
        :param azone_id: 可用区id
        """
        self.vm_cpu = vm_cpu
        self.vm_ram = vm_ram
        self.vm_systemdisk_size = systemdisk_size
        self.vm_flavor_id = flavor_id
        self.vm_public_ip = public_ip
        self.vm_image_id = image_id
        self.vm_image_name = image_name
        self.vm_network_id = network_id
        self.vm_network_name = network_name
        self.vm_azone_id = azone_id
        self.vm_azone_name = azone_name

    @property
    def vm_ram_mib(self):
        return 1024 * self.vm_ram

    @property
    def vm_ram_gib(self):
        return self.vm_ram

    def to_dict(self):
        return {
            self.KEY_CPU: self.vm_cpu,
            self.KEY_RAM: self.vm_ram,
            self.KEY_DISK_SIZE: self.vm_systemdisk_size,
            self.KEY_PUBLIC_IP: self.vm_public_ip,
            self.KEY_IMAGE_ID: self.vm_image_id,
            self.KEY_IMAGE_NAME: self.vm_image_name,
            self.KEY_NETWORK_ID: self.vm_network_id,
            self.KEY_NETWORK_NAME: self.vm_network_name,
            self.KEY_AZONE_ID: self.vm_azone_id,
            self.KEY_AZONE_NAME: self.vm_azone_name,
            self.KEY_FLAVOR_ID: self.vm_flavor_id
        }

    @classmethod
    def from_dict(cls, config: dict):
        for key in cls.KEYS:
            if key not in config:
                raise Exception(f'无效的云主机配置数据，缺少“{key}”配置数据')

        return cls(
            vm_cpu=config[cls.KEY_CPU],
            vm_ram=config[cls.KEY_RAM],
            systemdisk_size=config[cls.KEY_DISK_SIZE],
            public_ip=config[cls.KEY_PUBLIC_IP],
            image_id=config[cls.KEY_IMAGE_ID],
            image_name=config.get(cls.KEY_IMAGE_NAME, ''),
            network_id=config[cls.KEY_NETWORK_ID],
            network_name=config.get(cls.KEY_NETWORK_NAME, ''),
            azone_id=config[cls.KEY_AZONE_ID],
            azone_name=config.get(cls.KEY_AZONE_NAME, ''),
            flavor_id=config.get(cls.KEY_FLAVOR_ID, '')
        )


class DiskConfig(BaseConfig):
    KEY_DISK_SIZE = 'disk_size'
    KEY_AZONE_ID = 'disk_azone_id'
    KEY_AZONE_NAME = 'disk_azone_name'       # 可用区名称是可变的，不重要，不需要放到KEYS中
    KEYS = (KEY_DISK_SIZE, KEY_AZONE_ID)

    def __init__(self, disk_size: int, azone_id: str, azone_name: str):
        """
        :param disk_size: Gib
        """
        self.disk_size = disk_size
        self.disk_azone_id = azone_id
        self.disk_azone_name = azone_name

    def to_dict(self):
        return {
            self.KEY_DISK_SIZE: self.disk_size,
            self.KEY_AZONE_ID: self.disk_azone_id,
            self.KEY_AZONE_NAME: self.disk_azone_name
        }

    @classmethod
    def from_dict(cls, config: dict):
        for key in cls.KEYS:
            if key not in config:
                raise Exception(f'无效的云硬盘配置数据，缺少“{key}”配置数据')

        return cls(
            disk_size=config[cls.KEY_DISK_SIZE],
            azone_id=config[cls.KEY_AZONE_ID],
            azone_name=config.get(cls.KEY_AZONE_NAME, '')
        )


class BucketConfig(BaseConfig):
    def to_dict(self):
        return {}

    @classmethod
    def from_dict(cls, config: dict):
        return cls()


class ScanConfig(BaseConfig):
    KEY_NAME = 'name'
    KEY_HOST_ADDR = 'host_addr'
    KEY_WEB_URL = 'web_url'
    KEY_REMARK = 'remark'
    KEYS = (KEY_NAME, KEY_HOST_ADDR, KEY_WEB_URL)

    def __init__(self, name: str, host_addr: str, web_url: str, remark: str = ''):
        """
        :name: 任务名称
        :host_addr: 有效不为空时，表示订购host扫描任务
        :web_url: 有效不为空时，表示订购web扫描任务
        """
        self.name = name.strip(' ')
        self.host_addr = host_addr.strip(' ')
        self.web_url = web_url.strip(' ')
        self.remark = remark

    def to_dict(self):
        return {
            self.KEY_NAME: self.name,
            self.KEY_HOST_ADDR: self.host_addr,
            self.KEY_WEB_URL: self.web_url,
            self.KEY_REMARK: self.remark
        }

    @classmethod
    def from_dict(cls, config: dict):
        for key in cls.KEYS:
            if key not in config:
                raise Exception(f'无效的安全扫描配置数据，缺少“{key}”配置数据')

        return cls(
            name=config[cls.KEY_NAME],
            host_addr=config[cls.KEY_HOST_ADDR],
            web_url=config[cls.KEY_WEB_URL],
            remark=config.get(cls.KEY_REMARK, '')
        )


class ServerSnapshotConfig(BaseConfig):
    KEY_SEVER_ID = 'server_id'
    KEY_DISK_SIZE = 'systemdisk_size'
    KEY_AZONE_ID = 'azone_id'
    KEY_SNAPSHOT_NAME = 'snapshot_name'
    KEY_SNAPSHOT_DESC = 'snapshot_desc'
    KEYS = (KEY_SEVER_ID, KEY_DISK_SIZE, KEY_AZONE_ID, KEY_SNAPSHOT_NAME, KEY_SNAPSHOT_DESC)

    def __init__(self, server_id: str, systemdisk_size: int, azone_id: str, snapshot_name: str, snapshot_desc: str):
        """
        :param server_id: 云主机id
        :param systemdisk_size: Gib
        :param azone_id: 可用区id
        :param snapshot_name: 快照名称
        :param snapshot_desc: 快照描述备注
        """
        self.server_id = server_id
        self.systemdisk_size = systemdisk_size
        self.azone_id = azone_id
        self.snapshot_name = snapshot_name
        self.snapshot_desc = snapshot_desc

    def to_dict(self):
        return {
            self.KEY_SEVER_ID: self.server_id,
            self.KEY_DISK_SIZE: self.systemdisk_size,
            self.KEY_AZONE_ID: self.azone_id,
            self.KEY_SNAPSHOT_NAME: self.snapshot_name,
            self.KEY_SNAPSHOT_DESC: self.snapshot_desc
        }

    @classmethod
    def from_dict(cls, config: dict):
        for key in cls.KEYS:
            if key not in config:
                raise Exception(f'无效的云主机配置数据，缺少“{key}”配置数据')

        return cls(
            server_id=config[cls.KEY_SEVER_ID],
            systemdisk_size=config[cls.KEY_DISK_SIZE],
            azone_id=config[cls.KEY_AZONE_ID],
            snapshot_name=config[cls.KEY_SNAPSHOT_NAME],
            snapshot_desc=config[cls.KEY_SNAPSHOT_DESC]
        )
