import json

def test_declined_api_flow(client):
    event = {"id": "evt1", "summary": "Sample Event", "start_time": "2025-06-12T10:00:00Z"}

    # Add event to declined
    res = client.post('/delete_declined', json=event)
    assert res.status_code == 200

    # Recover event
    res = client.post('/recover', json=event)
    assert res.status_code == 200

    # Fetch declined page
    res = client.get('/declined')
    assert b"Sample Event" in res.data or b"No declined events" in res.data
