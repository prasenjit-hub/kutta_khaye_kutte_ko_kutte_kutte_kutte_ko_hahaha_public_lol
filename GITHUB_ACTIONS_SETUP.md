# 🤖 GitHub Actions Setup Guide - YouTube Shorts Automation

Complete guide to run your automation **FREE FOREVER** on GitHub Actions!

---

## ✅ What You'll Get:

- 🔄 **Automated runs every 6 hours** (4 times/day)
- 📊 **Progress tracking** (persists across runs)
- 🎯 **~20 Shorts/day** (5 parts per run x 4 runs)
- 💰 **100% FREE** (unlimited for public repos)
- ♾️ **Lifetime** (no expiration)

---

## 📋 Prerequisites:

- ✅ GitHub account (free)
- ✅ YouTube credentials setup (already done!)
- ✅ This project folder ready

---

## 🚀 Step-by-Step Setup:

### Step 1: Create GitHub Repository

#### 1.1 Go to GitHub
```
https://github.com/new
```

#### 1.2 Fill Repository Details:
- **Repository name:** `youtube-shorts-automation` (or any name)
- **Description:** "Automated YouTube Shorts from viral videos"
- **Visibility:** 
  - ✅ **Public** (Unlimited free minutes! Recommended)
  - 🔒 Private (2000 min/month, still enough)
- **Initialize:** ❌ Do NOT check any boxes (we'll push existing code)

#### 1.3 Click "Create repository"

---

### Step 2: Push Your Code to GitHub

#### 2.1 Open Terminal in Project Folder
```powershell
cd "z:\testing\instagram auto video upload"
```

#### 2.2 Initialize Git (if not already)
```bash
git init
git add .
git commit -m "Initial commit: YouTube Shorts automation"
```

#### 2.3 Add Remote & Push
```bash
# Replace YOUR_USERNAME and REPO_NAME
git remote add origin https://github.com/YOUR_USERNAME/youtube-shorts-automation.git
git branch -M main
git push -u origin main
```

**GitHub will ask for login:**
- Username: Your GitHub username
- Password: Use **Personal Access Token** (not your password!)

**Create Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Scopes: Check **`repo`** (full control)
4. Copy token, use as password

---

### Step 3: Configure GitHub Secrets

Secrets are **encrypted environment variables**. Your credentials will be safe!

#### 3.1 Go to Repository Settings
```
Your Repo → Settings → Secrets and variables → Actions
```

#### 3.2 Click "New repository secret"

#### 3.3 Add These Secrets:

**Secret 1: YOUTUBE_CREDENTIALS**
- Name: `YOUTUBE_CREDENTIALS`
- Value: 
  ```bash
  # On your PC, run this to encode:
  certutil -encode youtube_credentials.json temp.txt
  # Or on Linux/Mac:
  base64 youtube_credentials.json
  ```
  Copy the encoded output (single line, no spaces)

**Secret 2: YOUTUBE_TOKEN** (After first local authentication)
- Name: `YOUTUBE_TOKEN`
- Value:
  ```bash
  # Encode youtube_token.pickle
  certutil -encode youtube_token.pickle temp.txt
  # Or:
  base64 youtube_token.pickle
  ```
  
**Secret 3: GH_PAT** (GitHub Personal Access Token)
- Name: `GH_PAT`
- Value: Your GitHub token (same one you used for git push)
- **Why?** To allow workflow to commit progress back to repo

---

### Step 4: First Authentication (One-Time)

**Since GitHub Actions can't open browser**, you need to authenticate **once locally**:

#### 4.1 On Your PC:
```powershell
python main.py --full
```

#### 4.2 Browser Opens:
- Login to Google account
- Allow permissions
- `youtube_token.pickle` file is created

#### 4.3 Encode & Add to Secrets:
```powershell
certutil -encode youtube_token.pickle temp.txt
```
Copy output → Add as `YOUTUBE_TOKEN` secret (Step 3.3)

---

### Step 5: Test Workflow

#### 5.1 Manual Trigger (Test):
1. Go to **Actions** tab in your repo
2. Click **"YouTube Shorts Automation"** workflow
3. Click **"Run workflow"** dropdown
4. Click **"Run workflow"** button

#### 5.2 Watch Live Logs:
- Click on the running workflow
- Expand steps to see logs
- Should complete in ~5-10 minutes

#### 5.3 Verify Upload:
- Check your YouTube channel
- 5 new Shorts should appear!
- Check `tracking.json` in repo (will be updated)

---

### Step 6: Enable Scheduled Runs

**Already enabled!** Workflow runs automatically every 6 hours:
- 00:00 (midnight)
- 06:00 (morning)
- 12:00 (noon)
- 18:00 (evening)

**To change schedule:**
Edit `.github/workflows/automation.yml`:
```yaml
cron: '0 */6 * * *'  # Every 6 hours
# Or:
cron: '0 0,6,12,18 * * *'  # Specific times
# Or:
cron: '0 0 * * *'  # Once daily at midnight
```

---

## 📊 Monitoring & Maintenance:

### Check Workflow Runs:
```
Repo → Actions tab → See all runs
```

### Check Uploaded Videos:
- YouTube Studio → Content
- Or check `tracking.json` in repo

### Check Logs:
- Click on any workflow run
- Expand steps
- Download logs if needed

### Update Code:
```bash
# Make changes locally
git add .
git commit -m "Update configuration"
git push
# Next run will use updated code!
```

---

## ⚙️ Configuration:

### Upload Limit (Already Set):
`config.json`:
```json
"max_uploads_per_run": 5
```

**Adjust as needed:**
- `5` = Balanced (20 shorts/day)
- `3` = Conservative (12 shorts/day)
- `10` = Aggressive (40 shorts/day, watch quota!)

### Quota Management:
- Daily quota: 10,000 units
- 1 upload ≈ 1,600 units
- 5 uploads/run × 4 runs/day = 20 uploads ≈ 32,000 units
- ⚠️ This exceeds quota!

**Solution:** Reduce to 3 uploads/run or 2 runs/day

**Best Config:**
```json
"max_uploads_per_run": 3
```
Cron:
```yaml
cron: '0 */12 * * *'  # Every 12 hours (2x/day)
# Result: 3 x 2 = 6 uploads/day = 9,600 units ✅
```

---

## 🆘 Troubleshooting:

### Workflow Fails:
- Check **Actions** tab → Click failed run → Read error
- Common: Quota exceeded → Reduce uploads/run
- Common: Authentication failed → Re-encode `YOUTUBE_TOKEN`

### Duplicate Uploads:
- `tracking.json` not committing
- Check: `GH_PAT` secret is correct
- Check: Token has `repo` scope

### No Videos Uploading:
- Check secrets are correct (base64 encoded)
- Check YouTube channel is correct in `config.json`
- Check quota not exceeded (Google Cloud Console)

---

## 🔐 Security Best Practices:

✅ **Never commit these files:**
- `youtube_credentials.json`
- `youtube_token.pickle`
- `.env` files

✅ **Use Secrets for:**
- All credentials
- API keys
- Tokens

✅ **Public vs Private Repo:**
- Public = Code visible (but secrets are hidden)
- Private = Code + Secrets both hidden
- **Recommendation:** Public (unlimited minutes!)

---

## 📈 Expected Results:

### Daily Uploads (3 uploads/run, 2 runs/day):
- **6 Shorts/day**
- **~180 Shorts/month**
- **~2,160 Shorts/year**

### Growth Potential:
- Month 1: 180 videos
- Month 3: 540 videos
- Month 6: 1,080 videos
- **Viral potential increases exponentially!**

---

## ✅ Final Checklist:

- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] `YOUTUBE_CREDENTIALS` secret added
- [ ] `YOUTUBE_TOKEN` secret added (after local auth)
- [ ] `GH_PAT` secret added
- [ ] Workflow manually tested
- [ ] First 5 shorts uploaded successfully
- [ ] `tracking.json` updated in repo
- [ ] Scheduled runs enabled (automatic!)

---

## 🎉 Congratulations!

Your automation is now running **FREE FOREVER** on GitHub Actions!

**What happens next:**
- Every 6 hours (or your schedule)
- Workflow automatically runs
- Downloads → Processes → Uploads
- Progress saved
- Repeat!

**Sit back and watch your channel grow!** 📈🚀

---

## 💡 Pro Tips:

1. **Monitor first week daily** to ensure smooth operation
2. **Adjust upload frequency** based on quota usage
3. **Check YouTube Analytics** to optimize posting times
4. **Update config** to target trending topics
5. **Backup `tracking.json`** occasionally

Enjoy your automated YouTube Shorts channel! 🎬✨
