"""
Health Check Endpoint
"""

import json


def handler(request):
    """Simple health check"""
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"}),
    }
