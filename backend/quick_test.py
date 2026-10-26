import urllib.request, json, urllib.error

# Test GET /api/coffees
try:
    with urllib.request.urlopen("http://127.0.0.1:5000/api/coffees") as resp:
        data = json.loads(resp.read())
        print("GET /api/coffees SUCCESS:", data["success"])
        print("  Coffees count:", len(data.get("coffees", [])))
        for c in data["coffees"]:
            print(f"  [{c['id']}] {c['name']} - votes: {c['vote_count']}")
except urllib.error.HTTPError as e:
    print("GET ERROR:", e.code, e.read().decode()[:200])

# Test POST vote
try:
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/coffees/1/vote",
        data=b"",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        print("\nPOST /api/coffees/1/vote SUCCESS:", data)
except urllib.error.HTTPError as e:
    print("VOTE ERROR:", e.code, e.read().decode()[:200])

# Test 404
try:
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/coffees/999/vote",
        data=b"",
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print("Should have been 404!")
except urllib.error.HTTPError as e:
    print("\nPOST /api/coffees/999/vote returned", e.code, "(expected 404)")
