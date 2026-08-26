from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError, UnknownServiceError

from app.collectors.base import BaseCollector
from app.collectors.support import is_unsupported_api
from app.models.resource import Resource


@dataclass(frozen=True)
class ListSpec:
    name: str
    label: str
    boto: str
    operation: str
    key: str
    resource_type: str
    id_field: str = ""
    name_field: str = ""
    arn_field: str = ""
    kwargs: dict[str, Any] = field(default_factory=dict)


class GenericListCollector(BaseCollector):
    spec: ListSpec

    def collect_sync(self) -> list[Resource]:
        try:
            client = self.client(self.spec.boto)
            items = self.paginate(
                client, self.spec.operation, self.spec.key, **self.spec.kwargs
            )
        except UnknownServiceError:
            self.supported = False
            return []
        except ClientError as exc:
            if is_unsupported_api(exc):
                self.supported = False
                return []
            raise
        except (BotoCoreError, AttributeError):
            self.supported = False
            return []
        region = getattr(getattr(client, "meta", None), "region_name", None)
        resources: list[Resource] = []
        for item in items:
            resources.append(self._to_resource(item, region))
        return resources

    def _to_resource(self, item: Any, region: str | None) -> Resource:
        if isinstance(item, str):
            ident = item
            payload: dict[str, Any] = {"name": item}
        else:
            payload = dict(item)
            ident = str(
                payload.get(self.spec.id_field)
                or payload.get(self.spec.name_field)
                or payload.get("Name")
                or payload.get("name")
                or payload.get("Id")
                or payload.get("id")
                or payload.get("Arn")
                or payload.get("ARN")
                or ""
            )
        name = ident
        if isinstance(item, dict) and self.spec.name_field:
            name = str(item.get(self.spec.name_field) or ident)
        arn = None
        if isinstance(item, dict) and self.spec.arn_field:
            arn = item.get(self.spec.arn_field)
        return Resource(
            id=f"{self.spec.name}:{ident or name}",
            service=self.spec.name,
            resource_type=self.spec.resource_type,
            name=name or ident,
            arn=arn if isinstance(arn, str) else None,
            region=region,
            status=(item.get("Status") or item.get("State") or item.get("status") if isinstance(item, dict) else "available"),
            metadata={},
            raw=payload if isinstance(payload, dict) else {"value": item},
        )


def collector_class(spec: ListSpec) -> type[BaseCollector]:
    class Built(GenericListCollector):
        service_name = spec.name

        def __init__(self, floci_client) -> None:
            super().__init__(floci_client)
            self.spec = spec

    Built.__name__ = f"{spec.name.replace('-', '_').title()}Collector"
    Built.__qualname__ = Built.__name__
    return Built


# Inventory list APIs for Floci matrix services that do not already have a
# specialized collector. Names match the Floci services overview.
GENERIC_SPECS: tuple[ListSpec, ...] = (
    ListSpec("ssm", "SSM", "ssm", "describe_parameters", "Parameters", "parameter", "Name", "Name"),
    ListSpec("s3tables", "S3 Tables", "s3tables", "list_table_buckets", "tableBuckets", "table_bucket", "name", "name", "arn"),
    ListSpec("s3vectors", "S3 Vectors", "s3vectors", "list_indexes", "indexes", "index", "indexName", "indexName"),
    ListSpec("dynamodbstreams", "DynamoDB Streams", "dynamodbstreams", "list_streams", "Streams", "stream", "StreamArn", "TableName", "StreamArn"),
    ListSpec("apigatewayv2", "API Gateway v2", "apigatewayv2", "get_apis", "Items", "http_api", "ApiId", "Name", "ApiEndpoint"),
    ListSpec("organizations", "Organizations", "organizations", "list_roots", "Roots", "root", "Id", "Name", "Arn"),
    ListSpec("cognito-idp", "Cognito", "cognito-idp", "list_user_pools", "UserPools", "user_pool", "Id", "Name", kwargs={"MaxResults": 60}),
    ListSpec("cloudhsmv2", "CloudHSM v2", "cloudhsmv2", "describe_clusters", "Clusters", "cluster", "ClusterId", "ClusterId"),
    ListSpec("kinesis", "Kinesis", "kinesis", "list_streams", "StreamNames", "stream"),
    ListSpec("kinesisanalyticsv2", "Managed Apache Flink", "kinesisanalyticsv2", "list_applications", "ApplicationSummaries", "application", "ApplicationName", "ApplicationName", "ApplicationARN"),
    ListSpec("swf", "SWF", "swf", "list_domains", "domainInfos", "domain", "name", "name", kwargs={"registrationStatus": "REGISTERED"}),
    ListSpec("scheduler", "EventBridge Scheduler", "scheduler", "list_schedules", "Schedules", "schedule", "Name", "Name", "Arn"),
    ListSpec("pipes", "EventBridge Pipes", "pipes", "list_pipes", "Pipes", "pipe", "Name", "Name", "Arn"),
    ListSpec("cloudwatch", "CloudWatch Metrics", "cloudwatch", "list_dashboards", "DashboardEntries", "dashboard", "DashboardName", "DashboardName", "DashboardArn"),
    ListSpec("rum", "CloudWatch RUM", "rum", "list_app_monitors", "AppMonitorSummaries", "app_monitor", "Name", "Name"),
    ListSpec("guardduty", "GuardDuty", "guardduty", "list_detectors", "DetectorIds", "detector"),
    ListSpec("elasticache", "ElastiCache", "elasticache", "describe_cache_clusters", "CacheClusters", "cluster", "CacheClusterId", "CacheClusterId"),
    ListSpec("memorydb", "MemoryDB", "memorydb", "describe_clusters", "Clusters", "cluster", "Name", "Name", "ARN"),
    ListSpec("rds", "RDS", "rds", "describe_db_instances", "DBInstances", "db_instance", "DBInstanceIdentifier", "DBInstanceIdentifier", "DBInstanceArn"),
    ListSpec("kafka", "MSK", "kafka", "list_clusters_v2", "ClusterInfoList", "cluster", "ClusterName", "ClusterName", "ClusterArn"),
    ListSpec("mq", "Amazon MQ", "mq", "list_brokers", "BrokerSummaries", "broker", "BrokerId", "BrokerName", "BrokerArn"),
    ListSpec("mwaa", "MWAA", "mwaa", "list_environments", "Environments", "environment"),
    ListSpec("athena", "Athena", "athena", "list_work_groups", "WorkGroups", "workgroup", "Name", "Name"),
    ListSpec("glue", "Glue", "glue", "get_databases", "DatabaseList", "database", "Name", "Name"),
    ListSpec("neptune", "Neptune", "neptune", "describe_db_clusters", "DBClusters", "cluster", "DBClusterIdentifier", "DBClusterIdentifier", "DBClusterArn"),
    ListSpec("docdb", "DocumentDB", "docdb", "describe_db_clusters", "DBClusters", "cluster", "DBClusterIdentifier", "DBClusterIdentifier", "DBClusterArn"),
    ListSpec("emr", "EMR", "emr", "list_clusters", "Clusters", "cluster", "Id", "Name"),
    ListSpec("emr-serverless", "EMR Serverless", "emr-serverless", "list_applications", "applications", "application", "id", "name", "arn"),
    ListSpec("firehose", "Data Firehose", "firehose", "list_delivery_streams", "DeliveryStreamNames", "delivery_stream"),
    ListSpec("efs", "EFS", "efs", "describe_file_systems", "FileSystems", "file_system", "FileSystemId", "Name", "FileSystemArn"),
    ListSpec("lightsail", "Lightsail", "lightsail", "get_instances", "instances", "instance", "name", "name", "arn"),
    ListSpec("acm", "ACM", "acm", "list_certificates", "CertificateSummaryList", "certificate", "CertificateArn", "DomainName", "CertificateArn"),
    ListSpec("resource-explorer-2", "Resource Explorer", "resource-explorer-2", "list_indexes", "Indexes", "index", "Arn", "Region", "Arn"),
    ListSpec("ses", "SES", "ses", "list_identities", "Identities", "identity"),
    ListSpec("sesv2", "SES v2", "sesv2", "list_email_identities", "EmailIdentities", "email_identity", "IdentityName", "IdentityName"),
    ListSpec("opensearch", "OpenSearch", "opensearch", "list_domain_names", "DomainNames", "domain", "DomainName", "DomainName"),
    ListSpec("appconfig", "AppConfig", "appconfig", "list_applications", "Items", "application", "Id", "Name"),
    ListSpec("appsync", "AppSync", "appsync", "list_graphql_apis", "graphqlApis", "graphql_api", "apiId", "name", "arn"),
    ListSpec("eks", "EKS", "eks", "list_clusters", "clusters", "cluster"),
    ListSpec("wafv2", "WAF v2", "wafv2", "list_web_acls", "WebACLs", "web_acl", "Name", "Name", "ARN", kwargs={"Scope": "REGIONAL"}),
    ListSpec("autoscaling", "Auto Scaling", "autoscaling", "describe_auto_scaling_groups", "AutoScalingGroups", "asg", "AutoScalingGroupName", "AutoScalingGroupName", "AutoScalingGroupARN"),
    ListSpec("application-autoscaling", "Application Auto Scaling", "application-autoscaling", "describe_scalable_targets", "ScalableTargets", "scalable_target", "ResourceId", "ResourceId", kwargs={"ServiceNamespace": "ecs"}),
    ListSpec("elasticbeanstalk", "Elastic Beanstalk", "elasticbeanstalk", "describe_environments", "Environments", "environment", "EnvironmentId", "EnvironmentName"),
    ListSpec("codebuild", "CodeBuild", "codebuild", "list_projects", "projects", "project"),
    ListSpec("batch", "AWS Batch", "batch", "describe_job_queues", "jobQueues", "job_queue", "jobQueueName", "jobQueueName", "jobQueueArn"),
    ListSpec("codedeploy", "CodeDeploy", "codedeploy", "list_applications", "applications", "application"),
    ListSpec("codepipeline", "CodePipeline", "codepipeline", "list_pipelines", "pipelines", "pipeline", "name", "name"),
    ListSpec("backup", "AWS Backup", "backup", "list_backup_vaults", "BackupVaultList", "vault", "BackupVaultName", "BackupVaultName", "BackupVaultArn"),
    ListSpec("fis", "AWS FIS", "fis", "list_experiments", "experiments", "experiment", "id", "id"),
    ListSpec("cloudfront", "CloudFront", "cloudfront", "list_distributions", "DistributionList.Items", "distribution", "Id", "Id", "ARN"),
    ListSpec("servicediscovery", "Cloud Map", "servicediscovery", "list_namespaces", "Namespaces", "namespace", "Id", "Name", "Arn"),
    ListSpec("config", "AWS Config", "config", "describe_configuration_recorders", "ConfigurationRecorders", "recorder", "name", "name"),
    ListSpec("cloudtrail", "CloudTrail", "cloudtrail", "describe_trails", "trailList", "trail", "Name", "Name", "TrailARN"),
    ListSpec("transcribe", "Transcribe", "transcribe", "list_transcription_jobs", "TranscriptionJobSummaries", "transcription_job", "TranscriptionJobName", "TranscriptionJobName"),
    ListSpec("cur", "Cost and Usage Reports", "cur", "describe_report_definitions", "ReportDefinitions", "report", "ReportName", "ReportName"),
    ListSpec("bcm-data-exports", "BCM Data Exports", "bcm-data-exports", "list_exports", "Exports", "export", "ExportArn", "ExportName", "ExportArn"),
    ListSpec("transfer", "Transfer Family", "transfer", "list_servers", "Servers", "server", "ServerId", "ServerId", "Arn"),
    ListSpec("iot", "IoT Core", "iot", "list_things", "things", "thing", "thingName", "thingName"),
)


class PresenceCollector(BaseCollector):
    """Floci exposes the API, but there is no inventory list operation."""

    def collect_sync(self) -> list[Resource]:
        return []


def presence_class(name: str) -> type[BaseCollector]:
    class Built(PresenceCollector):
        service_name = name

    Built.__name__ = f"{name.replace('-', '_').title()}PresenceCollector"
    return Built


PROTOCOL_ONLY: tuple[str, ...] = (
    "signin",
    "lambda-microvms",
    "cloudcontrol",
    "rds-data",
    "appconfigdata",
    "bedrock-runtime",
    "bedrock-agentcore-control",
    "bedrock-agentcore",
    "resourcegroupstaggingapi",
    "textract",
    "pricing",
    "ce",
    "iot-data",
)


def build_generic_collectors() -> dict[str, type[BaseCollector]]:
    collectors = {spec.name: collector_class(spec) for spec in GENERIC_SPECS}
    collectors.update({name: presence_class(name) for name in PROTOCOL_ONLY})
    return collectors
