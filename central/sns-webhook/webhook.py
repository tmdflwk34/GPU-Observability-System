#!/usr/bin/env python3
import json
import time
import boto3
import requests
from flask import Flask, request

app = Flask(__name__)

ses_client = boto3.client(
    'ses',
    region_name='us-east-1',
    aws_access_key_id='REMOVED_EXPOSED_CREDENTIAL',
    aws_secret_access_key='REMOVED_EXPOSED_CREDENTIAL'
)

FROM_EMAIL = 'noreply@example.com'
ADMIN_EMAIL = 'admin@example.com'

# 사용자명 → 이메일 매핑
USER_EMAIL_MAP = {
    'admin': 'admin@example.com',
    'user20': 'user01@example.com',
    'user05': 'user02@example.com',
    'user12': 'user03@example.com',
    'user13': 'user04@example.com',
    'user22': 'user05@example.com',
    'user11': 'user06@example.com',
    'user08': 'user07@example.com',
    'user19': 'user08@example.com',
    'user17': 'user09@example.com',
    'user21': 'user10@example.com',
    'user15': 'user11@example.com',
    'user01': 'user12@example.com',
    'user09': 'user13@example.com',
    'user07': 'user14@example.com',
    'user14': 'user15@example.com',
    'user02': 'user16@example.com',
    'user18': 'user17@example.com',
    'user16': 'user18@example.com',
    'user04': 'user19@example.com'
}

DASHBOARD_URL = 'http://example-grafana-alb-0000000000.us-west-2.elb.amazonaws.com/d/adv2ww5'
PROMETHEUS_URL = 'http://prometheus:9090'

def get_top_cpu_user(instance):
    """Get the user with highest CPU usage on the instance"""
    query = f'topk(1, sum by (username) (rate(namedprocess_namegroup_cpu_seconds_total{{instance="{instance}"}}[5m])))'
    for attempt in range(2):
        try:
            response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': query}, timeout=5)
            data = response.json()
            if data['status'] == 'success' and data['data']['result']:
                return data['data']['result'][0]['metric'].get('username', '사용자')
        except:
            pass
        if attempt == 0:
            time.sleep(5)
    return '사용자'

def get_top_memory_user(instance):
    """Get the user with highest memory usage on the instance"""
    query = f'topk(1, sum by (username) (namedprocess_namegroup_memory_bytes{{instance="{instance}"}}))'
    for attempt in range(2):
        try:
            response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': query}, timeout=5)
            data = response.json()
            if data['status'] == 'success' and data['data']['result']:
                return data['data']['result'][0]['metric'].get('username', '사용자')
        except:
            pass
        if attempt == 0:
            time.sleep(5)
    return '사용자'

# 사용자 알림 중복 발송 방지 (1시간 쿨다운)
user_alert_cooldown = {}
COOLDOWN_SECONDS = 3600

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    alerts = data.get('alerts', [])
    
    if not alerts:
        return {'status': 'no alerts'}, 200
    
    first_alert = alerts[0]
    labels = first_alert.get('labels', {})
    annotations = first_alert.get('annotations', {})
    
    alertname = labels.get('alertname', 'Unknown')
    instance = labels.get('instance', 'Unknown')
    summary = annotations.get('summary', 'N/A')
    description = annotations.get('description', 'N/A')
    status = first_alert.get('status', 'Unknown')
    admin_only = labels.get('admin_only') == 'true'
    
    # Get user based on alert type
    if alertname == 'HighCPUUsage':
        user = labels.get('username') or labels.get('user') or get_top_cpu_user(instance)
    elif alertname == 'HighMemoryUsage':
        user = get_top_memory_user(instance)
    else:
        user = '사용자'
    
    # Determine recipients
    if admin_only or alertname not in ['HighCPUUsage', 'HighMemoryUsage']:
        to_emails = [ADMIN_EMAIL]
    else:
        user_email = USER_EMAIL_MAP.get(user)
        if user_email:
            # 사용자 중복 발송 방지
            cooldown_key = f"{user}:{alertname}:{instance}"
            now = time.time()
            last_sent = user_alert_cooldown.get(cooldown_key, 0)
            if now - last_sent < COOLDOWN_SECONDS:
                return {'status': 'cooldown', 'user': user}, 200
            to_emails = [user_email]
        else:
            to_emails = [ADMIN_EMAIL]
    
    message_lines = []
    
    if alertname == 'HighCPUUsage':
        message_lines.append("CPU 과부하 주의 알림")
        message_lines.append("")
        message_lines.append(f"{user} 님의 작업으로 인해 CPU 사용률이 90% 이상 과부하 중입니다.")
        message_lines.append(f"{instance} 서버에서 작업 중인 사항을 확인하고 주의해주세요.")
        message_lines.append("조치가 없을 경우 서버가 다운되거나 다른 사용자의 작업에 영향을 줄 수 있습니다.")
        message_lines.append("")
        message_lines.append("주의 알림:")
        message_lines.append(f"- 사용률: {description}")
        message_lines.append(f"- 사용자: {user}")
        message_lines.append(f"- 서버: {instance}")
    elif alertname == 'HighMemoryUsage':
        message_lines.append("메모리 과부하 주의 알림")
        message_lines.append("")
        message_lines.append(f"{user} 님의 작업으로 인해 메모리 사용률이 90% 이상 과부하 중입니다.")
        message_lines.append(f"{instance} 서버에서 작업 중인 사항을 확인하고 주의해주세요.")
        message_lines.append("조치가 없을 경우 서버가 다운되거나 다른 사용자의 작업에 영향을 줄 수 있습니다.")
        message_lines.append("")
        message_lines.append("주의 알림:")
        message_lines.append(f"- 사용률: {description}")
        message_lines.append(f"- 사용자: {user}")
        message_lines.append(f"- 서버: {instance}")
    elif alertname == 'DiskSpaceLow':
        message_lines.append("디스크 공간 부족 알림")
        message_lines.append("")
        message_lines.append(f"{instance} 서버의 디스크 공간이 부족합니다.")
        message_lines.append("조치가 없을 경우 서버 운영에 심각한 장애가 발생할 수 있습니다.")
        message_lines.append("")
        message_lines.append("상세 정보:")
        message_lines.append(f"- 서버: {instance}")
        message_lines.append(f"- 설명: {description}")
    else:
        message_lines.append(f"{alertname}")
        message_lines.append("")
        message_lines.append(f"서버: {instance}")
        message_lines.append(f"요약: {summary}")
        message_lines.append(f"설명: {description}")
        message_lines.append(f"상태: {status}")
    
    message_lines.append("")
    message_lines.append(f"모니터링 대시보드: {DASHBOARD_URL}")
    
    message = "\n".join(message_lines)
    subject = f"[Acme Alert] {alertname} - {instance}"
    
    try:
        response = ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': to_emails},
            Message={
                'Subject': {'Data': subject[:100]},
                'Body': {'Text': {'Data': message}}
            }
        )
        # 사용자 발송 시 쿨다운 기록
        if to_emails != [ADMIN_EMAIL]:
            cooldown_key = f"{user}:{alertname}:{instance}"
            user_alert_cooldown[cooldown_key] = time.time()
        return {'status': 'success', 'messageId': response['MessageId']}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
