import pytest
from gptdb.core.interface.storage import InMemoryStorage
from gptdb.util.serialization.json_serialization import JsonSerializer


@pytest.fixture
def serializer():
    return JsonSerializer()


@pytest.fixture
def in_memory_storage(serializer):
    return InMemoryStorage(serializer)
