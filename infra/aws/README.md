# NextWatch AWS Infrastructure Scripts

This directory contains all AWS-related scripts and documentation for deploying and managing NextWatch monitoring infrastructure.

## 📁 Directory Structure

```
aws/
├── deployment/          # Main deployment scripts
├── setup/              # Environment and configuration setup
├── monitoring/         # Monitoring-specific utilities
├── troubleshooting/    # Fix and diagnostic scripts
├── docs/              # Documentation and guides
└── README.md          # This file
```

## 🚀 Quick Start

### One-Click Deployment

```bash
./deployment/deploy-monitoring-one-click.sh
```

This master script will:

1. Check your AWS environment
2. Configure security groups
3. Deploy the complete monitoring stack

## 📂 Script Categories

### 🚀 **Deployment Scripts** (`deployment/`)

| Script                             | Purpose                                                   | Usage                                         |
| ---------------------------------- | --------------------------------------------------------- | --------------------------------------------- |
| `deploy-monitoring-one-click.sh`   | **Master orchestrator** - Complete end-to-end deployment  | `./deployment/deploy-monitoring-one-click.sh` |
| `deploy-monitoring-to-existing.sh` | Core deployment worker - Handles actual Docker deployment | Called by one-click script                    |

**Workflow:**

```
deploy-monitoring-one-click.sh
├── setup/check-environment.sh
├── setup/open-monitoring-ports.sh
└── deployment/deploy-monitoring-to-existing.sh
```

### ⚙️ **Setup Scripts** (`setup/`)

| Script                     | Purpose                                           | Usage                              |
| -------------------------- | ------------------------------------------------- | ---------------------------------- |
| `check-environment.sh`     | Validates AWS environment and NextWatch services  | `./setup/check-environment.sh`     |
| `open-monitoring-ports.sh` | Configures security groups for monitoring access  | `./setup/open-monitoring-ports.sh` |
| `setup-ssl-monitoring.sh`  | Sets up SSL/TLS with Let's Encrypt for monitoring | `./setup/setup-ssl-monitoring.sh`  |

### 📊 **Monitoring Scripts** (`monitoring/`)

| Script                    | Purpose                                          | Usage                                  |
| ------------------------- | ------------------------------------------------ | -------------------------------------- |
| `add-loki-integration.sh` | Adds Loki log aggregation to existing monitoring | `./monitoring/add-loki-integration.sh` |

### 🔧 **Troubleshooting Scripts** (`troubleshooting/`)

| Script                   | Purpose                                               | Usage                                      |
| ------------------------ | ----------------------------------------------------- | ------------------------------------------ |
| `fix-grafana-subpath.sh` | Fixes Grafana subpath configuration for reverse proxy | `./troubleshooting/fix-grafana-subpath.sh` |

### 📚 **Documentation** (`docs/`)

| Document                   | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `DOCKER_NETWORKING_FIX.md` | Explains Docker networking configuration for monitoring |

## 🎯 Common Use Cases

### First-Time Deployment

```bash
# Complete setup from scratch
./deployment/deploy-monitoring-one-click.sh
```

### Environment Validation Only

```bash
# Check if your AWS environment is ready
./setup/check-environment.sh
```

### Security Configuration Only

```bash
# Just configure monitoring ports
./setup/open-monitoring-ports.sh
```

### Add SSL to Existing Monitoring

```bash
# Set up HTTPS for your monitoring stack
./setup/setup-ssl-monitoring.sh
```

### Fix Grafana Issues

```bash
# Fix Grafana subpath problems
./troubleshooting/fix-grafana-subpath.sh
```

## 📊 Environment Configuration

### Monitoring Environment Files

The monitoring stack uses environment files for configuration:

- **`.env.monitoring.prod`**: Full production configuration (120+ variables)
- **`env/monitoring.prod.example`**: Template for new environments

To get started:

```bash
cd infra
cp env/monitoring.prod.example .env.monitoring.prod
nano .env.monitoring.prod
```

## 🔍 Script Dependencies

### Prerequisites

- AWS CLI configured
- SSH key for EC2 access
- NextWatch services running on target instance

### Dependency Chain

```
check-environment.sh → open-monitoring-ports.sh → deploy-monitoring-to-existing.sh
```

## 🌐 Access URLs (After Deployment)

- **📊 Grafana**: `http://YOUR_IP:3001` (admin/<GRAFANA_ADMIN_PASSWORD>)
- **🔍 Prometheus**: `http://YOUR_IP:9090`
- **📢 AlertManager**: `http://YOUR_IP:9093`
- **📋 Loki**: `http://YOUR_IP:3100`

## 🛡️ Security Notes

- Scripts automatically detect and configure your current IP
- Monitoring ports are restricted to your IP by default
- SSL setup available for production environments
- Domain-based access supported

## 📋 Troubleshooting

### Common Issues

1. **SSH Connection Failed**: Check SSH key path and security groups
2. **Monitoring Ports Blocked**: Run `./setup/open-monitoring-ports.sh`
3. **Services Not Found**: Verify NextWatch services are running
4. **Grafana Subpath Issues**: Run `./troubleshooting/fix-grafana-subpath.sh`

### Debug Commands

```bash
# Check environment
./setup/check-environment.sh

# Verify monitoring stack
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_IP 'cd /opt/nextwatch-monitoring && sudo docker compose ps'

# Check logs
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_IP 'cd /opt/nextwatch-monitoring && sudo docker compose logs grafana'
```

## 🔄 Updates and Maintenance

### Update Monitoring Stack

```bash
# Re-run deployment to update
./deployment/deploy-monitoring-to-existing.sh
```

### Add New Monitoring Features

```bash
# Add log aggregation
./monitoring/add-loki-integration.sh
```

## 🤝 Contributing

When adding new scripts:

1. Place in appropriate category directory
2. Update this README
3. Follow existing naming conventions
4. Include proper error handling and logging
5. Test on clean AWS environment

---

**💡 Tip**: Always run `./setup/check-environment.sh` first to ensure your AWS environment is ready for monitoring deployment.
