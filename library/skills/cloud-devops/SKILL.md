---
name: cloud-devops
description: Cloud platforms (AWS, GCP, Azure), Infrastructure as Code (Terraform, Pulumi), and DevOps engineering practices
---

# Cloud and DevOps

## AWS Core Services
- Compute: EC2 (instances), Lambda (serverless), ECS/EKS (containers), Fargate
- Storage: S3 (object), EBS (block), EFS (file), Glacier (archive)
- Database: RDS (relational), DynamoDB (NoSQL), ElastiCache (Redis/Memcached), Aurora
- Networking: VPC, subnets, security groups, NACLs, Route 53 (DNS), CloudFront (CDN)
- Messaging: SQS (queue), SNS (pub/sub), EventBridge (event bus), Kinesis (streaming)
- Auth: IAM (roles, policies, users), Cognito (user pools)
- API Gateway: REST and HTTP APIs, Lambda integration
- Observability: CloudWatch (logs, metrics, alarms), X-Ray (tracing)

## GCP Core Services
- Compute: Compute Engine, Cloud Run (containers), Cloud Functions, GKE
- Storage: Cloud Storage, Persistent Disk, Filestore
- Database: Cloud SQL, Firestore, Bigtable, Spanner, AlloyDB
- Networking: VPC, Cloud Load Balancing, Cloud CDN, Cloud DNS
- Messaging: Pub/Sub, Cloud Tasks, Eventarc
- Auth: IAM, Identity Platform, Firebase Auth
- BigQuery: serverless data warehouse, SQL analytics at scale

## Azure Core Services
- Compute: Virtual Machines, App Service, Functions, AKS, Container Apps
- Storage: Blob Storage, Disk Storage, Files, Table Storage
- Database: SQL Database, Cosmos DB, Cache for Redis
- Networking: VNet, Application Gateway, Front Door, DNS Zone
- Messaging: Service Bus, Event Grid, Event Hubs
- Auth: Entra ID (Azure AD), Managed Identity
- DevOps: Azure DevOps, Pipelines, Boards, Repos

## Terraform
- HCL syntax: resource, data, variable, output, locals
- Providers: aws, google, azurerm — version constraints
- State: terraform.tfstate, remote backends (S3, GCS, Azure Blob)
- Commands: init, plan, apply, destroy, import, state
- Modules: reusable components, inputs/outputs, registry modules
- Workspaces: environment isolation (dev, staging, prod)
- Lifecycle: create_before_destroy, prevent_destroy, ignore_changes
- Data sources: query existing infrastructure
- Provisioners: avoid when possible, prefer cloud-init/user-data

## Pulumi
- Infrastructure as real code (TypeScript, Python, Go, C#)
- Resources, stacks, configuration, secrets
- Component resources for reusable abstractions
- State management: Pulumi Cloud, self-managed backends

## Kubernetes
- Core objects: Pod, Deployment, Service, ConfigMap, Secret, Ingress
- Workloads: Deployment (stateless), StatefulSet (stateful), DaemonSet, Job, CronJob
- Networking: ClusterIP, NodePort, LoadBalancer, Ingress controllers
- Storage: PV, PVC, StorageClass
- Configuration: ConfigMap, Secret, environment variables
- Health checks: livenessProbe, readinessProbe, startupProbe
- Resource management: requests, limits, HPA (auto-scaling)
- Helm: charts, values.yaml, templates, releases
- kubectl: get, describe, logs, exec, apply, delete

## Monitoring and Observability
- Three pillars: metrics, logs, traces
- Prometheus + Grafana: metrics collection and dashboarding
- ELK/EFK stack: Elasticsearch, Logstash/Fluentd, Kibana
- Distributed tracing: Jaeger, Zipkin, OpenTelemetry
- SLOs, SLIs, SLAs: define and measure reliability
- Alerting: PagerDuty, OpsGenie, alert routing and escalation

## Best Practices
- Infrastructure as Code for everything — no manual console changes
- Least privilege: minimal IAM permissions per service/role
- Encrypt at rest and in transit
- Use managed services over self-hosted when possible
- Tag all resources for cost allocation and management
- Multi-AZ/region for high availability
- Automate deployments: GitOps, CI/CD pipelines
- Cost optimization: reserved instancesright-sizing, spot instances
