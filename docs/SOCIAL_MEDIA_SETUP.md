# 📱 Automate Instagram & Facebook Reels Setup Guide

Agar aapko **YouTube Shorts**, **Instagram Reels**, aur **Facebook Reels** teeno par auto-upload karna hai, to ye one-time setup karna padega.

---

## ✅ Step 1: Accounts Ready Karo
1.  **Instagram:** Apne Instagram account ko **Professional** (Creator or Business) account mein convert karein.
    *   *Settings > Account Type and Tools > Switch to Professional Account.*
2.  **Facebook Page:** Ek Facebook Page banayein (agar nahi hai).
3.  **Link Karo:** Instagram ko Facebook Page se connect karein.
    *   *Instagram App > Edit Profile > Page > Connect existing or Create new.*
    *   Make sure dono link ho gaye hain.

---

## 🔑 Step 2: Meta Developer App Banao
1.  Go to [developers.facebook.com](https://developers.facebook.com/) aur Login karein.
2.  **My Apps** > **Create App** pe click karein.
3.  Select **"Other"** > **Next**.
4.  Select **"Business"** > **Next**.
5.  App Name dein (e.g., "Shorts Automation") aur Create karein.

---

## 🛠️ Step 3: APIs Add Karo
App Dashboard mein aane ke baad, neeche scroll karein aur in products ko **Set up** karein:
1.  **Instagram Graph API**: (Click Set up).
2.  **Facebook Login for Business**: (Click Set up).

---

## 🎟️ Step 4: Token Generate Karo (IMP Task!)
1.  Left Sidebar mein **Marketing API** nahi balki **Tools > Graph API Explorer** par jayein (ya directly search karein).
2.  **Facebook App:** Apni banayi hui App select karein.
3.  **User or Page:** "User Token" select karein.
4.  **Permissions (Add Permission menu se ye sab add karein):**
    *   `instagram_basic`
    *   `instagram_content_publish`
    *   `pages_show_list`
    *   `pages_read_engagement`
    *   `pages_manage_posts` (Facebook Upload ke liye)
    *   `public_profile`
5.  **Generate Access Token** par click karein.
6.  Pop-up aayega -> "Continue as [Your Name]" -> Select your **Facebook Page** -> Select your **Instagram Account** -> Save.

---

## 🆔 Step 5: IDs Aur Long-Lived Token Nikalo
Abhi jo token mila wo sirf 1 hour chalta hai. Hamein "Long-Lived Token" chahiye (jo 60 days chalta hai).

**1. ID Nikalo:**
Graph API Explorer mein `me/accounts` likh kar **Submit** karein.
Response mein dekhein:
*   `id`: Ye aapka **FACEBOOK PAGE ID** hai (`FB_PAGE_ID`).
*   Is ID ko copy karke rakhein.

**2. IG Account ID Nikalo:**
Explorer mein likhein: `<FACEBOOK_PAGE_ID>?fields=instagram_business_account`
(Jahan `<FACEBOOK_PAGE_ID>` hai wahan upar wali ID dalein).
Response mein `instagram_business_account` ke andar `id` moti hai.
*   Ye aapka **IG ACCOUNT ID** hai (`IG_ACCOUNT_ID`).

**3. Long-Lived Token:**
*   Upper right mein "i" icon (Info) pe click karein token field ke paas.
*   "Open in Access Token Tool" click karein.
*   Neeche "Extend Access Token" ka button hoga. Click karein.
*   Ek naya Lamba Token milega. Ye hai **IG_ACCESS_TOKEN**.

---

## 🚀 Step 6: GitHub Secrets Update Karo
Apne GitHub Repo > Settings > Secrets mein ye 3 secrets add kar do:

1.  `IG_ACCESS_TOKEN`: (Jo lamba token mila)
2.  `IG_ACCOUNT_ID`: (Jo IG ID mili)
3.  `FB_PAGE_ID`: (Jo Facebook Page ID mili)

---

🎉 **Done!** Ab script automatically dono jagah upload karegi.
