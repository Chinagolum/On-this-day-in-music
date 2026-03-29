import json
import urllib.request
import os

def lambda_handler(event, context):
    """Forward SNS messages to Telegram"""
    
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    
    # Parse SNS message
    message = event['Records'][0]['Sns']['Message']
    subject = event['Records'][0]['Sns'].get('Subject', 'Alert')
    
    # Format for Telegram
    telegram_text = f"🚨 *{subject}*\n\n{message}"
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": telegram_text,
        "parse_mode": "Markdown"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        return {
            'statusCode': 200,
            'body': json.dumps('Sent to Telegram')
        }
