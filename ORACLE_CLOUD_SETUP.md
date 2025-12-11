# ☁️ Oracle Cloud Always Free Setup Guide

Complete guide to run your YouTube Shorts automation 24/7 for FREE!

---

## 📋 What You'll Get (Always Free):

✅ **Virtual Machine** - 1GB RAM, 1 CPU Core (24/7 running)
✅ **200 GB Block Storage**
✅ **10 TB Outbound Data Transfer/month**
✅ **No Credit Card Charges** (Always Free resources never expire)

---

## 🚀 Step 1: Create Oracle Cloud Account

### 1.1 Go to Oracle Cloud
```
https://www.oracle.com/cloud/free/
```

### 1.2 Click "Start for free"

### 1.3 Fill Account Details:
- **Country/Territory:** Select your country
- **Email:** Your email address
- **First/Last Name:** Your name

### 1.4 Verify Email
- Check your email
- Click verification link

### 1.5 Complete Registration:
- **Cloud Account Name:** Choose unique name (e.g., `epicshortshub`)
- **Home Region:** Select closest region (e.g., `India West (Mumbai)`)
  - ⚠️ **Important:** Can't change region later!
- **Password:** Create strong password

### 1.6 Payment Verification (Required but Not Charged):
- Oracle requires credit card for verification
- ✅ **You will NOT be charged** for Always Free resources
- They verify you're not a bot
- ⚠️ Never upgrade to "Pay as you go" unless you want to

### 1.7 Complete Setup
- Wait 2-5 minutes for account provisioning

---

## 🖥️ Step 2: Create Free VM Instance

### 2.1 Login to Oracle Cloud Console
```
https://cloud.oracle.com/
```

### 2.2 Navigate to Compute
- Click **☰ Menu** (top left)
- **Compute** → **Instances**

### 2.3 Create Instance
- Click **"Create Instance"** button

### 2.4 Configure Instance:

**Name:** `shorts-automation`

**Placement:**
- Keep defaults (should show your region)

**Image and Shape:**
- Click **"Change Image"**
- Select: **Canonical Ubuntu 22.04** (or latest)
- Click **"Select Image"**

**Shape:**
- Click **"Change Shape"**
- Select **"Always Free-eligible"** checkbox
- Choose: **VM.Standard.E2.1.Micro** (1 Core, 1GB RAM)
- Click **"Select Shape"**

**Networking:**
- Keep default VCN settings
- ✅ **"Assign a public IPv4 address"** (Important!)

**Add SSH Keys:**
- Select: **"Generate a key pair for me"**
- Click **"Save Private Key"** (Download `.key` file)
- Click **"Save Public Key"** (Optional, for backup)
- ⚠️ **SAVE THIS FILE!** You need it to login!

### 2.5 Create!
- Click **"Create"** button
- Wait 1-2 minutes for provisioning
- Status will change to **"Running"** (green)

### 2.6 Note Public IP Address
- Copy the **Public IP Address** (e.g., `123.45.67.89`)
- You'll need this to connect

---

## 🔐 Step 3: Connect to Your VM

### 3.1 Open Firewall (One-time setup)

**On Oracle Cloud:**
1. Go to Instance details page
2. Click **"Subnet"** link (under Primary VNIC)
3. Click **Default Security List**
4. Click **"Add Ingress Rules"**
5. Add rule:
   - **Source CIDR:** `0.0.0.0/0`
   - **Destination Port:** `22` (SSH)
   - Click **"Add Ingress Rules"**

### 3.2 Connect via SSH

**Windows (PowerShell):**
```powershell
# Fix key permissions first
icacls "path\to\downloaded.key" /inheritance:r
icacls "path\to\downloaded.key" /grant:r "%username%:R"

# Connect
ssh -i "path\to\downloaded.key" ubuntu@YOUR_PUBLIC_IP
```

**Linux/Mac:**
```bash
chmod 400 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@YOUR_PUBLIC_IP
```

Type `yes` when asked about fingerprint.

---

## 📦 Step 4: Setup Your Automation

### 4.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 Install Python & Dependencies
```bash
sudo apt install python3 python3-pip git ffmpeg -y
pip3 install --upgrade pip
```

### 4.3 Upload Your Project Files

**Option A: Using Git (Recommended)**
```bash
# If you have a GitHub repo
git clone YOUR_REPO_URL
cd YOUR_REPO_NAME
```

**Option B: Using SCP (From your PC)**
```powershell
# From your local PC (PowerShell)
scp -i "path\to\key.key" -r "z:\testing\instagram auto video upload" ubuntu@YOUR_IP:~/
```

### 4.4 Install Python Requirements
```bash
cd "instagram auto video upload"
pip3 install -r requirements.txt
```

### 4.5 Upload YouTube Credentials
```bash
# From your PC, upload the credentials file
scp -i "key.key" youtube_credentials.json ubuntu@YOUR_IP:~/instagram\ auto\ video\ upload/
```

---

## ⏰ Step 5: Setup Auto-Run (Cron Job)

### 5.1 Test Manual Run First
```bash
python3 main.py --full
```
- Browser won't open (headless server)
- First time will fail (need token)

### 5.2 Initial Authentication (One-time)

**On your LOCAL PC:**
1. Run: `python main.py --full`
2. Browser opens, authenticate
3. `youtube_token.pickle` is created

**Upload token to Oracle VM:**
```powershell
scp -i "key.key" youtube_token.pickle ubuntu@YOUR_IP:~/instagram\ auto\ video\ upload/
```

### 5.3 Setup Cron (Auto-run every 6 hours)
```bash
crontab -e
```

Choose editor (nano is easiest), then add:
```bash
# Run automation every 6 hours
0 */6 * * * cd ~/instagram\ auto\ video\ upload && /usr/bin/python3 main.py --full >> ~/automation.log 2>&1
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 5.4 Verify Cron
```bash
crontab -l
```

---

## 🎯 Monitoring & Maintenance

### Check Logs:
```bash
tail -f ~/automation.log
```

### Check If Running:
```bash
ps aux | grep python
```

### Restart Cron:
```bash
sudo service cron restart
```

### Update Code (If using Git):
```bash
cd ~/instagram\ auto\ video\ upload
git pull
```

---

## ⚠️ Important Notes:

1. **Never Upgrade Account**: Free tier is FOREVER if you don't upgrade
2. **Monitor Usage**: Stay within free limits (very generous for this use case)
3. **Backup Token**: Keep `youtube_token.pickle` backup on your PC
4. **Region Availability**: Sometimes free VMs are limited, try different regions if unavailable

---

## 🆘 Troubleshooting:

### "Out of host capacity"
- Try different availability domain
- Or wait and retry after a few hours

### SSH Connection Refused
- Check firewall rules (Step 3.1)
- Verify public IP address

### Python command not found
- Use `python3` instead of `python`
- Use `pip3` instead of `pip`

---

## ✅ Final Checklist:

- [ ] Oracle account created
- [ ] VM instance running (Always Free tier)
- [ ] SSH access working
- [ ] Project files uploaded
- [ ] Dependencies installed
- [ ] YouTube credentials uploaded
- [ ] Token authenticated
- [ ] Cron job configured
- [ ] Test run successful

---

🎉 **Congratulations! Your automation is now running 24/7 for FREE!**

Check logs daily: `tail ~/automation.log`
