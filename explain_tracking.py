"""
Tracking System Demo
Shows how duplicate uploads are prevented
"""
import json

print("=" * 80)
print("Tracking System Explanation")
print("=" * 80)

# Load current tracking
with open('tracking.json', 'r') as f:
    tracking = json.load(f)

print("\n📊 Current Tracking Status:")
print(f"Channel: {tracking.get('channel_url', 'Not set')}")
print(f"Last Scrape: {tracking.get('last_scrape', 'Never')}")
print(f"Total Videos Tracked: {len(tracking.get('videos', {}))}")

print("\n" + "=" * 80)
print("How Duplicate Prevention Works:")
print("=" * 80)

print("""
1. SCRAPING:
   - Jab channel scrape hota hai, har video ko tracking mein add kiya jata hai
   - Status: "pending" (not downloaded yet)

2. DOWNLOADING:
   - Highest viewed "pending" video download hota hai
   - Status changes: "pending" → "downloaded"
   - Already "downloaded" or "completed" videos SKIP ho jate hain

3. PROCESSING:
   - Video split + edit hota hai
   - Status changes: "downloaded" → "processed"

4. UPLOADING:
   - Instagram pe upload hota hai
   - Parts uploaded list mein add hote hain: [1, 2, 3, ...]
   - Status changes: "processed" → "completed"

5. NEXT RUN:
   - "completed" videos automatically SKIP ho jate hain
   - Only "pending" videos consider hote hain

Example tracking.json structure:
{
  "videos": {
    "VIDEO_ID_1": {
      "title": "Video Title",
      "views": 1000000,
      "status": "completed",          ← Already uploaded, SKIP!
      "parts_uploaded": [1, 2, 3],
      "last_upload": "2025-12-10"
    },
    "VIDEO_ID_2": {
      "status": "pending"              ← Next in queue
    }
  }
}

Status Flow:
pending → downloaded → processed → completed
  ↓          ↓           ↓            ↓
 Skip?      No         No           YES (SKIP!)

""")

print("=" * 80)
print("Commands to Check Tracking:")
print("=" * 80)
print("""
# Show current status
python main.py --status

# Manually view tracking file
cat tracking.json

# Check specific video
python -c "import json; t=json.load(open('tracking.json')); print(json.dumps(t['videos']['VIDEO_ID'], indent=2))"
""")
