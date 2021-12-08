# state
CHECKING = 0
INSTALLING = 1
COMPLETED = 2
ERROR = 3

# store
status: int = None
update_version: str = None
download_url: str = None
changelog_url: str = None
error_msg: str = None

update_available: bool = False