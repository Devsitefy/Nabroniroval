import uuid


async def test_hotels_crud_and_filters(ac):
    suffix = uuid.uuid4().hex[:8]
    payload = {"title": f"Race Hotel {suffix}", "location": f"Test City {suffix}"}

    created = await ac.post("/hotels", json=payload)
    assert created.status_code == 200
    hotel_id = created.json()["data"]["id"]

    one = await ac.get(f"/hotels/{hotel_id}")
    assert one.status_code == 200
    assert one.json()["data"]["title"] == payload["title"]

    listing = await ac.get(
        "/hotels",
        params={
            "title": "Race Hotel",
            "location": "Test City",
            "date_from": "2027-01-10",
            "date_to": "2027-01-12",
            "page": 1,
            "per_page": 5,
        },
    )
    assert listing.status_code == 200

    put_payload = {"title": f"Updated {suffix}", "location": f"New City {suffix}"}
    updated = await ac.put(f"/hotels/{hotel_id}", json=put_payload)
    assert updated.status_code == 200

    patched = await ac.patch(f"/hotels/{hotel_id}", json={"title": f"Patched {suffix}"})
    assert patched.status_code == 200

    after_patch = await ac.get(f"/hotels/{hotel_id}")
    assert after_patch.status_code == 200
    assert after_patch.json()["data"]["title"] == f"Patched {suffix}"
    assert after_patch.json()["data"]["location"] == f"New City {suffix}"

    deleted = await ac.delete(f"/hotels/{hotel_id}")
    assert deleted.status_code == 200

    missing = await ac.get(f"/hotels/{hotel_id}")
    assert missing.status_code == 404


async def test_hotels_reject_invalid_dates(ac):
    response = await ac.get(
        "/hotels",
        params={"date_from": "2027-01-12", "date_to": "2027-01-10"},
    )
    assert response.status_code == 400

    same_day = await ac.get(
        "/hotels",
        params={"date_from": "2027-01-10", "date_to": "2027-01-10"},
    )
    assert same_day.status_code == 400
