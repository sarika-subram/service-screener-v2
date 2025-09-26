#!/usr/bin/env python3
"""
Optional integration script for Service Screener observability.
Run this after Service Screener completes to upload metrics to S3.
"""

import json
import os
import sys
from datetime import datetime
from ObservabilityUploader import ObservabilityUploader

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 integration.py <path-to-service-screener-output>")
        print("Example: python3 integration.py ../../adminlte/aws/123456789012/")
        sys.exit(1)
    
    output_path = sys.argv[1]
    
    # Check if required files exist
    api_raw_path = os.path.join(output_path, 'api-raw.json')
    api_full_path = os.path.join(output_path, 'api-full.json')
    
    if not os.path.exists(api_raw_path):
        print(f"Error: {api_raw_path} not found")
        sys.exit(1)
    
    if not os.path.exists(api_full_path):
        print(f"Error: {api_full_path} not found")
        sys.exit(1)
    
    # Load the reports
    with open(api_raw_path, 'r') as f:
        raw_data = json.load(f)
    
    with open(api_full_path, 'r') as f:
        full_data = json.load(f)
    
    # Create summary data structure
    summary_data = {
        'resources': 0,
        'rules': 0,
        'timespent': 0,
        'findings': 0
    }
    
    # Extract basic metrics from the data
    for service_name, service_data in full_data.items():
        if 'summary' in service_data:
            for check_name, check_data in service_data['summary'].items():
                if '__affectedResources' in check_data:
                    affected_resources = check_data['__affectedResources']
                    finding_count = sum(len(resources) for resources in affected_resources.values())
                    summary_data['findings'] += finding_count
    
    # Upload to S3
    uploader = ObservabilityUploader()
    success = uploader.upload_report(raw_data, summary_data)
    
    if success:
        print("✅ Successfully uploaded observability data to S3")
    else:
        print("❌ Failed to upload observability data")
        sys.exit(1)

if __name__ == "__main__":
    main()