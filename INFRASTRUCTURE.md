# ALB 및 네트워크 설정

## Application Load Balancer
- **이름**: acme-grafana-alb
- **DNS**: example-grafana-alb-0000000000.us-west-2.elb.amazonaws.com
- **리전**: us-west-2

## Target Group
- **이름**: acme-grafana-tg
- **ARN**: arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/acme-grafana-tg/0000000000000000
- **프로토콜**: HTTP:80
- **Health Check**: /api/health (200-399)

## 타겟
- Instance: i-0aaaaaaaaaaaaaa09 (monitoring)
- Port: 80
# 모니터링 대상 인스턴스

## GPU 인스턴스

### p4de (p4de.24xlarge)
- IP: 10.0.1.12
- GPU: 8x A100 80GB
- Exporters: 9100 (node), 9400 (dcgm), 9256 (process), 9500 (gpu-custom)

### p4d (p4d.24xlarge)
- IP: 10.0.1.11
- GPU: 8x A100 40GB
- Exporters: 9100, 9400, 9256, 9500

### g5 (g5.12xlarge)
- IP: 10.0.1.13
- GPU: 4x A10G
- Exporters: 9100, 9400, 9256, 9500

### head (g4dn.xlarge)
- IP: 10.0.1.15
- GPU: 1x T4
- Exporters: 9100, 9400, 9256

### p5 (p5.48xlarge)
- IP: 10.0.2.11
- GPU: 8x H100
- Exporters: 9100, 9400, 9256, 9500

## CPU 인스턴스

### r7 (r7i.4xlarge)
- IP: 10.0.1.14
- Exporters: 9100 (node), 9256 (process)

## 중앙 모니터링

### monitoring
- Instance: i-0aaaaaaaaaaaaaa09
- Services: Prometheus (9090), Grafana (80), Alertmanager (9093), FSx Exporter (9101)
