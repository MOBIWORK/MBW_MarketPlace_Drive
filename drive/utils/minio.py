from minio import Minio
from minio.error import S3Error
import frappe
import os

import geojson
import io

connect_minio = None

def get_connect_minio(host_url, access_key, secret_key):
    global connect_minio
    if connect_minio is None:
        connect_minio = Minio(host_url, 
            access_key=access_key,
            secret_key=secret_key,
            secure=False
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

@frappe.whitelist(methods=["GET"])
def list_bucket():
    host_url = frappe.db.get_single_value("Drive Instance Settings", "host_minio_s3")
    access_key = frappe.db.get_single_value("Drive Instance Settings", "access_key_minio_s3")
    secret_key = frappe.db.get_single_value("Drive Instance Settings", "secret_key_minio_s3")
    client = Minio(host_url,
        access_key = access_key,
        secret_key = secret_key,
        secure=False
    )
    buckets = client.list_buckets()
    buckets_res = []
    for bucket in buckets:
        buckets_res.append({
            'name': bucket.name,
            'creation': bucket.creation_date
        })
    return buckets_res

@frappe.whitelist(methods="GET")
def list_object():
    objects_response = []
    host_url = frappe.db.get_single_value("Drive Instance Settings", "host_minio_s3")
    access_key = frappe.db.get_single_value("Drive Instance Settings", "access_key_minio_s3")
    secret_key = frappe.db.get_single_value("Drive Instance Settings", "secret_key_minio_s3")
    print("Dòng 91 ", access_key)
    print("Dòng 92 ", secret_key)
    client = Minio(host_url,
        access_key = access_key,
        secret_key = secret_key,
        secure=False
    )
    objects = client.list_objects("eov-geoviz")
    for obj in objects:
        objects_response.append(obj.object_name)
    return objects_response

@frappe.whitelist(methods="POST")
def upload_file_minio(file_path, object_key):
    host_url = frappe.db.get_single_value("Drive Instance Settings", "host_minio_s3")
    access_key = frappe.db.get_single_value("Drive Instance Settings", "access_key_minio_s3")
    secret_key = frappe.db.get_single_value("Drive Instance Settings", "secret_key_minio_s3")
    connect_minio = get_connect_minio(host_url, access_key, secret_key)
    upload_file_with_connect(connect_minio, file_path, object_key)
    return "ok"

@frappe.whitelist(methods="POST")
def upload_image_with_connect_byte_minio(object_key):
    spatial_datas = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [102, 90]
            },
                "properties": {
                    "area_pixel": 123
                }
        }
    ]
    geojson_data = geojson.FeatureCollection(spatial_datas)
    buffer = io.BytesIO()
    buffer.write(geojson.dumps(geojson_data).encode("utf-8"))
    host_url = frappe.db.get_single_value("Drive Instance Settings", "host_minio_s3")
    access_key = frappe.db.get_single_value("Drive Instance Settings", "access_key_minio_s3")
    secret_key = frappe.db.get_single_value("Drive Instance Settings", "secret_key_minio_s3")
    connect_minio = get_connect_minio(host_url, access_key, secret_key)
    upload_image_with_connect_byte(connect_minio, buffer.getvalue(), object_key)
    return "ok"