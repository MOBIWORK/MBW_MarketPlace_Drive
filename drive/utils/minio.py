from minio import Minio
from minio.error import S3Error
import frappe
import os

connect_minio = None

def get_connect_minio(host_url, access_key, secret_key):
    global connect_minio
    if connect_minio is None:
        connect_minio = Minio(host_url, 
            access_key=access_key,
            secret_key=secret_key
        )
    return connect_minio

def create_bucket_with_connect(connect):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    found_bucket = connect.bucket_exists(bucket_name)
    if not found_bucket:
        connect.make_bucket(bucket_name)

def upload_file_with_connect(connect, file_path, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    try:
        connect.fput_object(bucket_name, object_key, file_path)
    except S3Error as err:
        print(f"Lỗi khi tải lên s3: {err}")

def upload_image_with_connect_byte(connect, content, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    try:
        connect.put_object(
            bucket_name,
            object_key,
            data=iter([content]),  # Dữ liệu byte được chuyển thành iterable
            length=len(content),
            content_type="image/png"  # Content-Type của object
        )
    except S3Error as err:
        print(f"Lỗi khi tải lên s3: {err}")

def get_object_with_connect(connect, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    try:
        response = connect.get_object(bucket_name, object_key)
    finally:
        response.close()
        response.release_conn()
    return response

def delete_object_with_connect(connect, object_key):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    connect.remove_object(bucket_name, object_key)

def upload_object_from_stream(connect, stream, object_key, content_type):
    bucket_name = frappe.db.get_single_value("Drive Instance Settings", "bucket_name_minio")
    connect.put_object(
        bucket_name,
        object_key,
        data=stream.raw,       # Sử dụng stream từ response
        length=int(stream.headers['Content-Length']),  # Lấy kích thước từ header
        content_type=content_type
    )
