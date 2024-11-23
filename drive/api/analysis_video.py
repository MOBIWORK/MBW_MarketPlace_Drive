import frappe
from drive.sdk.pothole_with_velocity import PotholeDetectionVelocityAPI
from drive.sdk.pothole_with_gps import PotholeDetectionGPSAPI
import json
import requests
from drive.utils.s3 import upload_image_with_connect_byte, get_object_with_connect, get_connect_s3
from drive.utils.files import _get_user_directory_name, create_thumbnail_by_object
from drive.api.files import (
    create_folder,
    create_drive_entity 
)
from werkzeug.utils import secure_filename
import uuid
from frappe.utils.xlsxutils import make_xlsx
from datetime import datetime
import geojson
import io

#API trích xuất dữ liệu geojson và ảnh đối tượng từ video
##Tham số đầu vào:
###name_fvideo: Mã bản ghi tệp video thứ nhất
###name_svideo: Mã bản ghi tệp video thứ hai
###name_gps: Mã bản ghi tệp gps
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_with_geometry(name_fvideo, name_svideo, name_gps, parent):
    doc_fvideo = frappe.get_doc('Drive Entity', name_fvideo)
    doc_svideo = frappe.get_doc('Drive Entity', name_svideo)
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')

    frappe.enqueue(
        analytic_video_with_gps_job,
        queue="default",
        timeout=None,
        name_fvideo=name_fvideo,
        name_svideo=name_svideo,
        name_gps=name_gps,
        parent=parent,
        aws_access_key=aws_access_key,
        aws_secret_access_key=aws_secret_access_key
    )
    return {"name": doc_fvideo.name, "title": f"{doc_fvideo.title}_{doc_svideo.title}"}

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

#API nhận kết quả phân tích video từ server AI trả về
##Tham số đầu vào:
###result: Kết quả của phép phân tích
@frappe.whitelist(methods=["POST"], allow_guest=True)
def send_result_detect(result):
    task_id = result["task_id"]
    print("Dòng 77 result ai: ",result)
    return
    try:
        doc_task_queue = frappe.get_doc('Drive Task Queue', task_id)
        task_metadata = json.loads(doc_task_queue.task_metadata)
        if result["status"]["process_status"] != "SUCCESS":
            #Cập nhật thêm vào csdl
            frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': task_metadata["name_fvideo"], 'status': "error", 'message': str(result["process_result"])}))
            return
        folder_parent = task_metadata["folder_parent"]
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}"
        new_folder = create_folder(title_folder, folder_parent)
        if task_metadata["type_analysis"] == "Video_GPS":
            #Tạo dữ liệu không gian và ảnh
            pass
        else:
            #Tạo dữ liệu phi không gian excel và ảnh
            pass
        #Cập nhật trạng thái trong csdl và realtime
    except Exception as e:
        #Cập nhật trạng thái trong csdl và realtime
        pass


def analytic_video_with_gps_job(name_fvideo, name_svideo, name_gps, parent, aws_access_key, aws_secret_access_key):
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    api = PotholeDetectionGPSAPI()
    try:
        doc_fvideo = frappe.get_doc('Drive Entity', name_fvideo)
        doc_svideo = frappe.get_doc('Drive Entity', name_svideo)
        doc_gps = frappe.get_doc('Drive Entity', name_gps)

        #Lấy dữ liệu trên S3 của video và gps
        response_fvideo = get_object_with_connect(connect_s3, doc_fvideo.path)
        file_fvideo_stream = response_fvideo["Body"]
        file_fvideo_content = file_fvideo_stream.read()
        response_svideo = get_object_with_connect(connect_s3, doc_svideo.path)
        file_svideo_stream = response_svideo["Body"]
        file_svideo_content = file_svideo_stream.read()
        response_fgps = get_object_with_connect(connect_s3, doc_gps.path)
        file_gps_stream = response_fgps["Body"]
        file_gps_content = file_gps_stream.read()

        detection_results = api.upload_video(file_fvideo_content, file_svideo_content, file_gps_content)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_fvideo.title}_{doc_svideo.title}"
        new_folder = create_folder(title_folder, parent)
        spatial_datas = []
        for item in detection_results:
            image_data = api.get_image(item["image"])
            id_frame = item["ID"]
            file_name_image = secure_filename(f"{doc_fvideo.name}_{id_frame}.png")
            save_path = f"{_get_user_directory_name()}/{file_name_image}"
            upload_image_with_connect_byte(connect_s3, image_data, save_path)
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
            spatial_data = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [item["lng"], item["lat"]]
                },
                "properties": {
                    "ID": item["ID"],
                    "End_Frame": item["End_Frame"],
                    "Ratio": item["Ratio"],
                    "S_Real(m)": item["S_Real(m)"],
                    "S_pixel(pixel)": item["S_pixel(pixel)"],
                    "Start_Frame": item["Start_Frame"],
                    "Image": frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name}")
                }
            }
            spatial_datas.append(spatial_data)
        file_name_geojson = secure_filename(f"{doc_fvideo.name}_object.geojson")
        key_object_geojson = f"{_get_user_directory_name()}/{file_name_geojson}"
        # Tạo đối tượng GeoJSON FeatureCollection
        geojson_data = geojson.FeatureCollection(spatial_datas)
        # Sử dụng BytesIO để lưu GeoJSON
        buffer = io.BytesIO()
        buffer.write(geojson.dumps(geojson_data).encode("utf-8"))
        upload_image_with_connect_byte(connect_s3, buffer.getvalue(), key_object_geojson)
        name_geojson = str(uuid.uuid4().hex)
        create_drive_entity(
            name_geojson, f"results.geojson", new_folder.name, key_object_geojson, len(buffer.getvalue()), ".geojson", "application/geo+json", None
        )
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_fvideo.name, 'status': "success", 'message': new_folder.name}))
    except requests.exceptions.HTTPError as http_err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_fvideo.name, 'status': "error", 'message': str(http_err)}))
    except Exception as err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_fvideo.name, 'status': "error", 'message': str(err)}))

def analytic_video_with_velocity_job(name_fvideo, velocity, parent, aws_access_key, aws_secret_access_key):
    connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
    api = PotholeDetectionVelocityAPI()
    doc_video = frappe.get_doc('Drive Entity', name_fvideo)
    try:
        response = get_object_with_connect(connect_s3, doc_video.path)
        if response is None:
            frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "error", 'message': "object not found in s3"}))
            return
        file_stream = response['Body']
        file_content = file_stream.read()
        detection_results = api.upload_video_with_velocity(file_content, velocity)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        data_xlsx = []
        headers = ["ID", "Ratio", "S_Real (m)", "S_pixel (pixel)", "Start Frame", "End Frame", "Image"]
        data_xlsx.append(headers)
        for item in detection_results:
            image_data = api.get_image(item["image"])
            id_frame = item["ID"]
            file_name_image = secure_filename(f"{doc_video.name}_{id_frame}.png")
            save_path = f"{_get_user_directory_name()}/{file_name_image}"
            upload_image_with_connect_byte(connect_s3, image_data, save_path)
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
            item_xlsx = [
                id_frame,
                item["Ratio"],
                item["S_Real(m)"],
                item["S_pixel(pixel)"],
                item["Start_Frame"],
                item["End_Frame"],
                frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name}")
            ]
            data_xlsx.append(item_xlsx)
        byte_xlsx = make_xlsx(data_xlsx, "Data Export")
        file_name_xlsx = secure_filename(f"{doc_video.name}_object.xlsx")
        save_path_xlsx = f"{_get_user_directory_name()}/{file_name_xlsx}"
        upload_image_with_connect_byte(connect_s3, byte_xlsx.getvalue(), save_path_xlsx)
        name_xlsx = str(uuid.uuid4().hex)
        create_drive_entity(
            name_xlsx, f"results.xlsx", new_folder.name, save_path_xlsx, len(byte_xlsx.getvalue()), ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", None
        )
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "success", 'message': new_folder.name}))
    except requests.exceptions.HTTPError as http_err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "error", 'message': str(http_err)}))
    except Exception as err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "error", 'message': str(err)}))





