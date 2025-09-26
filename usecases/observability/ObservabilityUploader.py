import json
import boto3
import os
from datetime import datetime

class ObservabilityUploader:
    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or os.environ.get('SERVICE_SCREENER_S3_BUCKET')
        self.s3_client = None
        
        if self.bucket_name:
            try:
                self.s3_client = boto3.client('s3')
            except Exception as e:
                print(f"Failed to initialize S3 client: {e}")
    
    def upload_report(self, contexts, summary_data):
        """Upload Service Screener report to S3 for observability"""
        if not self.bucket_name or not self.s3_client:
            print("S3 bucket not configured, skipping observability upload")
            return False
        
        try:
            # Get account info from STS
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            timestamp = datetime.utcnow()
            
            # Create comprehensive report structure
            report = {
                'metadata': {
                    'account_id': account_id,
                    'timestamp': timestamp.isoformat(),
                    'services': list(contexts.keys())
                },
                'summary': summary_data,
                'services': contexts
            }
            
            # Generate S3 key with timestamp and account
            s3_key = f"reports/{account_id}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}-report.json"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(report, default=str),
                ContentType='application/json'
            )
            
            print(f"Report uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            print(f"Failed to upload report to S3: {e}")
            return False