***REMOVED***!/bin/bash

***REMOVED*** NextWatch Production Monitoring Stack Deployment Script
***REMOVED*** This script deploys the monitoring infrastructure to production

set -euo pipefail

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

***REMOVED*** Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra"
MONITORING_DIR="$INFRA_DIR/monitoring"

***REMOVED*** Environment file
ENV_FILE="$INFRA_DIR/.env.monitoring.prod"
COMPOSE_FILE="$INFRA_DIR/compose/monitoring.yml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} NextWatch Production Monitoring Setup ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

***REMOVED*** Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

***REMOVED*** Function to check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."

    local deps=("docker" "openssl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep is not installed. Please install it first."
            exit 1
        fi
    done

    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        log_error "Neither 'docker compose' nor 'docker-compose' found. Please install Docker Compose."
        exit 1
    fi

    log_success "All dependencies are installed"
}

***REMOVED*** Function to check if environment file exists
check_environment() {
    log_info "Checking environment configuration..."

    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Production environment file not found: $ENV_FILE"
        log_info "Creating from template..."

    if [[ -f "$INFRA_DIR/env/monitoring.prod.example" ]]; then
            cp "$INFRA_DIR/env/monitoring.prod.example" "$ENV_FILE"
            log_warning "Please edit $ENV_FILE with your production values before continuing"
            echo
            echo "Required configurations:"
            echo "  - GRAFANA_ADMIN_PASSWORD"
            echo "  - GRAFANA_SECRET_KEY"
            echo "  - SMTP configuration for alerts"
            echo "  - Alert email addresses"
            echo
            read -p "Press Enter after configuring the environment file..."
        else
            log_error "Environment template not found. Please create $ENV_FILE manually."
            exit 1
        fi
    fi

    ***REMOVED*** Source the environment file to validate
    if ! source "$ENV_FILE"; then
        log_error "Failed to source environment file. Please check for syntax errors."
        exit 1
    fi

    ***REMOVED*** Check required variables
    local required_vars=("PRODUCTION_DOMAIN" "GRAFANA_ADMIN_PASSWORD" "SMTP_HOST" "ALERT_EMAIL_TO")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    log_success "Environment configuration validated"
}

***REMOVED*** Function to create necessary directories
create_directories() {
    log_info "Creating monitoring directories..."

    local dirs=(
        "$MONITORING_DIR/prometheus/data"
        "$MONITORING_DIR/grafana/data"
        "$MONITORING_DIR/alertmanager/data"
        "$MONITORING_DIR/loki/data"
    )

    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        ***REMOVED*** Set appropriate permissions for Docker containers
        sudo chown -R 472:472 "$MONITORING_DIR/grafana/data" 2>/dev/null || true
        sudo chown -R 65534:65534 "$MONITORING_DIR/prometheus/data" 2>/dev/null || true
        sudo chown -R 65534:65534 "$MONITORING_DIR/alertmanager/data" 2>/dev/null || true
        sudo chown -R 10001:10001 "$MONITORING_DIR/loki/data" 2>/dev/null || true
    done

    log_success "Monitoring directories created"
}

***REMOVED*** Function to setup SSL certificates (if needed)
setup_ssl() {
    if [[ -n "${SSL_CERT_PATH:-}" ]] && [[ -n "${SSL_KEY_PATH:-}" ]]; then
        log_info "Checking SSL certificates..."

        if [[ ! -f "$SSL_CERT_PATH" ]] || [[ ! -f "$SSL_KEY_PATH" ]]; then
            log_warning "SSL certificates not found. Monitoring will run without HTTPS."
            log_info "To enable HTTPS, place certificates at:"
            log_info "  Certificate: $SSL_CERT_PATH"
            log_info "  Private Key: $SSL_KEY_PATH"
        else
            log_success "SSL certificates found"
        fi
    fi
}

***REMOVED*** Function to create Grafana database
setup_grafana_database() {
    log_info "Setting up Grafana database..."

    ***REMOVED*** Check if PostgreSQL is accessible
    if command -v psql &> /dev/null; then
        ***REMOVED*** Create Grafana database and user
        log_info "Creating Grafana database in PostgreSQL..."

        ***REMOVED*** This assumes PostgreSQL is running and accessible
        ***REMOVED*** You may need to adjust connection parameters
        PGPASSWORD="${POSTGRES_PASSWORD}" psql -h localhost -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "
        CREATE DATABASE ${GRAFANA_DB_NAME};
        CREATE USER ${GRAFANA_DB_USER} WITH PASSWORD '${GRAFANA_DB_PASSWORD}';
        GRANT ALL PRIVILEGES ON DATABASE ${GRAFANA_DB_NAME} TO ${GRAFANA_DB_USER};
        " 2>/dev/null || log_warning "Database setup failed or already exists"

        log_success "Grafana database configured"
    else
        log_warning "PostgreSQL client not found. Skipping database setup."
        log_info "Please create the Grafana database manually:"
        log_info "  Database: ${GRAFANA_DB_NAME}"
        log_info "  User: ${GRAFANA_DB_USER}"
    fi
}

***REMOVED*** Function to validate configuration files
validate_configs() {
    log_info "Validating configuration files..."

    local configs=(
        "$MONITORING_DIR/prometheus/prometheus.prod.yml"
        "$MONITORING_DIR/alertmanager/alertmanager.prod.yml"
        "$MONITORING_DIR/loki/loki.prod.yml"
        "$MONITORING_DIR/promtail/promtail.prod.yml"
    )

    for config in "${configs[@]}"; do
        if [[ ! -f "$config" ]]; then
            log_error "Configuration file not found: $config"
            exit 1
        fi
    done

    log_success "Configuration files validated"
}

***REMOVED*** Function to deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack to production..."

    cd "$INFRA_DIR"

    ***REMOVED*** Pull latest images
    log_info "Pulling latest Docker images..."
    $DOCKER_COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

    ***REMOVED*** Deploy monitoring stack
    log_info "Starting monitoring services..."
    $DOCKER_COMPOSE_CMD -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    ***REMOVED*** Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30

    ***REMOVED*** Check service health
    local services=("prometheus-prod" "grafana-prod" "alertmanager-prod" "loki-prod")
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            log_success "$service is running"
        else
            log_error "$service failed to start"
            docker logs "$service" --tail 20
            exit 1
        fi
    done
}

***REMOVED*** Function to display access information
show_access_info() {
    echo
    log_success "Monitoring stack deployed successfully!"
    echo
    echo -e "${GREEN}Access Information:${NC}"
    echo "  🌐 Production Domain: https://${PRODUCTION_DOMAIN}"
    echo "  📊 Prometheus: https://${PRODUCTION_DOMAIN}/prometheus/"
    echo "  📈 Grafana: https://${PRODUCTION_DOMAIN}/grafana/ (admin / ${GRAFANA_ADMIN_PASSWORD})"
    echo "  🔔 AlertManager: https://${PRODUCTION_DOMAIN}/alertmanager/"
    echo "  📋 Loki: http://${PRODUCTION_DOMAIN}:3100"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Configure reverse proxy (Nginx/Apache) with SSL"
    echo "  2. Set up Grafana dashboards"
    echo "  3. Test alert notifications"
    echo "  4. Configure backup for persistent data"
    echo
    echo -e "${BLUE}Monitoring Data Locations:${NC}"
    echo "  📊 Prometheus: $MONITORING_DIR/prometheus/data"
    echo "  📈 Grafana: $MONITORING_DIR/grafana/data"
    echo "  🔔 AlertManager: $MONITORING_DIR/alertmanager/data"
    echo "  📋 Loki: $MONITORING_DIR/loki/data"
}

***REMOVED*** Function to create backup script
create_backup_script() {
    log_info "Creating backup script..."

    cat > "$SCRIPT_DIR/backup-monitoring.sh" << 'EOF'
***REMOVED***!/bin/bash
***REMOVED*** Backup script for NextWatch monitoring data

BACKUP_DIR="/backups/monitoring/$(date +%Y%m%d_%H%M%S)"
MONITORING_DIR="/path/to/infra/monitoring"

mkdir -p "$BACKUP_DIR"

***REMOVED*** Backup Prometheus data
docker run --rm -v prometheus-data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/prometheus-data.tar.gz -C /data .

***REMOVED*** Backup Grafana data
docker run --rm -v grafana-data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/grafana-data.tar.gz -C /data .

***REMOVED*** Backup AlertManager data
docker run --rm -v alertmanager-data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/alertmanager-data.tar.gz -C /data .

***REMOVED*** Backup configuration files
tar czf "$BACKUP_DIR/monitoring-configs.tar.gz" -C "$MONITORING_DIR" .

echo "Backup completed: $BACKUP_DIR"
EOF

    chmod +x "$SCRIPT_DIR/backup-monitoring.sh"
    log_success "Backup script created at $SCRIPT_DIR/backup-monitoring.sh"
}

***REMOVED*** Main execution
main() {
    log_info "Starting production monitoring deployment..."

    check_dependencies
    check_environment
    create_directories
    setup_ssl
    setup_grafana_database
    validate_configs
    deploy_monitoring
    create_backup_script
    show_access_info

    log_success "Production monitoring deployment completed!"
}

***REMOVED*** Run the main function
main "$@"
