import json
from app import app

# Use Flask test client to exercise endpoints and print readable results
client = app.test_client()

def print_response(resp):
    print(f"STATUS: {resp.status_code}")
    try:
        data = resp.get_json()
        print(json.dumps(data, indent=2))
    except Exception:
        print(resp.data.decode('utf-8'))

if __name__ == '__main__':
    print('Testing root (should redirect to /login or 200 if session)')
    r = client.get('/')
    print_response(r)

    print('\nTesting stations-from-file (reads CSV in project root)')
    r = client.get('/api/stations-from-file')
    print_response(r)

    print('\nTesting nearby stations API at sample coords (28.65,77.2)')
    r = client.get('/api/stations/28.65/77.2')
    print_response(r)

    print('\nTesting location optimizer candidate endpoint')
    r = client.get('/api/optimize-locations/28.65/77.2')
    print_response(r)

    print('\nSmoke test finished')
