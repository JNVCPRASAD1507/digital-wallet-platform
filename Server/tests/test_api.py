def test_health(client):
    r=client.get("/health"); assert r.status_code==200; assert r.json()["status"]=="ok"
def test_auth_required(client):
    assert client.get("/api/wallets").status_code in (401,422)
def test_transfer_requires_auth(client):
    r=client.post("/api/transfers",json={"sender_wallet_id":"00000000-0000-0000-0000-000000000001","receiver_wallet_id":"00000000-0000-0000-0000-000000000002","amount":"100"})
    assert r.status_code in (401,422)
