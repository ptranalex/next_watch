***REMOVED***!/bin/sh
set -e

echo "🚀 Starting BFF API with cache warming..."

***REMOVED*** Check if we should enable cache warming
if [ "${ENABLE_CACHE_WARMING:-true}" = "true" ]; then
    echo "⏰ Cache warming is ENABLED"
    
    ***REMOVED*** Create cron jobs based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "⏰ Setting up PRODUCTION cache warming schedule..."
        cat > /tmp/crontab << 'PROD_EOF'
***REMOVED*** Production Cache Warming Schedule - run as app user
0 7 * * * su app -c "cd /app && python -m bff_api.cli warm warm-popular --limit 1000 >> /app/logs/warming.log 2>&1"
0 12 * * * su app -c "cd /app && python -m bff_api.cli warm warm-popular --limit 500 >> /app/logs/warming.log 2>&1"
0 17 * * * su app -c "cd /app && python -m bff_api.cli warm warm-popular --limit 500 >> /app/logs/warming.log 2>&1"
*/30 * * * * su app -c "cd /app && python -m bff_api.cli warm warm-popular --limit 100 >> /app/logs/warming.log 2>&1"
*/5 * * * * su app -c "cd /app && python -m bff_api.cli warm health-check >> /app/logs/health.log 2>&1"
PROD_EOF
    else
        echo "⏰ Setting up DEVELOPMENT cache warming schedule..."
        cat > /tmp/crontab << 'DEV_EOF'
***REMOVED*** Development Cache Warming Schedule (lighter) - run as app user
0 */2 * * * su app -c "cd /app && python -m bff_api.cli warm warm-popular --limit 50 >> /app/logs/warming.log 2>&1"
*/10 * * * * su app -c "cd /app && python -m bff_api.cli warm health-check >> /app/logs/health.log 2>&1"
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