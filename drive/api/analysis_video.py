import frappe
from drive.sdk.pothole_with_velocity import PotholeDetectionVelocityAPI
import json
import requests
from drive.utils.s3 import get_file, upload_image_with_b, init_conn, get_conn, get_connect_by_setting, get_object_with_conn, upload_image_with_b_conn
from drive.utils.files import _get_user_directory_name, create_thumbnail_by_object
from drive.api.files import (
    create_folder,
    create_drive_entity 
)
from werkzeug.utils import secure_filename
import uuid
from frappe.utils.xlsxutils import make_xlsx
from datetime import datetime

#API trích xuất dữ liệu geojson và ảnh đối tượng từ video
##Tham số đầu vào:
###name_fvideo: Mã bản ghi tệp video thứ nhất
###name_svideo: Mã bản ghi tệp video thứ hai
###name_gps: Mã bản ghi tệp gps
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_with_geometry(name_fvideo, name_svideo, name_gps, parent):
    pass

#API trích xuất dữ liệu phi không gian dưới dạng excel và ảnh đối tượng từ video
##Tham số đầu vào:
###name_fvideo: Mã bản ghi tệp video thứ nhất
###velocity: Tốc độ di chuyển tính bằng km/h
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_without_geometry(name_fvideo, velocity, parent):
    doc_fvideo = frappe.get_doc('Drive Entity', name_fvideo)
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    
    #analytic_video_with_velocity_job(name_fvideo, velocity, parent)
    frappe.enqueue(
        analytic_video_with_velocity_job,
        queue="default",
        timeout=None,
        name_fvideo=name_fvideo,
        velocity=velocity,
        parent=parent,
        aws_access_key=aws_access_key,
        aws_secret_access_key=aws_secret_access_key
    )
    return {"name": doc_fvideo.name, "title": doc_fvideo.title}

def analytic_video_with_velocity_job(name_fvideo, velocity, parent, aws_access_key, aws_secret_access_key):
    connect_s3 = get_connect_by_setting(aws_access_key, aws_secret_access_key)
    api = PotholeDetectionVelocityAPI()
    doc_video = frappe.get_doc('Drive Entity', name_fvideo)
    try:
        response = get_object_with_conn(connect_s3, doc_video.path)
        if response is None:
            frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "empty"}))
            return
        file_stream = response['Body']
        file_content = file_stream.read()
        detection_results = api.upload_video_with_velocity(file_content, velocity)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        data_xlsx = []
        for item in detection_results:
            image_data = api.get_image(item["image"])
            id_frame = item["ID"]
            file_name_image = secure_filename(f"{doc_video.name}_{id_frame}.png")
            save_path = f"{_get_user_directory_name()}/{file_name_image}"
            upload_image_with_b_conn(connect_s3, image_data, save_path)
            name = str(uuid.uuid4().hex)
            create_drive_entity(
                name, f"{id_frame}.png", new_folder.name, save_path, len(image_data), ".png", "image/png", None
            )
            frappe.enqueue(
                create_thumbnail_by_object,
                queue="default",
                timeout=None,
                now=True,
                at_front=True,
                entity_name=name,
                object_id=save_path,
                mime_type="image/png"
            )
            item_xlsx = {
                "ID": id_frame,
                "Ratio": item["Ratio"],
                "S_Real (m)": item["S_Real(m)"],
                "S_pixel (pixel)": item["S_pixel(pixel)"],
                "Start Frame": item["Start_Frame"],
                "End Frame": item["End_Frame"]
            }
            data_xlsx.append(item_xlsx)
        byte_xlsx = make_xlsx(data_xlsx, "Data Export")
        file_name_xlsx = secure_filename(f"{doc_video.name}_object.xlsx")
        save_path_xlsx = f"{_get_user_directory_name()}/{file_name_xlsx}"
        upload_image_with_b_conn(connect_s3, byte_xlsx.getvalue(), save_path_xlsx)
        name_xlsx = str(uuid.uuid4().hex)
        create_drive_entity(
            name_xlsx, f"results.xlsx", new_folder.name, save_path_xlsx, len(byte_xlsx.getvalue()), ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", None
        )
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "success"}))
    except requests.exceptions.HTTPError as http_err:
        print("Dòng 100 ", str(http_err))
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "error"}))
    except Exception as err:
        print("Dòng 103 ", str(err))
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "error"}))





