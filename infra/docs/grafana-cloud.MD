***REMOVED*** Grafana Cloud Migration - Technical Design & Implementation Plan

***REMOVED******REMOVED*** Executive Summary

**Objective**: Migrate self-hosted monitoring stack (Prometheus, Grafana, Alertmanager, Loki, Tempo) to Grafana Cloud to reduce infrastructure costs, improve reliability, and minimize operational overhead.

**Expected Benefits**:

- Cost reduction: Eliminate monitoring infrastructure hosting costs (~$500-800/month)
- Zero maintenance: No more upgrades, patching, or capacity planning
- Enhanced reliability: 99.9% SLA vs self-managed availability
- Improved performance: Global CDN and optimized storage backends
- Advanced features: Access to Grafana Cloud-exclusive capabilities (AI/ML insights, SLO management)

***REMOVED******REMOVED*** Current State Analysis

***REMOVED******REMOVED******REMOVED*** Self-Hosted Stack Overview

Our current monitoring stack consists of:

**Core Components**:

- **Prometheus**: Metrics collection and storage (retention: 30 days, 50GB)
- **Grafana**: Visualization and dashboards (10.2.0)
- **Alertmanager**: Alert routing and notifications (v0.26.0)
- **Loki**: Log aggregation (retention configured)
- **Tempo**: Distributed tracing
- **Blackbox Exporter**: Health endpoint monitoring
- **Node Exporter**: System metrics
- **cAdvisor**: Container metrics

**Monitored Services** (6 NextWatch APIs):

- backend-api (port 8000)
- bff-api (port 8000)
- auth-api (port 8000)
- search-api (port 8000)
- ml-api (port 8000)
- recommendation-api (port 8000)

**Current Dashboards & Alerts**:

- 10+ service-specific dashboards
- Health monitoring dashboards (healthy/degraded/unhealthy states)
- 50+ alerting rules covering availability, performance, and business metrics
- Advanced health status monitoring (3-tier: healthy/degraded/unhealthy)

**Resource Usage**:

- Prometheus: 2GB memory, 1 CPU, 50GB storage
- Grafana: 1GB memory, 0.5 CPU
- Total infrastructure cost: ~$600-800/month

***REMOVED******REMOVED*** Technical Design

***REMOVED******REMOVED******REMOVED*** Migration Architecture

***REMOVED******REMOVED******REMOVED******REMOVED*** Target Grafana Cloud Stack Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                        Grafana Cloud                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Hosted Grafana │  │ Grafana Mimir   │  │   Grafana Loki  │  │
│  │   (Visualization)│  │   (Metrics)     │  │     (Logs)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Grafana Tempo  │  │ Grafana Alerting│  │   Grafana IRM   │  │
│  │   (Tracing)     │  │ (Alert Manager) │  │  (Incident Mgmt)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NextWatch Services                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Grafana Alloy │  │   Grafana Alloy │  │   Grafana Alloy │  │
│  │   (Metrics)     │  │     (Logs)      │  │   (Traces)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│             │                   │                   │          │
│             ▼                   ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          NextWatch API Services                     │   │
│  │  backend│bff│auth│search│ml│recommendation           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Data Flow Architecture

1. **Metrics**: Services → Grafana Alloy → Grafana Cloud Metrics (Mimir)
2. **Logs**: Services → Grafana Alloy → Grafana Cloud Logs (Loki)
3. **Traces**: Services → Grafana Alloy → Grafana Cloud Traces (Tempo)
4. **Alerts**: Grafana Cloud Alerting → Grafana IRM → External channels

***REMOVED******REMOVED******REMOVED*** Component Migration Strategy

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Grafana Alloy Deployment

**Replace**: Prometheus, Promtail, and OTEL Collector
**Benefits**: Single agent, reduced complexity, better performance

```yaml
***REMOVED*** Alloy configuration structure
grafana_alloy:
  metrics_collection:
    - prometheus.scrape "services" { ... }
    - prometheus.remote_write "grafana_cloud" { ... }

  logs_collection:
    - loki.source.docker { ... }
    - loki.write "grafana_cloud" { ... }

  traces_collection:
    - otelcol.receiver.otlp { ... }
    - otelcol.exporter.otlp "grafana_cloud" { ... }
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Service Discovery & Monitoring

**Maintain**: Current service discovery patterns
**Enhance**: Better labeling and metadata

```yaml
***REMOVED*** Service discovery configuration
service_discovery:
  static_configs:
    - targets:
        - "backend-api:8000"
        - "bff-api:8000"
        - "auth-api:8000"
        - "search-api:8000"
        - "ml-api:8000"
        - "recommendation-api:8000"
      labels:
        environment: "production"
        cluster: "nextwatch-aws"
        region: "ap-southeast-1"
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Health Monitoring Migration

**Preserve**: Current 3-tier health status system
**Enhance**: Advanced SLO capabilities

Current health monitoring approach:

- HTTP 200 + "healthy": Fully operational
- HTTP 200/503 + "degraded": Partial functionality
- HTTP 503 + "unhealthy": Critical issues
- No response: Service down

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Dashboard Migration Strategy

**Approach**: Automated migration with manual validation
**Tools**: Grafana Cloud Migration Assistant + manual refinement

Migration priority:

1. **Critical dashboards**: Service health, API performance
2. **Business dashboards**: User analytics, system metrics
3. **Infrastructure dashboards**: System resources, networking

***REMOVED******REMOVED******REMOVED******REMOVED*** 5. Alerting Migration

**Strategy**: Rule-by-rule migration with improved grouping
**Enhancement**: Leverage Grafana IRM for incident management

Key alert categories:

- Service availability (critical)
- Performance degradation (warning)
- Business metrics (info)
- Infrastructure health (warning)

***REMOVED******REMOVED******REMOVED*** Security & Access Control

***REMOVED******REMOVED******REMOVED******REMOVED*** Authentication & Authorization

```yaml
***REMOVED*** RBAC structure for Grafana Cloud
roles:
  platform_admin:
    - Full dashboard access
    - Alert rule management
    - User management

  service_owner:
    - Service-specific dashboards
    - Service alert configuration
    - Read-only infrastructure metrics

  viewer:
    - Dashboard viewing only
    - No configuration access
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Data Security

- **Encryption**: TLS 1.3 for all data in transit
- **Authentication**: API keys with restricted scope
- **Network**: Private data source connect (PDC) for sensitive data
- **Compliance**: SOC2, GDPR compliant infrastructure

***REMOVED******REMOVED******REMOVED*** Performance & Scalability

***REMOVED******REMOVED******REMOVED******REMOVED*** Expected Performance Improvements (Free Tier)

- **Query latency**: 50% reduction due to optimized storage (within limits)
- **Dashboard load time**: 60% improvement with CDN
- **Alert delivery**: Sub-minute notification delivery
- **Data retention**: **Reduced to 14 days vs current 30 days** ⚠️
- **Operational overhead**: 90% reduction in maintenance tasks

***REMOVED******REMOVED******REMOVED******REMOVED*** Free Tier Constraints & Benefits

- **Metrics ingestion**: **Limited to 10k series** vs current unlimited collection ⚠️
- **Logs volume**: **50GB/month limit** vs current unlimited ⚠️
- **Users**: **Maximum 3 users** vs unlimited ⚠️
- **Query concurrency**: Auto-scaling within free tier limits
- **Geographic distribution**: Global CDN (same as paid)
- **Backup & DR**: Automated (same as paid)
- **Cost**: **$0 vs $565/month** ✅

***REMOVED******REMOVED*** Implementation Plan

***REMOVED******REMOVED******REMOVED*** Phase 1: Foundation Setup (Week 1)

**Goal**: Establish Grafana Cloud environment and basic connectivity

**Tasks**:

1. **Day 1-2: Account Setup**

   - Create Grafana Cloud stack (Free tier)
   - Configure basic authentication (note: SAML/SSO not available in free tier)
   - Set up 3 user accounts (maximum for free tier)
   - Generate API keys and connection credentials
   - Configure usage monitoring dashboards to track free tier limits

2. **Day 3-4: Parallel Environment Setup**

   - Install Grafana Alloy on monitoring hosts
   - Configure basic metrics collection (non-production)
   - Test connectivity to Grafana Cloud endpoints
   - Validate data ingestion with sample metrics

3. **Day 5-7: Service Discovery & Optimization**
   - Configure service discovery for **critical services first** (backend, bff, auth APIs)
   - Implement aggressive metric filtering to stay under 10k series limit
   - Test metrics collection with heavy filtering enabled
   - Validate metric cardinality stays well below free tier limits
   - Set up automated alerting when approaching usage thresholds

**Deliverables**:

- ✅ Functional Grafana Cloud stack
- ✅ Alloy agents deployed and tested
- ✅ Basic metrics flowing to cloud
- ✅ Cost monitoring dashboard

***REMOVED******REMOVED******REMOVED*** Phase 2: Metrics Migration (Week 2)

**Goal**: Migrate all metrics collection to Grafana Cloud

**Tasks**:

1. **Day 1-2: Production Metrics Migration**

   - Deploy Alloy to production monitoring hosts
   - Configure dual-write: self-hosted + cloud (validation period)
   - Migrate Prometheus scraping configurations
   - Implement advanced labeling and metadata

2. **Day 3-4: Health Monitoring Migration**

   - Configure blackbox exporter equivalent in Alloy
   - Migrate 3-tier health status monitoring
   - Test health endpoint monitoring for all services
   - Validate probe success metrics

3. **Day 5-7: Validation & Optimization**
   - Compare metrics between self-hosted and cloud
   - Optimize scraping intervals and retention
   - Configure metric preprocessing and filtering
   - Monitor and optimize costs

**Deliverables**:

- ✅ All metrics flowing to both environments
- ✅ Health monitoring functional in cloud
- ✅ Metric accuracy validation complete
- ✅ Cost optimization applied

***REMOVED******REMOVED******REMOVED*** Phase 3: Dashboard Migration (Week 3)

**Goal**: Migrate and enhance all dashboards

**Tasks**:

1. **Day 1-2: Critical Dashboard Migration**

   - Export current dashboards using Migration Assistant
   - Migrate service health monitoring dashboard
   - Migrate API performance dashboards
   - Test and validate critical visualizations

2. **Day 3-4: Business & Infrastructure Dashboards**

   - Migrate user analytics dashboard
   - Migrate system metrics dashboards
   - Update data source configurations
   - Enhance dashboards with cloud-native features

3. **Day 5-7: Dashboard Enhancement**
   - Implement improved templating and variables
   - Add SLO tracking capabilities
   - Configure dashboard permissions and sharing
   - Create migration documentation

**Deliverables**:

- ✅ All dashboards migrated and functional
- ✅ Enhanced visualizations with cloud features
- ✅ Proper access control implemented
- ✅ Dashboard documentation updated

***REMOVED******REMOVED******REMOVED*** Phase 4: Alerting & IRM Integration (Week 4)

**Goal**: Migrate alerting rules and enhance incident management

**Tasks**:

1. **Day 1-2: Alert Rule Migration**

   - Export existing Prometheus/Alertmanager rules
   - Convert to Grafana Cloud alerting format
   - Configure alert rule groups and timing
   - Test alert rule evaluation

2. **Day 3-4: Notification Configuration**

   - Configure contact points (Slack, email, webhooks)
   - Set up notification policies and routing
   - Configure mute timings and silences
   - Integrate with Grafana IRM for incident management

3. **Day 5-7: Advanced Alerting Features**
   - Implement multi-dimensional alerting
   - Configure SLO-based alerting
   - Set up anomaly detection alerts
   - Test end-to-end alert workflows

**Deliverables**:

- ✅ All alert rules migrated and active
- ✅ Notification channels configured
- ✅ IRM integration functional
- ✅ Alert testing and validation complete

***REMOVED******REMOVED******REMOVED*** Phase 5: Logs & Traces Migration (Week 5)

**Goal**: Migrate log aggregation and distributed tracing

**Tasks**:

1. **Day 1-2: Logs Migration**

   - Configure Alloy for log collection
   - Migrate Promtail configurations
   - Set up log parsing and labeling rules
   - Test log ingestion and querying

2. **Day 3-4: Traces Migration**

   - Configure OTEL collection in Alloy
   - Migrate Tempo tracing configuration
   - Test trace ingestion and correlation
   - Validate service map generation

3. **Day 5-7: Observability Correlation**
   - Configure logs-to-metrics correlation
   - Set up traces-to-logs correlation
   - Test exemplar functionality
   - Implement unified observability workflows

**Deliverables**:

- ✅ Logs flowing to Grafana Cloud Loki
- ✅ Traces flowing to Grafana Cloud Tempo
- ✅ Correlation between metrics, logs, and traces
- ✅ Unified observability experience

***REMOVED******REMOVED******REMOVED*** Phase 6: Validation & Cutover (Week 6)

**Goal**: Final validation and complete migration

**Tasks**:

1. **Day 1-2: Comprehensive Testing**

   - End-to-end monitoring workflow testing
   - Load testing with realistic traffic patterns
   - Disaster recovery testing
   - Performance benchmarking

2. **Day 3-4: Team Training & Documentation**

   - Train operations team on Grafana Cloud
   - Update runbooks and procedures
   - Create troubleshooting guides
   - Document new workflows and capabilities

3. **Day 5-7: Cutover & Cleanup**
   - Switch primary monitoring to Grafana Cloud
   - Graceful shutdown of self-hosted stack
   - Clean up old infrastructure
   - Monitor for 48 hours post-cutover

**Deliverables**:

- ✅ Production cutover completed
- ✅ Self-hosted infrastructure decommissioned
- ✅ Team trained on new platform
- ✅ Complete documentation available

***REMOVED******REMOVED*** Risk Management & Mitigation

***REMOVED******REMOVED******REMOVED*** Technical Risks

| Risk                           | Impact     | Probability | Mitigation                               |
| ------------------------------ | ---------- | ----------- | ---------------------------------------- |
| Data loss during migration     | High       | Low         | Dual-write approach, backups             |
| Performance degradation        | Medium     | Low         | Gradual cutover, rollback plan           |
| Alert rule gaps                | High       | Medium      | Rule-by-rule validation                  |
| Dashboard functionality loss   | Medium     | Medium      | Migration assistant + manual testing     |
| **Exceeding free tier limits** | **High**   | **High**    | **Aggressive filtering, monitoring**     |
| **Limited retention impact**   | **Medium** | **High**    | **External backup, historical analysis** |
| **User access constraints**    | **Low**    | **High**    | **Shared accounts, dashboard sharing**   |

***REMOVED******REMOVED******REMOVED*** Operational Risks

| Risk               | Impact | Probability | Mitigation                            |
| ------------------ | ------ | ----------- | ------------------------------------- |
| Team unfamiliarity | Low    | High        | Training program, documentation       |
| Vendor lock-in     | Medium | High        | Export capabilities, open standards   |
| Service disruption | High   | Low         | Phased migration, rollback procedures |
| Compliance issues  | Medium | Low         | Security review, audit preparation    |

***REMOVED******REMOVED******REMOVED*** Rollback Strategy

1. **Phase-level rollback**: Return to previous phase configuration
2. **Component rollback**: Selective rollback of individual components
3. **Emergency rollback**: Complete return to self-hosted stack
4. **Data preservation**: Maintain dual-write during critical phases

***REMOVED******REMOVED*** Cost Analysis

***REMOVED******REMOVED******REMOVED*** Current Costs (Monthly)

```
Infrastructure costs:
- EC2 instances (monitoring): $300
- EBS storage (50GB): $50
- Network transfer: $25
- Load balancer: $25
- Backup storage: $15
- Operational overhead: $150
Total: ~$565/month
```

***REMOVED******REMOVED******REMOVED*** Grafana Cloud Costs (Free Tier)

```
Free Tier Limits:
- Base cost: $0/month
- Metrics: 10k series (14-day retention)
- Logs: 50 GB/month (14-day retention)
- Traces: 50 GB/month (14-day retention)
- Profiles: 50 GB/month (14-day retention)
- Users: 3 users maximum
- Dashboards & alerts: ✅ Included
Total: $0/month
```

***REMOVED******REMOVED******REMOVED*** Cost Savings & Trade-offs

- **Monthly savings**: $565 (100% infrastructure cost reduction)
- **Annual savings**: $6,780
- **ROI timeline**: Immediate
- **Trade-offs**: Limited retention (14 days vs 30 days), metric series cap, user limits
- **Risk mitigation**: Implement aggressive metric filtering and sampling

***REMOVED******REMOVED******REMOVED*** Free Tier Optimization Strategies

***REMOVED******REMOVED******REMOVED******REMOVED*** Critical: Staying Within Free Tier Limits

**Metric Series Management (10k limit)**:

1. **Aggressive label filtering**: Remove high-cardinality labels (request_id, user_id, etc.)
2. **Recording rules**: Pre-aggregate commonly used queries
3. **Service prioritization**: Focus on critical services (backend, bff, auth APIs)
4. **Metric drop rules**: Drop less critical metrics (fine-grained percentiles, debug metrics)

**Log Volume Management (50GB/month)**:

1. **Structured logging**: Use consistent log levels (ERROR, WARN only for production)
2. **Sampling**: 1% sampling for DEBUG logs, 10% for INFO logs
3. **Log parsing**: Extract only essential fields for analysis
4. **Retention strategy**: Leverage 14-day window for incident analysis

**User Access Management (3 users)**:

1. **Shared service accounts**: Use for automation and alerts
2. **Rotation strategy**: Admin, on-call engineer, + 1 developer rotation
3. **View-only access**: Use dashboard sharing for broader team access

***REMOVED******REMOVED******REMOVED******REMOVED*** Enhanced Monitoring Strategy for Free Tier

```yaml
***REMOVED*** Optimized Alloy configuration for free tier
prometheus.scrape "critical_services" {
  targets = [
    {"__address__" = "backend-api:8000"},
    {"__address__" = "bff-api:8000"},
    {"__address__" = "auth-api:8000"},
  ]

  ***REMOVED*** Aggressive metric filtering
  metric_relabel_configs = [
    {
      source_labels = ["__name__"]
      regex = "(request_duration_seconds|http_requests_total|up|health_status)"
      action = "keep"
    },
    {
      source_labels = ["method"]
      regex = "(GET|POST|PUT|DELETE)"
      action = "keep"
    }
  ]
}

loki.source.docker "containers" {
  ***REMOVED*** Only collect ERROR and WARN logs
  relabel_rules = [
    {
      source_labels = ["__meta_docker_container_label_log_level"]
      regex = "(ERROR|WARN)"
      action = "keep"
    }
  ]
}
```

***REMOVED******REMOVED*** Free Tier Migration Strategy

***REMOVED******REMOVED******REMOVED*** Prioritization Framework

Given the free tier constraints, we must prioritize monitoring based on business impact:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Tier 1: Critical (Must Monitor)**

- **Services**: backend-api, bff-api, auth-api
- **Metrics**: HTTP requests, response times, error rates, health status
- **Logs**: ERROR and FATAL level only
- **Alerts**: Service down, high error rates, critical performance degradation

***REMOVED******REMOVED******REMOVED******REMOVED*** **Tier 2: Important (Monitor with Sampling)**

- **Services**: search-api, ml-api, recommendation-api
- **Metrics**: Basic health and availability only
- **Logs**: ERROR level with 50% sampling
- **Alerts**: Service down only

***REMOVED******REMOVED******REMOVED******REMOVED*** **Tier 3: Infrastructure (Minimal Monitoring)**

- **Metrics**: Node health, disk space critical alerts only
- **Logs**: System critical errors only (OOM, disk full)
- **Alerts**: Infrastructure failure only

***REMOVED******REMOVED******REMOVED*** Metric Budget Allocation (10k series limit)

```
Critical APIs (backend/bff/auth): 6,000 series (60%)
├── HTTP metrics: 2,000 series
├── Health metrics: 1,000 series
├── Performance metrics: 2,000 series
└── Business metrics: 1,000 series

Secondary APIs (search/ml/rec): 2,000 series (20%)
├── Basic health: 1,000 series
└── Core functionality: 1,000 series

Infrastructure: 1,500 series (15%)
├── Node metrics: 800 series
├── Container metrics: 500 series
└── Network metrics: 200 series

Buffer/Growth: 500 series (5%)
```

***REMOVED******REMOVED******REMOVED*** Phased Approach for Free Tier

**Phase 1**: Start with Tier 1 services only
**Phase 2**: Add Tier 2 services with careful monitoring of usage
**Phase 3**: Add minimal infrastructure monitoring
**Phase 4**: Optimize and fine-tune based on actual usage patterns

***REMOVED******REMOVED******REMOVED*** Backup Strategy for Limited Retention

Since free tier only provides 14-day retention:

1. **Critical incidents**: Export relevant data before it expires
2. **Historical analysis**: Maintain 6-month rolling export for trends
3. **Compliance**: Store security-relevant logs externally
4. **Performance baselines**: Export monthly performance summaries

***REMOVED******REMOVED*** Industry Best Practices Applied

***REMOVED******REMOVED******REMOVED*** 1. Observability as Code

- **Infrastructure as Code**: Terraform for Grafana Cloud configuration
- **Dashboard as Code**: Version-controlled dashboard definitions
- **Alert as Code**: GitOps workflow for alert rule management

***REMOVED******REMOVED******REMOVED*** 2. SRE Principles

- **Error budgets**: Implement SLO-based monitoring
- **Incident response**: Integrate with Grafana IRM
- **Postmortem culture**: Enhanced incident analysis capabilities

***REMOVED******REMOVED******REMOVED*** 3. Security Best Practices

- **Zero-trust networking**: Private data source connect (PDC)
- **Least privilege access**: Granular RBAC implementation
- **Encryption everywhere**: TLS 1.3, at-rest encryption
- **Secret management**: Secure API key rotation

***REMOVED******REMOVED******REMOVED*** 4. Cost Optimization

- **Resource tagging**: Comprehensive labeling strategy
- **Usage monitoring**: Real-time cost tracking
- **Capacity planning**: Adaptive scaling based on usage
- **Waste elimination**: Automated cleanup of unused resources

***REMOVED******REMOVED******REMOVED*** 5. Migration Patterns

- **Strangler Fig**: Gradual component replacement
- **Blue-Green**: Parallel environment validation
- **Feature Flags**: Gradual feature enablement
- **Rollback readiness**: Comprehensive fallback procedures

***REMOVED******REMOVED*** Success Metrics

***REMOVED******REMOVED******REMOVED*** Technical KPIs

- **Uptime improvement**: 99.9% vs current 99.5%
- **Query performance**: 50% faster dashboard loads
- **Alert latency**: <1 minute notification delivery
- **Cost reduction**: 40%+ infrastructure cost savings

***REMOVED******REMOVED******REMOVED*** Operational KPIs

- **Mean Time to Detection (MTTD)**: <2 minutes
- **Mean Time to Resolution (MTTR)**: 25% improvement
- **Operational overhead**: 80% reduction in maintenance tasks
- **Team productivity**: 30% reduction in monitoring-related tasks

***REMOVED******REMOVED******REMOVED*** Business KPIs

- **Service reliability**: Improved SLA adherence
- **Customer satisfaction**: Faster issue resolution
- **Innovation velocity**: More time for feature development
- **Compliance**: Enhanced audit and security posture

---

***REMOVED******REMOVED*** Next Steps

1. **Immediate**: Review and approve this technical design
2. **Week 1**: Begin Phase 1 implementation
3. **Ongoing**: Weekly progress reviews and risk assessment
4. **Post-migration**: Quarterly optimization reviews

This migration represents a strategic investment in NextWatch's observability infrastructure, positioning the platform for scale, reliability, and operational excellence.
