import argparse
import boto3
import requests
import os

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"File downloaded to {output_path}")

def upload(file_path, bn, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bn, s3_key)
    print(f"File uploaded to S3: s3://{bn}/{s3_key}")

def generate(bn, s3_key, expiration):
    s3 = boto3.client('s3')
    url = s3.generate(
        'get_object',
        Params={'Bucket': bn, 'Key': s3_key},
        ExpiresIn=expiration
    )
    print(f"Presigned URL: {url}")
    return url

def main():
    parser = argparse.ArgumentParser(description="Download a file, upload it to S3, and generate a presigned URL.")
    parser.add_argument('url', type=str, help="URL of the file to download")
    parser.add_argument('bucket', type=str, help="S3 bucket name")
    parser.add_argument('--key', type=str, default='uploaded_file.gif', help="S3 object key")
    parser.add_argument('--expiration', type=int, default=3600, help="Presigned URL expiration time in seconds")
    
    args = parser.parse_args()

    file_name = os.path.basename(args.url)
    local_path = f"/tmp/{file_name}"

    download_file(args.url, local_path)
    upload(local_path, args.bucket, args.key)
    generate(args.bucket, args.key, args.expiration)

if __name__ == "__main__":
    main()
