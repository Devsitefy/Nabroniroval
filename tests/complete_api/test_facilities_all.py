import uuid


async def test_facilities_get_and_post(ac):
    title = f"Facility-{uuid.uuid4().hex[:8]}"
    created = await ac.post("/facilities", json={"title": title})
    assert created.status_code == 200
    assert created.json()["data"]["title"] == title

    listing = await ac.get("/facilities")
    assert listing.status_code == 200
    assert any(item["title"] == title for item in listing.json())
