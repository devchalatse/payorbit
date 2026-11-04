"""Business, customer and invoice API tests."""

from datetime import date, timedelta


def create_business_and_customer(client):
    business_response = client.post(
        "/api/v1/businesses",
        json={
            "name": "Example Wholesale",
            "registration_number": "2026/123456/07",
            "email": "accounts@example.co.za",
        },
    )
    assert business_response.status_code == 201
    business = business_response.json()

    customer_response = client.post(
        "/api/v1/customers",
        json={
            "business_id": business["id"],
            "name": "Corner Store",
            "email": "buyer@example.co.za",
        },
    )
    assert customer_response.status_code == 201
    return business, customer_response.json()


def test_create_business_and_customer(client):
    business, customer = create_business_and_customer(client)

    assert business["name"] == "Example Wholesale"
    assert customer["business_id"] == business["id"]


def test_create_and_issue_invoice(client):
    business, customer = create_business_and_customer(client)
    response = client.post(
        "/api/v1/invoices",
        json={
            "business_id": business["id"],
            "customer_id": customer["id"],
            "due_date": (date.today() + timedelta(days=14)).isoformat(),
            "currency": "zar",
            "tax_cents": 1500,
            "items": [
                {
                    "description": "Bulk coffee beans",
                    "quantity": "2.5",
                    "unit_price_cents": 10000,
                },
                {
                    "description": "Delivery",
                    "quantity": "1",
                    "unit_price_cents": 2500,
                },
            ],
        },
    )

    assert response.status_code == 201
    invoice = response.json()
    assert invoice["status"] == "draft"
    assert invoice["currency"] == "ZAR"
    assert invoice["subtotal_cents"] == 27500
    assert invoice["tax_cents"] == 1500
    assert invoice["total_cents"] == 29000
    assert len(invoice["items"]) == 2

    issued = client.post(f"/api/v1/invoices/{invoice['id']}/issue")
    assert issued.status_code == 200
    assert issued.json()["status"] == "issued"
    assert issued.json()["issue_date"] == date.today().isoformat()

    duplicate_issue = client.post(f"/api/v1/invoices/{invoice['id']}/issue")
    assert duplicate_issue.status_code == 409


def test_customer_must_belong_to_invoice_business(client):
    _, customer = create_business_and_customer(client)
    other_business = client.post(
        "/api/v1/businesses",
        json={"name": "Other Wholesale", "email": "other@example.co.za"},
    ).json()

    response = client.post(
        "/api/v1/invoices",
        json={
            "business_id": other_business["id"],
            "customer_id": customer["id"],
            "due_date": (date.today() + timedelta(days=3)).isoformat(),
            "items": [{"description": "Item", "quantity": "1", "unit_price_cents": 100}],
        },
    )
    assert response.status_code == 404


def test_invoice_due_date_cannot_be_in_past(client):
    business, customer = create_business_and_customer(client)
    response = client.post(
        "/api/v1/invoices",
        json={
            "business_id": business["id"],
            "customer_id": customer["id"],
            "due_date": (date.today() - timedelta(days=1)).isoformat(),
            "items": [{"description": "Item", "quantity": "1", "unit_price_cents": 100}],
        },
    )
    assert response.status_code == 422


def test_duplicate_business_registration_number_is_rejected(client):
    create_business_and_customer(client)
    response = client.post(
        "/api/v1/businesses",
        json={
            "name": "Duplicate Registration",
            "registration_number": "2026/123456/07",
            "email": "duplicate@example.co.za",
        },
    )
    assert response.status_code == 409


def test_business_read_endpoints(client):
    business, _ = create_business_and_customer(client)

    listed = client.get("/api/v1/businesses")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/businesses/{business['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == business["id"]

    missing = client.get("/api/v1/businesses/00000000-0000-0000-0000-000000000000")
    assert missing.status_code == 404


def test_customer_read_endpoints_and_unknown_business(client):
    business, customer = create_business_and_customer(client)

    listed = client.get(f"/api/v1/customers?business_id={business['id']}")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/customers/{customer['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == customer["id"]

    missing = client.post(
        "/api/v1/customers",
        json={
            "business_id": "00000000-0000-0000-0000-000000000000",
            "name": "Unknown business customer",
        },
    )
    assert missing.status_code == 404


def test_invoice_read_endpoints(client):
    business, customer = create_business_and_customer(client)
    created = client.post(
        "/api/v1/invoices",
        json={
            "business_id": business["id"],
            "customer_id": customer["id"],
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
            "items": [{"description": "Product", "quantity": "1", "unit_price_cents": 1250}],
        },
    )
    invoice = created.json()

    listed = client.get(f"/api/v1/invoices?business_id={business['id']}")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/invoices/{invoice['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == invoice["id"]

    missing = client.get(
        "/api/v1/invoices/00000000-0000-0000-0000-000000000000"
    )
    assert missing.status_code == 404


def test_invoice_requires_existing_business_and_customer(client):
    business, _ = create_business_and_customer(client)
    payload = {
        "business_id": business["id"],
        "customer_id": "00000000-0000-0000-0000-000000000000",
        "due_date": (date.today() + timedelta(days=5)).isoformat(),
        "items": [{"description": "Product", "quantity": "1", "unit_price_cents": 1250}],
    }
    missing_customer = client.post("/api/v1/invoices", json=payload)
    assert missing_customer.status_code == 404

    payload["business_id"] = "00000000-0000-0000-0000-000000000000"
    missing_business = client.post("/api/v1/invoices", json=payload)
    assert missing_business.status_code == 404


def test_invoice_validation_rejects_empty_items_and_negative_price(client):
    business, customer = create_business_and_customer(client)
    base = {
        "business_id": business["id"],
        "customer_id": customer["id"],
        "due_date": (date.today() + timedelta(days=5)).isoformat(),
    }
    empty_items = client.post("/api/v1/invoices", json={**base, "items": []})
    assert empty_items.status_code == 422

    invalid_price = client.post(
        "/api/v1/invoices",
        json={
            **base,
            "items": [{"description": "Invalid", "quantity": "1", "unit_price_cents": -10}],
        },
    )
    assert invalid_price.status_code == 422
