async def test_get_facility(ac):
    facility = await ac.get("/facilities")
    assert facility.status_code == 200


async def create_facility(ac):
    facility = await ac.post("/facilities", json={"title": "Кондиционер"})

    assert facility.status_code == 200
