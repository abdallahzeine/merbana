def test_settings_get_update_and_requirements(client):
    current = client.get("/api/settings")
    assert current.status_code == 200
    assert current.json()["id"] == 1

    updated = client.put(
        "/api/settings",
        json={"company_name": "Merbana Test"},
    )
    assert updated.status_code == 200
    assert updated.json()["company_name"] == "Merbana Test"

    requirements = client.get("/api/settings/password-requirements")
    assert requirements.status_code == 200
    assert requirements.json()["create_order"] is True


def test_settings_update_single_requirement(client):
    toggled = client.put("/api/settings/password-requirements/create_order?is_required=false")
    assert toggled.status_code == 200
    assert (
        toggled.json()["security"]["password_required_for"]["create_order"] is False
    )
