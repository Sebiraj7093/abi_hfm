# {service}-hf-api

## DevOps Roadmap
- [x] Monitoring - Prometheus
- [x] Debug
- [x] Tracing - Jaeger
- [x] Logs - Graylog
- [x] Orchestrator Split - Kubernetes/Swarm
- [x] Yamls Usage
- [x] Health Check Handlers
- [x] Secrets Management - Vault

## Service Dependencies (Auto-Generated from Jaeger)
### First Level Services Dependencies DAG
![First Level Services Dependencies DAG](https://minio-api.hfmarkets.com/jaeger/dependencies/{service}-hf-api/first_level_dag.png)

### Data Stores Dependencies DAG
![Data Stores Dependencies DAG](https://minio-api.hfmarkets.com/jaeger/dependencies/{service}-hf-api/data_stores_dag.png)

### Deep Dependency Graph
![Deep Dependency Graph](https://minio-api.hfmarkets.com/jaeger/dependencies/{service}-hf-api/ddg.png)

## Introduction
Short summary of the service
* What is the purpose of this application and how critical it is.  
* What other critical components it interacts with.


## Technologies Used

* Python 3.13
* Fastapi v0.115.7

## Components
* [HF YAML Loader](https://gitlab.hfmarkets.com/libraries/hf-yaml-loader)
* [HF Mysql Client](https://gitlab.hfmarkets.com/libraries/mysql_client)
* [HF Mongo Client](https://gitlab.hfmarkets.com/libraries/hf-mongo-client)
* [HF Redis Client](https://gitlab.hfmarkets.com/libraries/hf-redis-client)
* [HF HTTP Client](https://gitlab.hfmarkets.com/libraries/hf-http-client)
* [HF Health](https://gitlab.hfmarkets.com/libraries/hf-health)
* [HF Logger](https://gitlab.hfmarkets.com/libraries/hf-logger)


## Service environments

| Environment     | Link                                          |
------------------|-----------------------------------------------|
| dev1            | https://{service}-hf-api-kdev1.hfmarkets.com  |
| dev2            | https://{service}-hf-api-kdev2.hfmarkets.com  |
| dev3            | https://{service}-hf-api-kdev3.hfmarkets.com  |
| dev4            | https://{service}-hf-api-kdev4.hfmarkets.com  |
| dev5            | https://{service}-hf-api-kdev5.hfmarkets.com  |
| dev6            | https://{service}-hf-api-kdev6.hfmarkets.com  |
| dev7            | https://{service}-hf-api-kdev7.hfmarkets.com  |
| qa1             | https://{service}-hf-api-kqa1.hfmarkets.com   |
| Staging         | https://{service}-hf-api-staging.hfmarkets.com |
| Live            | https://{service}-hf-api.hfmarkets.com        |

## Monitoring

* [Graylog Live](https://graylog.hfmarkets.com/search?q=gl2_source_input%3A60e6b056754647000a414cb1+AND+kubernetes_container_name%3A+%{service}-hf-api%22+AND+kubernetes_namespace_name%3A+%22live%22&rangetype=relative&relative=300)
* [Graylog Staging](https://graylog.hfmarkets.com/search?q=gl2_source_input%3A60e6b056754647000a414cb1+AND+kubernetes_container_name%3A+%{service}-hf-api%22+AND+kubernetes_namespace_name%3A+%22staging%22&rangetype=relative&relative=300)
* [Grafana](https://grafana.hfmarkets.com/d/cf2tyTank/kubernetes-services-performance?orgId=1&refresh=1m&var-cluster=All&var-namespace=live&var-service_name={service}-hf-api&var-Filters=path%7C!%3D%7C%2Fmetrics&var-Filters=handler%7C!%3D%7CMetricsHandler)


* Jaeger
    
    | Environment | Link                                                                                    |
    |-------------|-----------------------------------------------------------------------------------------|
    | dev1        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev1 |
    | dev2        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev2 |
    | dev3        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev3 |
    | dev4        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev4 |
    | dev5        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev5 |
    | dev6        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev6 |
    | dev7        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev7 |
    | dev8        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev8 |
    | dev9        | https://jaeger-dev.hfmarkets.com/search?service={service}%20dev9 |
    | qa1         | https://jaeger-dev.hfmarkets.com/search?service={service}%20qa1  |
    | staging     | https://jaeger.hfmarkets.com/search?service={service}%20staging  |
    | live        | https://jaeger.hfmarkets.com/search?service={service}%20live     |
    

  ## Deployment

* [Jenkins Dev](https://jenkins2.hfmarkets.com/blue/organizations/jenkins/{service}-hf-api/branches/)
* [Jenkins Staging](https://jenkins2.hfmarkets.com/blue/organizations/jenkins/{service}-hf-api-staging/activity)
* [Jenkins Live](https://jenkins2.hfmarkets.com/view/kubernetes/view/kube-main-live/job/{service}-hf-api-production/)

## Code Quality

* Sonarqube

    | Environment | Link                                                                  |
    |:-----------:|:----------------------------------------------------------------------|
    |    dev1     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev     |
    |    dev2     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev2    |
    |    dev3     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev3    |
    |    dev4     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev4    |
    |    dev5     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev5    |
    |    dev6     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev6    |
    |    dev7     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_dev7    |
    |     qa1     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_qa1     |
    |   staging   | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api_staging |
    |    live     | https://sonarqube.hfmarkets.com/dashboard?id={service}-hf-api         |

* [Bandit](https://sonarqube.hfmarkets.com/dashboard?id=hf_bandit_{service}-hf-api) (Security issues)


## Testing
        
* Run all tests
    ```commandline
    kube -p {service}-hf-api --test
    ```

* Run specific test/tests
    ```commandline
    kube -p {service}-hf-api --test -c <test_path>
    ```

## Further Reading

1. https://fastapi.tiangolo.com/
2. https://www.jenkins.io/
3. https://www.sonarqube.org/
4. https://www.graylog.org/
5. https://www.jaegertracing.io/
6. https://kubernetes.io/
7. https://wiki.hfmarkets.net/kube-test
8. https://wiki.hfmarkets.net/kube
