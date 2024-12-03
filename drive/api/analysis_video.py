import frappe
import json
from drive.utils.s3 import upload_image_with_connect_byte, get_connect_s3, upload_object_from_stream, upload_file_with_connect
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
from drive.sdk.road import RoadSDK
import os
from drive.utils.using_quota import exist_pupv
from pathlib import Path
from drive.api.files import get_user_uploads_directory

#API trích xuất dữ liệu geojson và ảnh đối tượng từ một video
# Với mỗi 1MB xử lý thì tương ứng với 1PPUV  
##Tham số đầu vào:
###name_fvideo: Mã bản ghi tệp video thứ nhất
###name_gps: Mã bản ghi tệp gps
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_video_with_geometry(name_fvideo, name_gps, parent):
    doc_fvideo = frappe.get_doc('Drive Entity', name_fvideo)

    convert_mb_to_pupv = frappe.db.get_single_value('Drive Instance Settings', 'convert_mb_to_pupv')
    if convert_mb_to_pupv is None or convert_mb_to_pupv == 0:
        convert_mb_to_pupv = 1

    ppuv_used = (doc_fvideo.file_size/1048576) * convert_mb_to_pupv

    if exist_pupv(ppuv_used) == False:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': "Insufficient Process Unit Per's Video(PUPV). Please upgrade the package to use"}), user=frappe.session.user)
        return 

    doc_task_queue = frappe.new_doc('Drive Task Queue')
    obj_task_metadata = {
        'name_fvideo': name_fvideo,
        'name_gps': name_gps,
        'parent': parent,
        'type': "Video_GPS"
    }
    doc_task_queue.task_metadata = json.dumps(obj_task_metadata)
    doc_task_queue.status = "Processing"
    doc_task_queue.pupv = ppuv_used
    doc_task_queue.save(ignore_permissions=True)

    #host = "http://10.0.1.85:8005"
    video_url = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name_fvideo}")
    gps_url = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name_gps}")
    #video_url = f"{host}/api/method/drive.api.files.get_file_content?entity_name={name_fvideo}"
    #gps_url = f"{host}/api/method/drive.api.files.get_file_content?entity_name={name_gps}"
    sdk = RoadSDK()
    response = sdk.process_video_gpx(doc_task_queue.name, video_url, gps_url)
    return {"name": doc_fvideo.name, "title": f"{doc_fvideo.title}"}

#API trích xuất dữ liệu phi không gian dưới dạng excel và ảnh đối tượng từ video
# Với mỗi 1MB xử lý thì tương ứng với 1PPUV
##Tham số đầu vào:
###name_fvideo: Mã bản ghi tệp video thứ nhất
###velocity: Tốc độ di chuyển tính bằng km/h
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_without_geometry(name_fvideo, velocity, parent):
    doc_fvideo = frappe.get_doc('Drive Entity', name_fvideo)

    convert_mb_to_pupv = frappe.db.get_single_value('Drive Instance Settings', 'convert_mb_to_pupv')
    if convert_mb_to_pupv is None or convert_mb_to_pupv == 0:
        convert_mb_to_pupv = 1

    ppuv_used = (doc_fvideo.file_size/1048576) * convert_mb_to_pupv
    if exist_pupv(ppuv_used) == False:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': "Insufficient Process Unit Per's Video(PUPV). Please upgrade the package to use"}), user=frappe.session.user)
        return

    doc_task_queue = frappe.new_doc('Drive Task Queue')
    obj_task_metadata = {
        'name_fvideo': name_fvideo,
        'velocity': velocity,
        'parent': parent,
        'type': "Video_Velocity"
    }
    doc_task_queue.task_metadata = json.dumps(obj_task_metadata)
    doc_task_queue.status = "Processing"
    doc_task_queue.pupv = ppuv_used
    doc_task_queue.save(ignore_permissions=True)
    
    #host = "http://10.0.1.85:8005"
    video_url = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name_fvideo}")
    #video_url = f"{host}/api/method/drive.api.files.get_file_content?entity_name={name_fvideo}"
    sdk = RoadSDK()
    response = sdk.process_single_video_velocity(doc_task_queue.name, video_url, velocity)
    return {"name": doc_fvideo.name, "title": doc_fvideo.title}

#API nhận kết quả phân tích video từ server AI trả về
##Tham số đầu vào:
###result: Kết quả của phép phân tích
@frappe.whitelist(methods=["POST"], allow_guest=True)
def send_result_detect(result):
    task_id = result["task_id"]
    doc_setting = frappe.get_single('Drive Instance Settings')
    aws_access_key = doc_setting.aws_access_key
    aws_secret_access_key = doc_setting.get_password('aws_secret_key')
    doc_task_queue = frappe.get_doc('Drive Task Queue', task_id)
    task_metadata = json.loads(doc_task_queue.task_metadata)
    frappe.set_user(doc_setting.owner)
    try:
        if task_metadata["type"] == "Video_GPS":
            #Tạo dữ liệu không gian và ảnh
            #save_result_analysis_video_with_gps_job(task_metadata["name_fvideo"], task_metadata["parent"], aws_access_key, aws_secret_access_key, result)
            frappe.enqueue(
                save_result_analysis_video_with_gps_job,
                queue="default",
                timeout=None,
                name_fvideo=task_metadata["name_fvideo"],
                parent=task_metadata["parent"],
                aws_access_key=aws_access_key,
                aws_secret_access_key=aws_secret_access_key,
                result=result
            )
        else:
            #Tạo dữ liệu phi không gian excel và ảnh
            #save_result_analysis_with_velocity_job(task_metadata["name_fvideo"], task_metadata["parent"], aws_access_key, aws_secret_access_key, result)
            frappe.enqueue(
                save_result_analysis_with_velocity_job,
                queue="default",
                timeout=None,
                name_fvideo=task_metadata["name_fvideo"],
                parent=task_metadata["parent"],
                aws_access_key=aws_access_key,
                aws_secret_access_key=aws_secret_access_key,
                result=result
            )
    except Exception as e:
        doc_task_queue = frappe.get_doc('Drive Task Queue', task_id)
        doc_task_queue.status = "Error"
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': task_metadata["name_fvideo"], 'status': "error", 'message': str(e)}), user=frappe.session.user)

def save_result_analysis_video_with_gps_job(name_fvideo, parent, aws_access_key, aws_secret_access_key, result):
    try:
        sdk = RoadSDK()
        doc_video = frappe.get_doc('Drive Entity', name_fvideo)
        doc_task_queue = frappe.get_doc('Drive Task Queue', result["task_id"])
        if result["status"]["process_status"] != "SUCCESS":
            doc_task_queue.status = "Error"
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': "Error AI Server"}), user=frappe.session.user)
            return
        metadata_result = result["process_result"]["metadata"]
        connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        spatial_datas = []
        for item in metadata_result:
            image_response = sdk.get_stream_by_url(item["image"])
            title_image = os.path.basename(item["image"])
            file_name_image = secure_filename(title_image)
            save_path = f"{_get_user_directory_name()}/{file_name_image}"
            upload_object_from_stream(connect_s3, image_response, save_path, image_response.headers.get('Content-Type'))
            name = str(uuid.uuid4().hex)
            create_drive_entity(
                name, title_image, new_folder.name, save_path, image_response.headers.get('Content-Length'), ".jpg", "image/jpeg", None
            )
            frappe.enqueue(
                create_thumbnail_by_object,
                queue="default",
                timeout=None,
                now=True,
                at_front=True,
                entity_name=name,
                object_id=save_path,
                mime_type="image/jpeg"
            )
            spatial_data = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [item["gps"]["longitude"], item["gps"]["latitude"]]
                },
                "properties": {
                    "area_pixel": item["area_pixel"],
                    "area_real": item["area_real"],
                    "image": frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name}"),
                    "longitude": item["gps"]["longitude"],
                    "latitude": item["gps"]["latitude"]
                }
            }
            spatial_datas.append(spatial_data)
        file_name_geojson = secure_filename(f"{doc_video.name}_object.geojson")
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
        output_video_link = result["process_result"]["output_video"]
        if output_video_link != None:
            video_stream = sdk.get_stream_by_url(output_video_link)
            title_output_video = os.path.basename(output_video_link)
            file_name_output_video = secure_filename(title_output_video)
            key_object_video_output = f"{_get_user_directory_name()}/{file_name_output_video}"
            
            temp_path = (
                Path(get_user_uploads_directory(user=frappe.session.user))
                / f"{int(timestamp)}_{file_name_output_video}"
            )
            with open(temp_path, 'wb') as file:
                for chunk in video_stream.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            upload_file_with_connect(connect_s3, temp_path, key_object_video_output)
            #upload_object_from_stream(connect_s3, video_stream, key_object_video_output, video_stream.headers.get('Content-Type'))
            name_output_video = str(uuid.uuid4().hex)
            create_drive_entity(
                name_output_video, title_output_video, new_folder.name, key_object_video_output, video_stream.headers.get('Content-Length'), ".mp4", "video/mp4", None
            )
            frappe.enqueue(
                create_thumbnail_by_object,
                queue="default",
                timeout=None,
                now=True,
                at_front=True,
                entity_name=name_output_video,
                object_id=key_object_video_output,
                mime_type="video/mp4"
            )
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': doc_video.name, 'status': "success", 'message': new_folder.name}), user=frappe.session.user)
    except Exception as err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': str(err)}), user=frappe.session.user)

def save_result_analysis_with_velocity_job(name_fvideo, parent, aws_access_key, aws_secret_access_key, result):
    try:
        sdk = RoadSDK()
        doc_video = frappe.get_doc('Drive Entity', name_fvideo)
        doc_task_queue = frappe.get_doc('Drive Task Queue', result["task_id"])
        if result["status"]["process_status"] != "SUCCESS":
            doc_task_queue.status = "Error"
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': "Error AI Server"}), user=frappe.session.user)
            return
        metadata_result = result["process_result"]["metadata"]
        connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        data_xlsx = []
        headers = ["S_Real (m)", "S_pixel (pixel)", "Image"]
        data_xlsx.append(headers)
        for item in metadata_result:
            image_response = sdk.get_stream_by_url(item["image"])
            title_image = os.path.basename(item["image"])
            file_name_image = secure_filename(title_image)
            save_path = f"{_get_user_directory_name()}/{file_name_image}"
            upload_object_from_stream(connect_s3, image_response, save_path, image_response.headers.get('Content-Type'))
            name = str(uuid.uuid4().hex)
            create_drive_entity(
                name, title_image, new_folder.name, save_path, image_response.headers.get('Content-Length'), ".jpg", "image/jpeg", None
            )
            frappe.enqueue(
                create_thumbnail_by_object,
                queue="default",
                timeout=None,
                now=True,
                at_front=True,
                entity_name=name,
                object_id=save_path,
                mime_type="image/jpeg"
            )
            item_xlsx = [
                item["area_real"],
                item["area_pixel"],
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
        output_video_link = result["process_result"]["output_video"]
        if output_video_link != None:
            video_stream = sdk.get_stream_by_url(output_video_link)
            title_output_video = os.path.basename(output_video_link)
            file_name_output_video = secure_filename(title_output_video)
            key_object_video_output = f"{_get_user_directory_name()}/{file_name_output_video}"
            upload_object_from_stream(connect_s3, video_stream, key_object_video_output, video_stream.headers.get('Content-Type'))
            name_output_video = str(uuid.uuid4().hex)
            create_drive_entity(
                name_output_video, title_output_video, new_folder.name, key_object_video_output, video_stream.headers.get('Content-Length'), ".mp4", "video/mp4", None
            )
            frappe.enqueue(
                create_thumbnail_by_object,
                queue="default",
                timeout=None,
                now=True,
                at_front=True,
                entity_name=name_output_video,
                object_id=key_object_video_output,
                mime_type="video/mp4"
            )
        doc_task_queue.status = "Success"
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "success", 'message': new_folder.name}), user=frappe.session.user)
    except Exception as err:
        frappe.publish_realtime('event_analytic_video_job', message=json.dumps({'name': name_fvideo, 'status': "error", 'message': str(err)}), user=frappe.session.user)
