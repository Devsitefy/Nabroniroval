from unittest.mock import AsyncMock

import pytest

from src.repositories.base import BaseRepository


async def test_delete_without_filters_is_programmer_error():
    repo = BaseRepository(AsyncMock())
    with pytest.raises(ValueError, match="Delete requires filters"):
        await repo.delete()
