import frappe
import boto3
from botocore.exceptions import ClientError
import os

doc_setting = frappe.get_single('Drive Instance Settings')
conn = boto3.client(
    "s3",
    aws_access_key_id = doc_setting.aws_access_key,
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
)

def upload_file(file_path, object_key):
    try:
        conn.head_bucket(Bucket="eov-geoviz")
    except ClientError as e:
        conn.create_bucket(Bucket="eov-geoviz")
    
    try:
        conn.upload_file(file_path, "eov-geoviz", object_key)

        #Xóa tệp trên ổ đĩa đi
        os.remove(file_path)
    except Exception as e:
        print(f"Dòng 21 Lỗi khi tải lên s3: {e}")

@frappe.whitelist()
def list_objects(bucket_name):
    return conn.list_objects(Bucket=bucket_name)

@frappe.whitelist()
def list_bucket():
    return conn.list_buckets()

def get_conn():
    return conn