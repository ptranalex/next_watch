***REMOVED*** NextWatch AWS Infrastructure Scripts

This directory contains all AWS-related scripts and documentation for deploying and managing NextWatch monitoring infrastructure.

***REMOVED******REMOVED*** 📁 Directory Structure

```
aws/
├── deployment/          ***REMOVED*** Main deployment scripts
├── setup/              ***REMOVED*** Environment and configuration setup
├── monitoring/         ***REMOVED*** Monitoring-specific utilities
├── troubleshooting/    ***REMOVED*** Fix and diagnostic scripts
├── docs/              ***REMOVED*** Documentation and guides
└── README.md          ***REMOVED*** This file
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** One-Click Deployment

```bash
./deployment/deploy-monitoring-one-click.sh
```

This master script will:

1. Check your AWS environment
2. Configure security groups
3. Deploy the complete monitoring stack

***REMOVED******REMOVED*** 📂 Script Categories

***REMOVED******REMOVED******REMOVED*** 🚀 **Deployment Scripts** (`deployment/`)

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

***REMOVED******REMOVED******REMOVED*** ⚙️ **Setup Scripts** (`setup/`)

| Script                     | Purpose                                           | Usage                              |
| -------------------------- | ------------------------------------------------- | ---------------------------------- |
| `check-environment.sh`     | Validates AWS environment and NextWatch services  | `./setup/check-environment.sh`     |
| `open-monitoring-ports.sh` | Configures security groups for monitoring access  | `./setup/open-monitoring-ports.sh` |
| `setup-ssl-monitoring.sh`  | Sets up SSL/TLS with Let's Encrypt for monitoring | `./setup/setup-ssl-monitoring.sh`  |

***REMOVED******REMOVED******REMOVED*** 📊 **Monitoring Scripts** (`monitoring/`)

| Script                    | Purpose                                          | Usage                                  |
| ------------------------- | ------------------------------------------------ | -------------------------------------- |
| `add-loki-integration.sh` | Adds Loki log aggregation to existing monitoring | `./monitoring/add-loki-integration.sh` |

***REMOVED******REMOVED******REMOVED*** 🔧 **Troubleshooting Scripts** (`troubleshooting/`)

| Script                   | Purpose                                               | Usage                                      |
| ------------------------ | ----------------------------------------------------- | ------------------------------------------ |
| `fix-grafana-subpath.sh` | Fixes Grafana subpath configuration for reverse proxy | `./troubleshooting/fix-grafana-subpath.sh` |

***REMOVED******REMOVED******REMOVED*** 📚 **Documentation** (`docs/`)

| Document                   | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `DOCKER_NETWORKING_FIX.md` | Explains Docker networking configuration for monitoring |

***REMOVED******REMOVED*** 🎯 Common Use Cases

***REMOVED******REMOVED******REMOVED*** First-Time Deployment

```bash
***REMOVED*** Complete setup from scratch
./deployment/deploy-monitoring-one-click.sh
```

***REMOVED******REMOVED******REMOVED*** Environment Validation Only

```bash
***REMOVED*** Check if your AWS environment is ready
./setup/check-environment.sh
```

***REMOVED******REMOVED******REMOVED*** Security Configuration Only

```bash
***REMOVED*** Just configure monitoring ports
./setup/open-monitoring-ports.sh
```

***REMOVED******REMOVED******REMOVED*** Add SSL to Existing Monitoring

```bash
***REMOVED*** Set up HTTPS for your monitoring stack
./setup/setup-ssl-monitoring.sh
```

***REMOVED******REMOVED******REMOVED*** Fix Grafana Issues

```bash
***REMOVED*** Fix Grafana subpath problems
./troubleshooting/fix-grafana-subpath.sh
```

***REMOVED******REMOVED*** 📊 Environment Configuration

***REMOVED******REMOVED******REMOVED*** Monitoring Environment Files

The monitoring stack uses environment files for configuration:

- **`.env.monitoring.prod`**: Full production configuration (120+ variables)
- **`.env.monitoring.simple`**: Minimal configuration (17 variables, used as fallback)
- **`env.monitoring.prod.example`**: Template for new environments

See `../MONITORING_ENV_GUIDE.md` for detailed configuration instructions.

***REMOVED******REMOVED*** 🔍 Script Dependencies

***REMOVED******REMOVED******REMOVED*** Prerequisites

- AWS CLI configured
- SSH key for EC2 access
- NextWatch services running on target instance

***REMOVED******REMOVED******REMOVED*** Dependency Chain

```
check-environment.sh → open-monitoring-ports.sh → deploy-monitoring-to-existing.sh
```

***REMOVED******REMOVED*** 🌐 Access URLs (After Deployment)

- **📊 Grafana**: `http://YOUR_IP:3001` (admin/NextWatch2024Admin)
- **🔍 Prometheus**: `http://YOUR_IP:9090`
- **📢 AlertManager**: `http://YOUR_IP:9093`
- **📋 Loki**: `http://YOUR_IP:3100`

***REMOVED******REMOVED*** 🛡️ Security Notes

- Scripts automatically detect and configure your current IP
- Monitoring ports are restricted to your IP by default
- SSL setup available for production environments
- Domain-based access supported

***REMOVED******REMOVED*** 📋 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

1. **SSH Connection Failed**: Check SSH key path and security groups
2. **Monitoring Ports Blocked**: Run `./setup/open-monitoring-ports.sh`
3. **Services Not Found**: Verify NextWatch services are running
4. **Grafana Subpath Issues**: Run `./troubleshooting/fix-grafana-subpath.sh`

***REMOVED******REMOVED******REMOVED*** Debug Commands

```bash
***REMOVED*** Check environment
./setup/check-environment.sh

***REMOVED*** Verify monitoring stack
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_IP 'cd /opt/nextwatch-monitoring && sudo docker-compose ps'

***REMOVED*** Check logs
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_IP 'cd /opt/nextwatch-monitoring && sudo docker-compose logs grafana'
```

***REMOVED******REMOVED*** 🔄 Updates and Maintenance

***REMOVED******REMOVED******REMOVED*** Update Monitoring Stack

```bash
***REMOVED*** Re-run deployment to update
./deployment/deploy-monitoring-to-existing.sh
```

***REMOVED******REMOVED******REMOVED*** Add New Monitoring Features

```bash
***REMOVED*** Add log aggregation
./monitoring/add-loki-integration.sh
```

***REMOVED******REMOVED*** 🤝 Contributing

When adding new scripts:

1. Place in appropriate category directory
2. Update this README
3. Follow existing naming conventions
4. Include proper error handling and logging
5. Test on clean AWS environment

---

**💡 Tip**: Always run `./setup/check-environment.sh` first to ensure your AWS environment is ready for monitoring deployment.
