import frappe
import boto3
from botocore.exceptions import ClientError
import os

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

def create_bucket_with_connect(connect):
    try:
        bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
        connect.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        connect.create_bucket(Bucket=bucket_name)

def upload_file_with_connect(connect, file_path, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    try:
        connect.upload_file(file_path, bucket_name, object_key)
        #Xóa tệp trên ổ đĩa đi
        os.remove(file_path)
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

def upload_image_with_connect_byte(connect, content, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    try:
        connect.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content,
            ContentType="image/png"
        )
    except Exception as e:
        print(f"Lỗi khi tải lên s3: {e}")

def get_object_with_connect(connect, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    return connect.get_object(
        Bucket = bucket_name,
        Key = object_key
    )

def delete_object_with_connect(connect, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    connect.delete_object(
        Bucket=bucket_name,
        Key=object_key
    )

def upload_object_from_stream(connect, stream, object_key, content_type):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    connect.upload_fileobj(
        stream.raw,
        bucket_name,
        object_key
    )

def upload_fileobj_with_connect(connect, chunk, object_key, content_type):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
    connect.upload_fileobj(
        chunk,
        bucket_name,
        object_key,
        ExtraArgs={'ContentType': content_type}
    )

@frappe.whitelist()
def get_object_by_key(bucket_name, key_object):
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    content = connect_s3.get_object(
        Bucket = bucket_name,
        Key = key_object
    )
    return content

@frappe.whitelist()
def post_object_to_s3(src_file):
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    connect_s3.upload_file(src_file, "eov-geoviz", "/test/objs3.jpg")
    return "ok"
    

@frappe.whitelist()
def list_objects(bucket_name):
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    return connect_s3.list_objects(Bucket=bucket_name)

@frappe.whitelist()
def list_bucket():
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    return connect_s3.list_buckets()

@frappe.whitelist()
def delete_objects(bucket_name):
    # Liệt kê các đối tượng trong bucket
    objects_to_delete = []
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
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

@frappe.whitelist()
def get_bucket_region(bucket_name):
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    response = connect_s3.get_bucket_location(Bucket=bucket_name)
    return response.get('LocationConstraint')
