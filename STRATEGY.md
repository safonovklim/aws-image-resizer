# DevOps Strategy

This page describes strategy that you would apply to production-ready application.
It will be focused, but not limited to Image AutoResizer Application

_**P.S.**: In this document we will refer to AWS "native" services (Lambda, Cloudwatch, etc), but you may want to choose your own third-party tools - ELK, Grafana, etc. Concepts would be same or similar in other providers._

_**P.P.S.**:I recommend to apply best practices from [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/appendix.html)._

## Observability

> Q: How would you implement comprehensive observability for this thumbnail generation service?  What metrics, logs, and traces would you collect? What tools would you use to analyze and visualize this data?

A: Primary purpose of this application - **generate thumbnails**. 

Observability must be built around it to guarantee successful delivery to the business.
That said, here is what you can monitor:

### Metrics

1. "Business" metrics 
   - 1.1. Amount of processed images
   - 1.2. Amount of rejected images 
   - 1.3. Processing Duration

This type of metrics is not available by default and not present in the application. In order to enable, your application (lambda function in our example) must publish custom metrics to Cloudwatch API using `PutMetricData` endpoint. [Learn more here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html)

2. Infrastructure metrics 
  - 2.1. Lambda function ([documentation](https://docs.aws.amazon.com/lambda/latest/operatorguide/important-metrics.html))
    - 2.1.1. Duration 
    - 2.1.2. Error Rate (Errors / Invocations Count) _must be below reasonable threshold - 1-2%_
    - 2.1.3. Concurrency Execution
    - 2.1.4. Throttles 
  - 2.2. SQS queue ([documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-available-cloudwatch-metrics.html))
    - `ApproximateAgeOfOldestMessage`
    - For Dead-Letter Queue
      - `ApproximateNumberOfMessagesVisible` must be below static number
      - `ApproximateAgeOfOldestMessage`
  - 2.3. S3 buckets ([documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/metrics-dimensions.html))
    - 2.3.1. `NumberOfObjects`
    - 2.3.2. `BucketSizeBytes`
    - 2.3.3. `PostRequests`/`PutRequests` for the Source S3 Bucket 
    - 2.3.4. `PostRequests`/`PutRequests` for the Destination S3 Bucket
    - Reason: to monitor buckets growth or unexpected DDOS attacks on upload
- 3. Costs / Budget alerts
  - You can setup daily/weekly/monthly Budget Alerts based on tags of your application or Cloudformation Stack. [Learn more here](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html) 


These are must-have observability metrics. Some metrics (1.1, 1.2, 1.3, 2.1) have higher priority (for 24/7 operator response), some of them (2.3) - lower priority for business-hours response only

### Big picture
These metrics are related to application-specific resources, but you also need to monitor "big picture" (account-/org-wide infrastructure) such as:

- Unreserved Account Concurrency
- Error Rates on your global/shared Load balancers, API Gateways
- Blocks on your WAF (firewall)
- etc

### Dashboards

To support your operations team, I'd recommend to build Cloudwatch Dashboard.
Goal of this dashboard - to present current status of the application and help to troubleshoot anomalies, attacks or application defects.

You could place metric charts in the same order as above.

|                                        |                                            |
|----------------------------------------|--------------------------------------------|
| **Business metrics**                   |                                            |
| Amount of processed images             | Amount of rejected images                  |
| Processing Duration                    |                                            |
| --------------                         | --------------                             |
| **Lambda metrics**                     |                                            |
| Duration                               | Error Rates                                |
| Concurrency                            | Throttles                                  | 
| --------------                         | --------------                             |
| **SQS metrics**                        |                                            |
| `ApproximateAgeOfOldestMessage`        |                                            |
| DLQ - `ApproximateAgeOfOldestMessage`  | DLQ - `ApproximateAgeOfOldestMessage`      | 
| --------------                         | --------------                             |
| **S3 metrics**                         |                                            |
| `NumberOfObjects`                      | `BucketSizeBytes`                          |
| Source `PostRequests` /  `PutRequests` | Destination `PostRequests` / `PutRequests` | 


See also "Monitoring"


## Security

> Q: How would you secure the S3
buckets, the Lambda function, and the data in transit? How would you protect
against common vulnerabilities?


For this particular application, you can apply following to secure buckets, functions, data:

- Ensure that S3 buckets are private and not exposed to public _(already applied)_
- Ensure that Lambda Function has minimal IAM permissions - [Grant least privilege access](https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_permissions_least_privileges.html) Principal _(already applied)_
- Ensure that Data Encrypted with KMS keys created and owned by you only _(applied with AWS-managed keys)_
- Ensure that Python version is up-to-date _(already applied)_

As an operator, you must protect application against various attack vectors:

- Public-facing interfaces 
- Bad inputs (SQL Injections, etc)
- Dependency injection (python packages in our case)
- Privilege escalation
- and many more

Shall you use application in production and add more functionality (user uploads, etc), make sure you enable following:

- WAF (Web Application Firewall) with common set rules (protection against bad inputs, sql injections, IP reputation lists, etc)
- Audit dependencies and pin to approved versions only. Do not use `latest` tag 
- Grant Least Privilege to your principals (Lambda Execution Role should have access to specific 2 buckets, specific queue and logs writing ONLY)
- Apply Rate-limit by IP and/or API Key to avoid DDOS attacks 
- Apply maximum concurrency limit on your Lambda to avoid unexpected spikes and throttles on other apps
- Apply auto-scaling to handle traffic spikes (SQS + Lambda already enable it)

## Monitoring

Observability section answers - "what?" and "why?" to monitor. This section explains "how?" to monitor. For this application, I recommend to setup following:

- **High-priority Alerts:**
 - For 24/7 on-call rotation
 - Adjust threshold if needed
 - Business - `Amount of rejected images` divided by `Total images` (rate) - OK if below 1% 
 - Lambda - Error Rates - OK if below 1%
 - Lambda - Latency - OK if below 1sec
 - Lambda - Throttles - OK if below or equal 0 (absolute)
 - Lambda - Concurrency - OK if below or equal X (X is currently set maximum concurrency on this function)
 - SQS - Dead-letter Queue - `ApproximateNumberOfMessagesVisible` - OK if below or equal 0
 
- **Low-priority Alerts:**
 - For business hours on-call rotation
 - Adjust threshold if needed
 - Business - `Amount of processed images` - OK if below X (X is approximate amount of images per minute / hour)
 - S3 - `PostRequests` /  `PutRequests` - OK if below X (X is approximate amount of requests per minute / hour)

- **Dashboards**
  - As mentioned in Observability section, setup two dashboards:
    - Application-centric
    - "Global" (for shared resources, network, WAF, etc)
  - Link these dashboards to related alerts/monitors

- **On-call Rotation**
  - In order to setup proactive response, setup Opsgenie or PagerDuty account
  - In this account, setup your team, schedule and escalations. For example - 1 operation team member per week
  - Connect Cloudwatch Alerts to Opsgenie/PagerDuty (for proactive notifications)
  - Connect Opsgenie/PagerDuty with Slack channel (for historical context)
  - Ensure team members install mobile app and allow push notifications.


As you operate your application, make sure you respond properly:
- adjust thresholds in case of false-positives
- create and link runbooks for triggered alerts (see [confluence template](https://www.atlassian.com/software/confluence/templates/devops-runbook))
- perform Root-Cause Analysis / Postmortem (in case of production incident)

## CI/CD

This repository contains two Github Workflows (pipelines):
  - `ci.yml` (continuous integration) - responsible only for integration part - static code analysis, unit tests, artifacts (build outputs) creation.
  - `cd.yml` (continuous delivery/deployment) - responsible for continuous deployment of successful artifacts to the production.


These pipelines are independent, however CD requires successful CI (it uses artifacts `cdk.out` from CI). 
CD can be kicked off any time, but for simplicity of this demo - it runs after every successful CI run.

## Scalability and Cost Optimization

> Q: How would you handle increased traffic and load? What cost optimization strategies would you implement?

Here is what can help application to support unexpected traffic spikes:

- Queueing - SQS queue allows you to queue and invoke files in sequence (rather than placing all of them against lambda, causing throttles spikes)
- Batching (default to 10) - SQS-to-Lambda integration allows you to process multiple messages at the same time. If message is failing, it will be retried few times (default - 3) or rejected to Dead-Letter Queue 
- Concurrency Limit (default - unlimited) - set concurrency limit to control maximum amount of parallel lambda invocations, preventing costs/usage spikes

After application running in production for a while and you'd like to reduce costs, you can do following:

- **Performance optimizations** (check if application can be simplified/decoupled) to save extra bucks on used memory/latency - Lambda billed per duration and used memory.
- **Switch to ARM64 / Graviton** - savings up to 33% on compute
- **Compute Savings plan** - purchase 1-year/3-year commitments. [Learn more here](https://aws.amazon.com/savingsplans/compute-pricing/)
- **Private Pricing Agreements** (for enterprises) - custom agreement with AWS for long-term commitments in exchange of discounts (up to 30%)
- Other (not recommended) - **Group Buying** - companies like [Pump.co](https://pump.co/) allow you to save a bit by joining existing workload account with shared paying/billing account
