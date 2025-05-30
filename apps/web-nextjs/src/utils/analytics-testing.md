***REMOVED*** Testing Google Analytics Integration

This guide shows you how to verify that Google Analytics is working properly in your Next Watch application.

***REMOVED******REMOVED*** 🚀 Quick Test Methods

***REMOVED******REMOVED******REMOVED*** 1. **Browser Console Testing (Easiest)**

Open your browser's developer console and run:

```javascript
// Test all analytics events at once
window.analyticsDevUtils.testAllEvents();

// Check GA status
window.analyticsDevUtils.checkGAStatus();

// Get the last event sent
window.analyticsDevUtils.getLastEvent();
```

***REMOVED******REMOVED******REMOVED*** 2. **Manual Event Testing**

In the browser console:

```javascript
// Test a movie like event
window.analyticsDevUtils.testAllEvents();

// Or test individual events through the UI:
// - Like a movie
// - Search for something
// - Navigate between pages
```

***REMOVED******REMOVED******REMOVED*** 3. **Check Console Logs**

In development mode, you'll see detailed logs:

```bash
***REMOVED*** Look for these in your browser console:
📊 Analytics Event (DEV) { event: "movie_interaction", movie_action: "like", ... }
🔍 Google Analytics Event
  Event Data: { event: "movie_interaction", ... }
  Timestamp: 2024-01-15T10:30:00.000Z
  Environment: development
```

***REMOVED******REMOVED*** 🔍 Verification Methods

***REMOVED******REMOVED******REMOVED*** Method 1: Google Analytics Real-Time Reports

1. **Open Google Analytics**

   - Go to [analytics.google.com](https://analytics.google.com)
   - Select your property (G-KEFGRJ4SLR)

2. **Navigate to Real-Time Reports**

   - Click "Reports" in the left sidebar
   - Click "Realtime" → "Overview"

3. **Test Events**

   - In your app, perform actions (like movies, search, etc.)
   - Watch the real-time report for events appearing

4. **Check Event Details**
   - Go to "Realtime" → "Events"
   - Look for your custom events: `movie_interaction`, `search`, etc.

***REMOVED******REMOVED******REMOVED*** Method 2: Browser Developer Tools

1. **Open Network Tab**

   - F12 → Network tab
   - Filter by "analytics" or "google"

2. **Perform Actions**

   - Like a movie, search, navigate
   - Look for requests to `google-analytics.com` or `googletagmanager.com`

3. **Check Request Payload**
   - Click on the analytics requests
   - Check the payload contains your event data

***REMOVED******REMOVED******REMOVED*** Method 3: Google Analytics DebugView

1. **Enable Debug Mode**

   ```javascript
   // In browser console
   window.gtag("config", "G-KEFGRJ4SLR", {
     debug_mode: true,
   });
   ```

2. **Open DebugView**
   - In GA4, go to "Configure" → "DebugView"
   - Perform actions in your app
   - See events appear in real-time with full details

***REMOVED******REMOVED******REMOVED*** Method 4: Browser Console Verification

```javascript
// Check if Google Analytics is loaded
typeof window.gtag === "function"; // Should be true
Array.isArray(window.dataLayer); // Should be true

// Check recent events
window.dataLayer.slice(-5); // Shows last 5 events

// Get last analytics event (development only)
window.lastAnalyticsEvent;
```

***REMOVED******REMOVED*** 🧪 Step-by-Step Testing

***REMOVED******REMOVED******REMOVED*** Test 1: Basic Setup Verification

1. **Start the development server**

   ```bash
   pnpm dev
   ```

2. **Open browser console**

   - F12 → Console tab

3. **Check GA status**

   ```javascript
   window.analyticsDevUtils.checkGAStatus();
   ```

   **Expected output:**

   ```
   🔍 Google Analytics Status
   gtag function available: true
   dataLayer available: true
   Environment: development
   dataLayer events: 3
   ```

***REMOVED******REMOVED******REMOVED*** Test 2: Movie Interaction Events

1. **Navigate to a movie page**

   - Go to any movie detail page

2. **Like the movie**

   - Click the like button

3. **Check console logs**

   - Look for: `📊 Analytics Event (DEV) { event: "movie_interaction", movie_action: "like", ... }`

4. **Verify in GA Real-Time**
   - Check GA Real-Time → Events
   - Look for `movie_interaction` event

***REMOVED******REMOVED******REMOVED*** Test 3: Search Events

1. **Use the search feature**

   - Search for "batman"

2. **Check console logs**

   - Look for: `📊 Analytics Event (DEV) { event: "search", search_term: "batman", ... }`

3. **Verify in GA Real-Time**
   - Look for `search` event with search term

***REMOVED******REMOVED******REMOVED*** Test 4: Comprehensive Test

1. **Run all tests**

   ```javascript
   window.analyticsDevUtils.testAllEvents();
   ```

2. **Check GA Real-Time Events**
   - Should see 8 different events appear
   - Each with proper event names and parameters

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Issue: No events in Google Analytics

**Check:**

1. **Tracking ID is correct** - Verify `G-KEFGRJ4SLR` in layout.tsx
2. **Network requests** - Look for GA requests in Network tab
3. **Console errors** - Check for JavaScript errors
4. **Ad blockers** - Disable ad blockers that might block GA

**Debug:**

```javascript
// Check if GA is loaded
window.analyticsDevUtils.checkGAStatus();

// Check for errors
console.log(window.dataLayer);
```

***REMOVED******REMOVED******REMOVED*** Issue: Events not appearing in console

**Check:**

1. **Development mode** - Only shows detailed logs in development
2. **Log level** - Check if debug logs are enabled
3. **Browser console** - Make sure console is open

***REMOVED******REMOVED******REMOVED*** Issue: TypeScript errors

**Fix:**

```typescript
// Make sure imports are correct
import { useAnalytics } from "@/services/hooks/core";
```

***REMOVED******REMOVED*** 📊 What to Look For

***REMOVED******REMOVED******REMOVED*** In Browser Console (Development)

```bash
✅ Analytics Event logs with 📊 emoji
✅ Grouped console logs with event details
✅ No error messages
✅ window.analyticsDevUtils available
```

***REMOVED******REMOVED******REMOVED*** In Google Analytics Real-Time

```bash
✅ Active users count increases
✅ Custom events appear: movie_interaction, search, etc.
✅ Event parameters are populated correctly
✅ Events appear within 30 seconds of action
```

***REMOVED******REMOVED******REMOVED*** In Network Tab

```bash
✅ Requests to google-analytics.com
✅ Requests contain event data
✅ HTTP 200 responses
✅ No CORS errors
```

***REMOVED******REMOVED*** 🎯 Production Testing

In production, logging is minimal, but you can still verify:

1. **Google Analytics Real-Time Reports**

   - Most reliable method for production

2. **Network Tab**

   - Check for GA requests

3. **Basic Console Check**
   ```javascript
   // Should work in production
   typeof window.gtag === "function";
   ```

***REMOVED******REMOVED*** 📈 Monitoring Analytics Health

***REMOVED******REMOVED******REMOVED*** Development

- Console logs show all events
- `window.analyticsDevUtils` for testing
- Detailed error reporting

***REMOVED******REMOVED******REMOVED*** Production

- Monitor GA Real-Time reports
- Check application logs for analytics errors
- Set up GA alerts for data collection issues

***REMOVED******REMOVED*** 🔧 Advanced Debugging

***REMOVED******REMOVED******REMOVED*** Enable GA Debug Mode

```javascript
window.gtag("config", "G-KEFGRJ4SLR", {
  debug_mode: true,
  send_page_view: false, // If you want to control page views manually
});
```

***REMOVED******REMOVED******REMOVED*** Custom Event Validation

```javascript
// Validate event structure before sending
const validateEvent = (eventData) => {
  console.log("Event validation:", {
    hasEventName: !!eventData.event,
    hasRequiredParams: Object.keys(eventData).length > 1,
    eventData,
  });
};
```

This comprehensive testing approach ensures your Google Analytics integration is working correctly across all environments! 🎉
