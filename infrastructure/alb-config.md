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
