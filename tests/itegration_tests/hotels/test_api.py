async def test_get_hotels(ac):
    hotel = await ac.get(
        "/hotels", params={"date_from": "2026-09-10", "date_to": "2026-09-30"}
    )
    print(hotel.json())

    assert hotel.status_code == 200
