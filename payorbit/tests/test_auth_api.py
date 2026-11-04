"""Authentication and business tenant-isolation tests."""

from datetime import date, timedelta


TEST_PASSWORD = "test-only-passphrase-123456!"


def register(client, email, business_name, registration_number):
    return client.post(
        "/api/v1/auth/register",
        json={
            "business_name": business_name,
            "business_registration_number": registration_number,
            "business_email": f"{business_name.lower().replace(' ', '')}@example.co.za",
            "full_name": "Test Owner",
            "email": email,
            "password": TEST_PASSWORD,
        },
    )


def authenticate(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})


def test_register_login_and_current_user(client):
    created = register(client, "owner@example.co.za", "Owner Business", "REG-OWNER")
    assert created.status_code == 201
    body = created.json()
    assert body["user"]["email"] == "owner@example.co.za"
    assert body["businesses"][0]["role"] == "owner"
    assert body["expires_in"] == 1800

    authenticate(client, body["access_token"])
    current = client.get("/api/v1/auth/me")
    assert current.status_code == 200
    assert current.json()["id"] == body["user"]["id"]

    logged_in = client.post(
        "/api/v1/auth/login",
        json={"email": "OWNER@example.co.za", "password": TEST_PASSWORD},
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["user"]["id"] == body["user"]["id"]


def test_login_rejects_wrong_password_and_unknown_user(client):
    register(client, "owner@example.co.za", "Owner Business", "REG-OWNER")
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.co.za", "password": "incorrect-passphrase"},
    )
    unknown_user = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.co.za", "password": "incorrect-passphrase"},
    )
    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()


def test_protected_routes_reject_missing_or_invalid_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    client.headers.update({"Authorization": "Bearer definitely-not-a-jwt"})
    assert client.get("/api/v1/auth/me").status_code == 401


def test_business_data_is_isolated_between_users(client):
    first = register(client, "first@example.co.za", "First Business", "REG-FIRST").json()
    second = register(client, "second@example.co.za", "Second Business", "REG-SECOND").json()
    first_business = first["businesses"][0]["id"]

    authenticate(client, first["access_token"])
    customer = client.post(
        "/api/v1/customers",
        json={"business_id": first_business, "name": "First Customer"},
    )
    assert customer.status_code == 201
    first_customer_id = customer.json()["id"]

    authenticate(client, second["access_token"])
    assert client.get("/api/v1/businesses").json()[0]["id"] == second["businesses"][0]["id"]
    assert client.get(f"/api/v1/businesses/{first_business}").status_code == 404
    assert client.get(f"/api/v1/customers?business_id={first_business}").status_code == 404
    assert client.get(f"/api/v1/customers/{first_customer_id}").status_code == 404

    invoice = client.post(
        "/api/v1/invoices",
        json={
            "business_id": first_business,
            "customer_id": first_customer_id,
            "due_date": (date.today() + timedelta(days=3)).isoformat(),
            "items": [{"description": "Goods", "quantity": "1", "unit_price_cents": 1000}],
        },
    )
    assert invoice.status_code == 404


def test_authenticated_user_can_create_an_additional_business(client):
    account = register(client, "owner@example.co.za", "Owner Business", "REG-OWNER").json()
    authenticate(client, account["access_token"])
    response = client.post(
        "/api/v1/businesses",
        json={
            "name": "Second Owned Business",
            "registration_number": "REG-SECOND",
            "email": "second-business@example.co.za",
        },
    )
    assert response.status_code == 201
    listed = client.get("/api/v1/businesses")
    assert listed.status_code == 200
    assert len(listed.json()) == 2
