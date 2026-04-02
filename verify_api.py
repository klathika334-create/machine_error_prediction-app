import sys
import os

# Ensure src is in the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dashboard.app import app
import json

try:
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['username'] = 'test'
            sess['role'] = 'user'
        
        response = client.get('/api/random-data')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json
            print(f"Type: {type(data)}")
            if isinstance(data, list):
                print(f"Length: {len(data)}")
                if len(data) > 0:
                    last_item = data[-1]
                    print(f"Last item keys: {list(last_item.keys())}")
                    if 'explanation' in last_item:
                        print(f"Explanation found: {last_item['explanation']}")
                    if 'fault_detected' in last_item:
                        print(f"Fault detected: {last_item['fault_detected']}")
                
                # Check sequential data
                response2 = client.get('/api/random-data')
                data2 = response2.json
                if data != data2:
                    print("SUCCESS: Sequential data confirmed (chunk 2 is different from chunk 1)")
                else:
                    print("WARNING: Data chunks are identical")
            else:
                print(f"Data content: {data}")
        else:
            print(response.data.decode())
except Exception as e:
    print(f"Error: {e}")
    