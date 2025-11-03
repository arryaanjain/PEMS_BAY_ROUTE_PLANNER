# Google Maps API Setup & Troubleshooting

## Current Issue: REQUEST_DENIED

The `REQUEST_DENIED` error means Google Maps API is rejecting your requests. Here's how to fix it:

---

## Step 1: Verify API Key is Set

Run the diagnostic test script:
```bash
cd backend
python test_google_api.py
```

This will check:
- ✓ If API key is loaded from `.env`
- ✓ API key format
- ✓ Actual API call to Google

---

## Step 2: Enable Required APIs

Go to [Google Cloud Console API Library](https://console.cloud.google.com/apis/library)

Enable these APIs:
1. **Places API** (New) ✅ - For autocomplete and place details
2. **Geocoding API** ✅ - For address to coordinates
3. **Maps JavaScript API** (optional) - For frontend map display
4. **Directions API** (optional) - For route optimization

**Important:** After enabling, wait 1-2 minutes for changes to propagate.

---

## Step 3: Create/Check API Key

### Create New API Key:
1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"Create Credentials"** → **"API Key"**
3. Copy the key immediately
4. Click **"Restrict Key"** (optional but recommended)

### Add to `.env`:
```bash
cd backend
cp .env.example .env
nano .env  # or use your text editor
```

Add your key:
```env
GOOGLE_MAPS_API_KEY=AIzaSyC-your-actual-api-key-here
```

---

## Step 4: Remove API Key Restrictions (During Development)

If your API key has restrictions, temporarily remove them for testing:

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on your API key
3. Under **"API restrictions"**:
   - Select **"Don't restrict key"** (for testing only)
4. Under **"Application restrictions"**:
   - Select **"None"** (for testing only)
5. Click **"Save"**
6. Wait 1-2 minutes

⚠️ **Security Note:** Re-enable restrictions after confirming it works!

---

## Step 5: Enable Billing

Google Maps APIs require billing to be enabled (even with free tier):

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Link a billing account to your project
3. You get **$200 free credits per month**
4. Places Autocomplete: $2.83 per 1000 requests (after free tier)

---

## Step 6: Test Configuration

### Test via script:
```bash
python backend/test_google_api.py
```

### Test via API endpoint:
```bash
# Start backend
uvicorn backend.app.main:app --reload

# In another terminal, check config
curl http://localhost:8000/api/locations/config-check

# Test autocomplete
curl "http://localhost:8000/api/locations/autocomplete?query=San+Francisco"
```

---

## Step 7: Check Server Logs

When you run the backend, check for:
```
Google API status: REQUEST_DENIED
Google API error: [error message]
API key (first 10 chars): AIzaSyC...
```

Common error messages:
- **"This API project is not authorized to use this API"** → Enable the API
- **"API key not valid"** → Check your API key
- **"The provided API key is invalid"** → Regenerate key
- **"Billing has not been enabled"** → Enable billing

---

## Quick Checklist

- [ ] `.env` file exists in `backend/` directory
- [ ] `GOOGLE_MAPS_API_KEY` is set in `.env`
- [ ] API key is valid (39 characters, starts with `AIza`)
- [ ] Places API is enabled in Google Cloud Console
- [ ] Geocoding API is enabled
- [ ] Billing is enabled for the project
- [ ] No API restrictions during testing
- [ ] Waited 1-2 minutes after enabling APIs

---

## Alternative: Use Mock Data (Temporary)

If you want to continue development without Google Maps API, I can create a mock service that returns fake data for testing. Let me know!

---

## Verify Backend Routes

After fixing, test these endpoints:

```bash
# Diagnostic
GET http://localhost:8000/api/locations/config-check

# Autocomplete
GET http://localhost:8000/api/locations/autocomplete?query=oakland

# Validate
POST http://localhost:8000/api/locations/validate
{
  "name": "San Francisco",
  "coordinates": {"lat": 37.7749, "lng": -122.4194}
}
```

Expected responses:
- ✅ Status 200
- ✅ JSON data with locations
- ✅ No "REQUEST_DENIED" in logs

---

## Need Help?

Run the diagnostic and share the output:
```bash
python backend/test_google_api.py
```
