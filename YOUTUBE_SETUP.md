# YouTube Upload Setup Guide

## 📋 Prerequisites
- Google Account
- 5-10 minutes
- Internet connection

---

## 🚀 Step-by-Step Setup

### Step 1: Google Cloud Console mein Project Banao

1. **Open**: [Google Cloud Console](https://console.cloud.google.com/)

2. **New Project**:
   - Click: "Select a project" (top bar)
   - Click: "NEW PROJECT"
   - Project name: `YouTube Auto Upload`
   - Click: "CREATE"

### Step 2: YouTube Data API Enable Karo

1. **Search API**:
   - Left menu → "APIs & Services" → "Library"
   - Search: `YouTube Data API v3`
   - Click on it
   - Click: "ENABLE"

### Step 3: OAuth Credentials Create Karo

1. **Configure Consent Screen** (Pehli baar):
   - Left menu → "APIs & Services" → "OAuth consent screen"
   - User Type: **External** (select karo)
   - Click: "CREATE"
   
   **App Information**:
   - App name: `YouTube Auto Uploader`
   - User support email: Your email
   - Developer contact: Your email
   - Click: "SAVE AND CONTINUE"
   
   **Scopes**:
   - Click: "ADD OR REMOVE SCOPES"
   - Search: `youtube.upload`
   - Select: `.../auth/youtube.upload`
   - Click: "UPDATE"
   - Click: "SAVE AND CONTINUE"
   
   **Test Users** (Important!):
   - Click: "ADD USERS"
   - Enter your Gmail address (jo upload ke liye use karoge)
   - Click: "ADD"
   - Click: "SAVE AND CONTINUE"

2. **Create Credentials**:
   - Left menu → "Credentials"
   - Click: "CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: **Desktop app**
   - Name: `YouTube Uploader Client`
   - Click: "CREATE"
   - **Download JSON**:
     - Click download icon (⬇️)
     - Save as: `youtube_credentials.json`
     - Move to project folder: `Z:\testing\instagram auto video upload\`

### Step 4: Add Dependencies

Update `requirements.txt`:

```txt
google-api-python-client>=2.108.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
```

Install:
```powershell
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### Step 5: First Time Authentication

```powershell
cd "Z:\testing\instagram auto video upload"
python modules\youtube_uploader.py
```

Kya hoga:
1. Browser automatically open hoga
2. Google account select karo
3. Warning: "Google hasn't verified this app" → Click "Continue"
4. Permissions de do
5. "Authentication successful" message dikhe → Done!
6. Token save ho jayega (`youtube_token.pickle`)

Next time authentication nahi chahiye! ✅

---

## 🎬 Usage Examples

### Basic Upload

```python
from modules.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()

video_id = uploader.upload_short(
    video_path='processed/video_part1_edited.mp4',
    title='Amazing Video - Part 1',
    description='This is an amazing video!\n\n#Shorts',
    tags=['shorts', 'viral', 'trending']
)

print(f"Uploaded: https://www.youtube.com/shorts/{video_id}")
```

### Batch Upload

```python
videos = [
    ('processed/vid1_part1.mp4', 1, 'My Video Title'),
    ('processed/vid1_part2.mp4', 2, 'My Video Title'),
    ('processed/vid1_part3.mp4', 3, 'My Video Title'),
]

results = uploader.upload_batch(
    videos=videos,
    title_template='{title} - Part {part}',
    tags=['shorts', 'viral']
)

print(f"Successful: {len(results['successful'])}")
```

### With Main Script

```powershell
# Upload to YouTube
python main.py --upload-to youtube

# Upload specific video
python main.py --upload-youtube VIDEO_ID
```

---

## 🔐 Security Notes

### Safe:
- ✅ `youtube_credentials.json` - Safe, doesn't contain passwords
- ✅ `youtube_token.pickle` - Also safe, auto-refreshes
- ✅ Both are gitignored

### Keep Private:
- ⚠️ Don't share these files publicly
- ⚠️ Don't commit to public GitHub

---

## 🐛 Troubleshooting

### Error: "youtube_credentials.json not found"
**Solution**: Download credentials from Google Cloud Console (Step 3)

### Error: "Google hasn't verified this app"
**Solution**: 
1. Click "Advanced" 
2. Click "Go to YouTube Auto Uploader (unsafe)"
3. This is normal for personal projects

### Error: "Access blocked: Authorization Error"
**Solution**: Add your email in "Test Users" (Step 3, OAuth consent screen)

### Error: "The request cannot be completed because you have exceeded your quota"
**Solution**: 
- Free tier: 10,000 quota units/day
- 1 upload = ~1600 units
- Can upload ~6 videos/day
- Request quota increase from Google Cloud Console

### Error: "Invalid authentication credentials"
**Solution**: Delete `youtube_token.pickle` and re-authenticate

---

## 📊 YouTube API Quotas

| Action | Cost (units) | Daily Limit (Free) |
|--------|--------------|-------------------|
| Upload Video | 1,600 | ~6 uploads/day |
| Update Video | 50 | 200/day |
| List Videos | 1 | 10,000/day |

**Note**: Quota limit badha sakte ho (request Google se)

---

## ✅ Verification

Test upload karo:

```powershell
python modules\youtube_uploader.py
```

Success message:
```
✓ Authentication successful!
Ready to upload videos to YouTube Shorts
```

---

## 🎯 Next Steps

1. ✅ Setup complete
2. ✅ Authentication done
3. 🚀 Ready to upload!

Use in automation:
```powershell
python main.py --platform youtube --full
```

---

## 📞 Support

**Common Issues**:
- Make sure project is in Google Cloud Console
- API is enabled
- OAuth consent screen configured
- Test user added
- Credentials file downloaded

**Still stuck?**
- Check: https://console.cloud.google.com/apis/credentials
- Verify: YouTube Data API v3 is enabled
- Confirm: Test user email is correct

---

**Setup time**: ~10 minutes
**Future runs**: Instant (no re-authentication needed)
