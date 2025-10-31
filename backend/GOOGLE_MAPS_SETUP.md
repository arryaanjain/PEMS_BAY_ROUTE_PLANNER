# Google Maps API Setup Guide

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top
4. Click "New Project"
5. Name it "PEMS Bay Route Planner" (or any name you prefer)
6. Click "Create"

## Step 2: Enable Billing

⚠️ **Important**: Google Maps API requires a billing account, but they offer $200 free credit per month.

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Click "Link a billing account" or "Create billing account"
3. Follow the prompts to add a credit/debit card
4. Don't worry - you won't be charged unless you exceed the free tier

## Step 3: Enable Required APIs

1. Go to [API Library](https://console.cloud.google.com/apis/library)
2. Search for and enable each of these APIs:
   - **Places API** (for autocomplete)
   - **Geocoding API** (for address validation)
   - **Maps JavaScript API** (for map display)
   - **Directions API** (optional - for route optimization)

For each API:
- Click on the API name
- Click "Enable"
- Wait for it to activate

## Step 4: Create API Key

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "API Key"
3. Your new API key will be displayed
4. **COPY THIS KEY IMMEDIATELY** - it looks like: `AIzaSyD...` (39 characters)

## Step 5: Secure Your API Key (Recommended)

To prevent unauthorized use:

1. Click on your API key name to edit it
2. Under "API restrictions":
   - Select "Restrict key"
   - Check only the APIs you enabled (Places API, Geocoding API, etc.)
3. Under "Application restrictions":
   - For development: Choose "None" or "IP addresses"
   - If using IP addresses, add `127.0.0.1` and your server IP
4. Click "Save"

## Step 6: Add API Key to Your Backend

1. Open your terminal in the backend directory
2. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file:
   ```bash
   nano .env
   # or use any text editor
   ```

4. Replace the placeholder with your real API key:
   ```env
   GOOGLE_MAPS_API_KEY=AIzaSyD...your_actual_key_here
   ```

5. Save and close the file

## Step 7: Test Your Setup

Run the diagnostic script:
```bash
python test_google_api.py
```

You should see:
```
✓ API Key is set
✓ Autocomplete API working! Found X suggestions
```

## Step 8: Start Your Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test the endpoint:
```bash
curl "http://localhost:8000/api/locations/autocomplete?query=oakland"
```

## Troubleshooting

### Still getting REQUEST_DENIED?

1. **Wait 1-2 minutes** - API enablement can take time
2. **Check billing** - Ensure it's linked to your project
3. **Verify API is enabled** - Go back to API Library and confirm
4. **Check key restrictions** - Make sure they're not too strict

### Error: "This API project is not authorized to use this API"

- The API is not enabled. Go back to Step 3

### Error: "API keys with referer restrictions cannot be used with this API"

- Change "Application restrictions" to "None" for testing

### Free Tier Limits

Google provides:
- **$200 free credit per month**
- Places Autocomplete: ~1,000 requests free
- Geocoding: ~40,000 requests free

For this project, you'll likely stay well within the free tier.

## Security Best Practices

1. **Never commit `.env` to Git** (it's in `.gitignore`)
2. **Use API restrictions** in production
3. **Monitor usage** in [Google Cloud Console → APIs & Services → Dashboard](https://console.cloud.google.com/apis/dashboard)
4. **Set up budget alerts** to avoid unexpected charges

## Example Working `.env` File

```env
# Google Maps API Key
GOOGLE_MAPS_API_KEY=AIzaSyABC123...your_real_39_character_key

# Database Configuration
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=pems_bay_planner
```

## Next Steps After Setup

Once your API key works:
1. Test autocomplete: Visit `http://localhost:8000/docs` and try the `/api/locations/autocomplete` endpoint
2. Test validation: Try the `/api/locations/validate` endpoint
3. Check the frontend integration by running `npm run dev` in the frontend folder

---

**Need Help?** Check [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
