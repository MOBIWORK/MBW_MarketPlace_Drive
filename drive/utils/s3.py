import frappe
import boto3
from botocore.exceptions import ClientError
import os
from drive.utils.const import BUCKET_NAME

connect_s3 = None

def get_connect_s3(aws_access_id, aws_secret_access_key):
    global connect_s3
    if connect_s3 is None:
        connect_s3 = boto3.client(
            "s3",
            aws_access_key_id = aws_access_id,
            aws_secret_access_key = aws_secret_access_key
        )
    return connect_s3

def upload_file_with_connect(connect, file_path, object_key):
    try:
        connect.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        connect.create_bucket(Bucket=BUCKET_NAME)
    
    try:
        connect.upload_file(file_path, BUCKET_NAME, object_key)
        #Xóa tệp trên ổ đĩa đi
        os.remove(file_path)
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

def upload_image_with_connect_byte(connect, content, object_key):
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

def get_object_with_connect(connect, object_key):
    return connect.get_object(
        Bucket = BUCKET_NAME,
        Key = object_key
    )

def delete_object_with_connect(connect, object_key):
    connect.delete_object(
        Bucket=BUCKET_NAME,
        Key=object_key
    )

@frappe.whitelist()
def list_objects(bucket_name):
    return connect_s3.list_objects(Bucket=bucket_name)

@frappe.whitelist()
def list_bucket():
    return connect_s3.list_buckets()

@frappe.whitelist()
def delete_objects(bucket_name):
    # Liệt kê các đối tượng trong bucket
    objects_to_delete = []
    response = connect_s3.list_objects_v2(Bucket=bucket_name)
    
    # Kiểm tra xem có đối tượng nào trong bucket không
    if 'Contents' in response:
        # Tạo danh sách các đối tượng cần xóa
        for obj in response['Contents']:
            objects_to_delete.append({'Key': obj['Key']})

        # Xóa đối tượng
        if objects_to_delete:
            delete_response = connect_s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': objects_to_delete}
            )
            return delete_response
        else:
            return "No objects to delete"
    else:
        return "Bucket is empty or does not exist"
