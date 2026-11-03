from src.exceptions import ObjectNotFoundException
from src.utils.db_manager import DBManager


class BaseService:
    db: DBManager | None
    not_found_exception = ObjectNotFoundException

    def __init__(self, db: DBManager | None = None):
        self.db = db
