import json
import boto3
import os
from datetime import datetime
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Process Service Screener reports uploaded to S3 and convert to structured metrics
    """
    s3_client = boto3.client('s3')
    metrics_bucket = os.environ['METRICS_BUCKET']
    
    try:
        # Process each S3 event
        for record in event['Records']:
            # Get bucket and object key from the event
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            print(f"Processing report: s3://{bucket}/{key}")
            
            # Download and parse the report
            response = s3_client.get_object(Bucket=bucket, Key=key)
            report_data = json.loads(response['Body'].read())
            
            # Extract metrics from the report
            metrics = extract_metrics(report_data)
            
            # Generate output key for processed metrics
            timestamp = datetime.utcnow()
            output_key = f"metrics/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}-metrics.json"
            
            # Upload processed metrics
            s3_client.put_object(
                Bucket=metrics_bucket,
                Key=output_key,
                Body=json.dumps(metrics, indent=2, default=str),
                ContentType='application/json'
            )
            
            print(f"Metrics uploaded: s3://{metrics_bucket}/{output_key}")
            
            # Create/update manifest file for QuickSight
            update_manifest(s3_client, metrics_bucket)
            
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed Service Screener reports')
        }
        
    except Exception as e:
        print(f"Error processing report: {str(e)}")
        raise e

def extract_metrics(report_data):
    """Extract structured metrics from Service Screener report"""
    
    metadata = report_data.get('metadata', {})
    summary = report_data.get('summary', {})
    services = report_data.get('services', {})
    
    # Base metrics
    metrics = {
        'scan_timestamp': metadata.get('timestamp', datetime.utcnow().isoformat()),
        'account_id': metadata.get('account_id', 'unknown'),
        'services_scanned': metadata.get('services', []),
        'total_resources': summary.get('resources', 0),
        'total_rules': summary.get('rules', 0),
        'total_findings': summary.get('findings', 0),
        'scan_duration': summary.get('timespent', 0)
    }
    
    # Service-level metrics
    service_metrics = []
    findings_by_criticality = {'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
    findings_by_category = {}
    
    for service_name, service_data in services.items():
        if isinstance(service_data, dict) and 'summary' in service_data:
            service_findings = 0
            
            for check_name, check_data in service_data['summary'].items():
                if isinstance(check_data, dict) and '__affectedResources' in check_data:
                    affected_resources = check_data['__affectedResources']
                    finding_count = sum(len(resources) for resources in affected_resources.values())
                    service_findings += finding_count
                    
                    # Extract criticality and category if available
                    criticality = check_data.get('criticality', 'Info')
                    category = check_data.get('category', 'Other')
                    
                    findings_by_criticality[criticality] = findings_by_criticality.get(criticality, 0) + finding_count
                    findings_by_category[category] = findings_by_category.get(category, 0) + finding_count
            
            service_metrics.append({
                'service_name': service_name,
                'findings_count': service_findings,
                'scan_timestamp': metrics['scan_timestamp'],
                'account_id': metrics['account_id']
            })
    
    # Add aggregated metrics
    metrics.update({
        'findings_by_criticality': findings_by_criticality,
        'findings_by_category': findings_by_category,
        'service_metrics': service_metrics
    })
    
    return metrics

def update_manifest(s3_client, bucket):
    """Create/update QuickSight manifest file"""
    
    manifest = {
        "fileLocations": [
            {
                "URIs": [
                    f"s3://{bucket}/metrics/"
                ]
            }
        ],
        "globalUploadSettings": {
            "format": "JSON"
        }
    }
    
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key='manifest.json',
            Body=json.dumps(manifest, indent=2),
            ContentType='application/json'
        )
        print(f"Updated manifest file: s3://{bucket}/manifest.json")
    except Exception as e:
        print(f"Failed to update manifest: {str(e)}")
        # Don't fail the entire function for manifest issues
        pass