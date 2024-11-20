import frappe
import boto3
from botocore.exceptions import ClientError
import os
from drive.utils.const import BUCKET_NAME

conn = None

def init_conn(aws_access_id, aws_secret_access_key):
    global conn
    if conn is None:
        conn = boto3.client(
            "s3",
            aws_access_key_id = aws_access_id,
            aws_secret_access_key = aws_secret_access_key
        )

def upload_file(file_path, object_key):
    try:
        conn.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        conn.create_bucket(Bucket=BUCKET_NAME)
    
    try:
        conn.upload_file(file_path, BUCKET_NAME, object_key)

        #Xóa tệp trên ổ đĩa đi
        os.remove(file_path)
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

def upload_image_with_b(content, object_key):
    try:
        conn.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        conn.create_bucket(Bucket=BUCKET_NAME)
    
    try:
        conn.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=content,
            ContentType="image/png"
        )
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

def delete_file(object_key):
    if object_exists(BUCKET_NAME, object_key):
        conn.delete_object(
            Bucket=BUCKET_NAME,
            Key=object_key
        )
    else:
        print(f"Object {object_key} không tồn tại")

def object_exists(bucket, key):
    try:
        conn.head_object(
            Bucket = bucket,
            Key = key
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise

def get_file(object_key):
    if object_exists(BUCKET_NAME, object_key):
        return conn.get_object(
            Bucket = BUCKET_NAME,
            Key = object_key
        )
    else:
        return None

def get_connect_by_setting(aws_access_key_id, aws_secret_access_key):
    return boto3.client(
        "s3",
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key
    )

def get_object_with_conn(connect, object_key):
    return connect.get_object(
        Bucket = BUCKET_NAME,
        Key = object_key
    )

def upload_image_with_b_conn(connect, content, object_key):
    try:
        connect.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        connect.create_bucket(Bucket=BUCKET_NAME)
    
    try:
        connect.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=content,
            ContentType="image/png"
        )
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

@frappe.whitelist()
def list_objects(bucket_name):
    return conn.list_objects(Bucket=bucket_name)

@frappe.whitelist()
def list_bucket():
    return conn.list_buckets()

@frappe.whitelist()
def delete_objects(bucket_name):
    # Liệt kê các đối tượng trong bucket
    objects_to_delete = []
    response = conn.list_objects_v2(Bucket=bucket_name)
    
    # Kiểm tra xem có đối tượng nào trong bucket không
    if 'Contents' in response:
        # Tạo danh sách các đối tượng cần xóa
        for obj in response['Contents']:
            objects_to_delete.append({'Key': obj['Key']})

        # Xóa đối tượng
        if objects_to_delete:
            delete_response = conn.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects_to_delete}
            )
            return delete_response
        else:
            return "No objects to delete"
    else:
        return "Bucket is empty or does not exist"

def get_conn():
    return conn