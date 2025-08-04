***REMOVED***!/bin/sh
set -e

***REMOVED*** BFF API Startup Script with Smart Cache Warming
***REMOVED*** 
***REMOVED*** Production Mode: Warms ALL available movies (no limits)
***REMOVED*** Development Mode: Uses debug limits for faster testing
***REMOVED***
***REMOVED*** Environment Variables:
***REMOVED*** - ENVIRONMENT: "production" or "development"
***REMOVED*** - ENABLE_CACHE_WARMING: "true" or "false" (default: true)
***REMOVED*** - TIER1_DEV_LIMIT: Max movies for Tier 1 in dev (default: 50)
***REMOVED*** - TIER2_DEV_LIMIT: Max movies for Tier 2 in dev (default: 200)  
***REMOVED*** - TIER3_DEV_LIMIT: Max movies for Tier 3 in dev (default: 500)

echo "🚀 Starting BFF API with cache warming..."

***REMOVED*** Configuration variables for warming strategy
***REMOVED*** Production: warm ALL movies (no limits), Development: use limits for faster testing
TIER1_DEV_LIMIT="${TIER1_DEV_LIMIT:-50}"
TIER2_DEV_LIMIT="${TIER2_DEV_LIMIT:-200}"
TIER3_DEV_LIMIT="${TIER3_DEV_LIMIT:-500}"
WARMING_STRATEGY="${WARMING_STRATEGY:-unlimited_with_debug}"

echo "📊 Cache warming configuration:"
echo "   Strategy: $WARMING_STRATEGY"
if [ "$ENVIRONMENT" = "production" ]; then
    echo "   Production: Warming ALL available movies (no limits)"
else
    echo "   Development: Using debug limits"
    echo "   - Tier 1 dev limit: $TIER1_DEV_LIMIT"
    echo "   - Tier 2 dev limit: $TIER2_DEV_LIMIT"
    echo "   - Tier 3 dev limit: $TIER3_DEV_LIMIT"
fi

***REMOVED*** Check if we should enable cache warming
if [ "${ENABLE_CACHE_WARMING:-true}" = "true" ]; then
    echo "⏰ Cache warming is ENABLED"
    
    ***REMOVED*** Create cron jobs based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "⏰ Setting up PRODUCTION cache warming schedule - UNLIMITED warming (ALL movies)..."
        cat > /tmp/crontab << PROD_EOF
***REMOVED*** Production Cache Warming Schedule - UNLIMITED (ALL 4000+ movies)
***REMOVED*** Tier 1: New releases + trending (every 2 hours) - ALL MOVIES
0 */2 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 1 --verbose >> /app/logs/tier1-warming.log 2>&1"

***REMOVED*** Tier 2: Popular movies + user favorites (daily) - ALL MOVIES
0 6 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --verbose >> /app/logs/tier2-warming.log 2>&1"
0 18 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --verbose >> /app/logs/tier2-warming.log 2>&1"

***REMOVED*** Tier 3: Full catalog refresh (weekly) - ALL MOVIES  
0 2 * * 0 su app -c "cd /app && python -m bff_api.cli cache warm-tier 3 --verbose >> /app/logs/tier3-warming.log 2>&1"

***REMOVED*** Legacy popular warming (reduced frequency) - FALLBACK
0 14 * * * su app -c "cd /app && python -m bff_api.cli cache warm-legacy --limit 200 >> /app/logs/legacy-warming.log 2>&1"

***REMOVED*** Health checks (every 5 minutes)
*/5 * * * * su app -c "cd /app && python -m bff_api.cli health check >> /app/logs/health.log 2>&1"

***REMOVED*** Cache monitoring (every 30 minutes)
*/30 * * * * su app -c "cd /app && python -m bff_api.cli cache show >> /app/logs/cache-stats.log 2>&1"
PROD_EOF
    else
        echo "⏰ Setting up DEVELOPMENT cache warming schedule with debug limits..."
        cat > /tmp/crontab << DEV_EOF
***REMOVED*** Development Cache Warming Schedule - Limited for faster testing
***REMOVED*** Tier 1: New releases + trending (every 4 hours) - DEBUG LIMITS
0 */4 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 1 --max-movies $TIER1_DEV_LIMIT --verbose >> /app/logs/tier1-warming.log 2>&1"

***REMOVED*** Tier 2: Popular movies (twice daily) - DEBUG LIMITS
0 9 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies $TIER2_DEV_LIMIT --verbose >> /app/logs/tier2-warming.log 2>&1"
0 21 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies \$((TIER2_DEV_LIMIT / 2)) --verbose >> /app/logs/tier2-warming.log 2>&1"

***REMOVED*** Tier 3: Full catalog (weekly, smaller sample) - DEBUG LIMITS
0 3 * * 0 su app -c "cd /app && python -m bff_api.cli cache warm-tier 3 --max-movies $TIER3_DEV_LIMIT --verbose >> /app/logs/tier3-warming.log 2>&1"

***REMOVED*** Legacy warming (reduced) - FALLBACK
0 15 * * * su app -c "cd /app && python -m bff_api.cli cache warm-legacy --limit 50 >> /app/logs/legacy-warming.log 2>&1"

***REMOVED*** Health checks (every 10 minutes for dev)
*/10 * * * * su app -c "cd /app && python -m bff_api.cli health check >> /app/logs/health.log 2>&1"
DEV_EOF
    fi

    ***REMOVED*** Install crontab for root (but commands run as app user)
    crontab /tmp/crontab
    echo "📋 Cache warming cron jobs installed:"
    crontab -l
    
    ***REMOVED*** Start cron daemon in background
    echo "🔄 Starting cron daemon in background..."
    crond
    
    echo "✅ Cache warming enabled and scheduled"
else
    echo "⏰ Cache warming is DISABLED (set ENABLE_CACHE_WARMING=true to enable)"
fi

***REMOVED*** Switch to app user and start the API
echo "🚀 Starting BFF API as app user..."
exec su app -c "cd /app && python -m bff_api"