import os
import logging
import boto3
import datetime
import urllib

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数
LINE_NOTIFY_URL = os.environ.get('LINE_NOTIFY_URL')
LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')

response = boto3.client('cloudwatch', region_name='us-east-1')

# 請求情報取得
get_metric_statistics = response.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        }
    ],
    StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
    EndTime=datetime.datetime.today(),
    Period=86400,
    Statistics=['Maximum'])

cost = get_metric_statistics['Datapoints'][0]['Maximum']
date = get_metric_statistics['Datapoints'][0]['Timestamp'].strftime("%Y年%m月%d日")

def lambda_handler(event, context):
    message = f"\n{date}までのAWSの料金は、${cost}です。"
    return notify_to_line(message)

def notify_to_line(message):
    method = "POST"
    headers = {"Authorization" : "Bearer " + LINE_ACCESS_TOKEN}
    payload = {"message" : message}
    
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
        return message
    except Exception as e:
        logger.error("Request failed: %s", e)
