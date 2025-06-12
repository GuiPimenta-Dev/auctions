import boto3
import json

def get_proxy_config():
    """Get Oxylabs proxy configuration from AWS Secrets Manager"""
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId="Oxylabs")
    secret = json.loads(response["SecretString"])
    
    return {
        "username": secret["username"],
        "password": secret["password"],
        "endpoint": "pr.oxylabs.io:7777"
    }

def get_proxy_url():
    """Get formatted proxy URL for Oxylabs"""
    config = get_proxy_config()
    return f"http://{config['username']}:{config['password']}@{config['endpoint']}" 