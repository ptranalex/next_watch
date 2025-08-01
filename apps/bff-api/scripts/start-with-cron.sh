***REMOVED***!/bin/sh
set -e

echo "🚀 Starting BFF API with cache warming..."

***REMOVED*** Configuration variables for warming strategy
TIER1_MAX_MOVIES="${TIER1_MAX_MOVIES:-50}"
TIER2_MAX_MOVIES="${TIER2_MAX_MOVIES:-500}"
TIER3_MAX_MOVIES="${TIER3_MAX_MOVIES:-1000}"
WARMING_STRATEGY="${WARMING_STRATEGY:-version_aware}"

echo "📊 Cache warming configuration:"
echo "   Strategy: $WARMING_STRATEGY"
echo "   Tier 1 max movies: $TIER1_MAX_MOVIES"
echo "   Tier 2 max movies: $TIER2_MAX_MOVIES"
echo "   Tier 3 max movies: $TIER3_MAX_MOVIES"

***REMOVED*** Check if we should enable cache warming
if [ "${ENABLE_CACHE_WARMING:-true}" = "true" ]; then
    echo "⏰ Cache warming is ENABLED"
    
    ***REMOVED*** Create cron jobs based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "⏰ Setting up PRODUCTION cache warming schedule with version-aware tiers..."
        cat > /tmp/crontab << PROD_EOF
***REMOVED*** Production Cache Warming Schedule - Version-Aware Priority Tiers
***REMOVED*** Tier 1: New releases + trending (every 2 hours) - HIGH PRIORITY
0 */2 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 1 --max-movies $TIER1_MAX_MOVIES --verbose >> /app/logs/tier1-warming.log 2>&1"

***REMOVED*** Tier 2: Popular movies + user favorites (daily) - MEDIUM PRIORITY
0 6 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies $TIER2_MAX_MOVIES --verbose >> /app/logs/tier2-warming.log 2>&1"
0 18 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies \$((TIER2_MAX_MOVIES / 2)) --verbose >> /app/logs/tier2-warming.log 2>&1"

***REMOVED*** Tier 3: Full catalog refresh (weekly) - LOW PRIORITY  
0 2 * * 0 su app -c "cd /app && python -m bff_api.cli cache warm-tier 3 --max-movies $TIER3_MAX_MOVIES --verbose >> /app/logs/tier3-warming.log 2>&1"

***REMOVED*** Legacy popular warming (reduced frequency) - FALLBACK
0 14 * * * su app -c "cd /app && python -m bff_api.cli cache warm-legacy --limit 200 >> /app/logs/legacy-warming.log 2>&1"

***REMOVED*** Health checks (every 5 minutes)
*/5 * * * * su app -c "cd /app && python -m bff_api.cli health check >> /app/logs/health.log 2>&1"

***REMOVED*** Cache monitoring (every 30 minutes)
*/30 * * * * su app -c "cd /app && python -m bff_api.cli cache show >> /app/logs/cache-stats.log 2>&1"
PROD_EOF
    else
        echo "⏰ Setting up DEVELOPMENT cache warming schedule with version-aware tiers..."
        cat > /tmp/crontab << DEV_EOF
***REMOVED*** Development Cache Warming Schedule - Version-Aware (Lighter Load)
***REMOVED*** Tier 1: New releases + trending (every 4 hours) - DEV FREQUENCY
0 */4 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 1 --max-movies \$((TIER1_MAX_MOVIES / 2)) --verbose >> /app/logs/tier1-warming.log 2>&1"

***REMOVED*** Tier 2: Popular movies (twice daily) - DEV FREQUENCY
0 9 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies \$((TIER2_MAX_MOVIES / 5)) --verbose >> /app/logs/tier2-warming.log 2>&1"
0 21 * * * su app -c "cd /app && python -m bff_api.cli cache warm-tier 2 --max-movies \$((TIER2_MAX_MOVIES / 10)) --verbose >> /app/logs/tier2-warming.log 2>&1"

***REMOVED*** Tier 3: Full catalog (weekly, smaller sample) - DEV FREQUENCY
0 3 * * 0 su app -c "cd /app && python -m bff_api.cli cache warm-tier 3 --max-movies \$((TIER3_MAX_MOVIES / 5)) --verbose >> /app/logs/tier3-warming.log 2>&1"

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