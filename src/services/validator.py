from datetime import date

from src.exceptions import ObjectNotFoundException, CheckInDateEqualsCheckOutException, \
    CheckInDateLaterThanCheckOutException
from src.services.base import BaseService


class ValidatorService(BaseService):
    async def __call__(self, repository, **kwargs):
        try:
            return await repository.get_one(**kwargs)
        except ObjectNotFoundException:
            raise repository.not_found_exception

    @staticmethod
    def date_validate(date_from: date, date_to: date):
        if date_from > date_to:
            raise CheckInDateLaterThanCheckOutException

        if date_from == date_to:
            raise CheckInDateEqualsCheckOutException