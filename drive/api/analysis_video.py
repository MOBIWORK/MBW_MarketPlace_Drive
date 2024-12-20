import frappe
import json
from drive.utils.s3 import upload_image_with_connect_byte, get_connect_s3, upload_object_from_stream, upload_file_with_connect
from drive.utils.files import _get_user_directory_name, create_thumbnail_by_object, create_thumbnail
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
from drive.utils.const import BASE_URL_AI

#API trích xuất dữ liệu geojson và ảnh đối tượng từ một video
# Với mỗi 1MB xử lý thì tương ứng với 1PPUV  
##Tham số đầu vào:
###name_file: Mã bản ghi tệp
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_with_geometry(name_file, parent):
    doc_task_queue = frappe.new_doc('Drive Task Queue')
    doc_task_queue.name = uuid.uuid4().hex
    try:
        result_process = process_input_file_same_name(name_file)
        if result_process.get("name_video") is not None and result_process.get("name_gpx") is not None:
            doc_video = frappe.get_doc("Drive Entity", result_process.get("name_video"))
            doc_video.is_analysis = True
            doc_video.save(ignore_permissions=True)
            doc_gpx = frappe.get_doc("Drive Entity", result_process.get("name_gpx"))
            doc_gpx.is_analysis = True
            doc_gpx.save(ignore_permissions=True)
            obj_task_metadata = {
                'name_file': doc_video.name,
                'parent': parent,
                'type': "video_with_gps",
                'title_file': doc_video.title,
                'file_size': doc_video.file_size,
                'name_gpx': doc_gpx.name
            }
            convert_mb_to_pupv = frappe.db.get_single_value('Drive Instance Settings', 'convert_mb_to_pupv')
            if convert_mb_to_pupv is None or convert_mb_to_pupv == 0:
                convert_mb_to_pupv = 1
            ppuv_used = round((doc_video.file_size/1048576) * convert_mb_to_pupv)
            doc_task_queue.pupv = ppuv_used
            doc_task_queue.task_metadata = json.dumps(obj_task_metadata)
            doc_task_queue.uploaded_time = datetime.now()
            if exist_pupv(ppuv_used) == False:
                doc_task_queue.status = "Error"
                doc_task_queue.error_message = "Insufficient Process Unit Per's Video(PUPV). Please upgrade the package to use"
                doc_task_queue.save(ignore_permissions=True)
                frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
                return
            #Triển khai code
            #url_file_video = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={doc_video.name}")
            #url_file_gps = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={doc_gpx.name}")
            #hook_url = frappe.utils.get_url("/api/method/drive.api.analysis_video.send_result_detect")
            #status_hook_url = frappe.utils.get_url("/api/method/drive.api.analysis_video.send_status_tasking")
            
            #Trên local
            url_file_video = f"http://10.0.1.85:8005/api/method/drive.api.files.get_file_content?entity_name={doc_video.name}"
            url_file_gps = f"http://10.0.1.85:8005/api/method/drive.api.files.get_file_content?entity_name={doc_gpx.name}"
            hook_url = "http://10.0.1.85:8005/api/method/drive.api.analysis_video.send_result_detect"
            status_hook_url = "http://10.0.1.85:8005/api/method/drive.api.analysis_video.send_status_tasking"

            sdk = RoadSDK(BASE_URL_AI)
            response = sdk.process_video_gpx(doc_task_queue.name, url_file_video, url_file_gps, hook_url, status_hook_url)
            doc_task_queue.status = "Pending"
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
    except Exception as e:
        doc_task_queue.status = "Error"
        doc_task_queue.pupv = 0
        doc_task_queue.uploaded_time = datetime.now()
        doc_task_queue.error_message = str(e)
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)

def process_input_file_same_name(name_file):
    doc_file = frappe.get_doc('Drive Entity', name_file)
    name_video = None
    name_gpx = None
    title_without_extension = os.path.splitext(doc_file.title)[0]
    files_analysis = frappe.db.get_list("Drive Entity",
        filters={
            'title': ['like', f'{title_without_extension}%'],
            'is_analysis': 0
        },
        fields=['name', 'file_kind', 'file_size', 'title']
    )
    if len(files_analysis) == 2:
        for file_analysis in files_analysis:
            if file_analysis.file_kind == "Video":
                name_video = file_analysis.name
            else:
                extension_file = os.path.splitext(file_analysis.title)[1]
                if extension_file == ".gpx":
                    name_gpx = file_analysis.name
    return {'name_video': name_video, 'name_gpx': name_gpx}

#API trích xuất dữ liệu phi không gian dưới dạng excel và ảnh đối tượng từ video
# Với mỗi 1MB xử lý thì tương ứng với 1PPUV
##Tham số đầu vào:
###name_file: Mã bản ghi tệp video thứ nhất
###parent: Mã thư mục cha chứa video phân tích
@frappe.whitelist(methods=["POST"])
def analytic_without_geometry(name_file, parent):
    doc_task_queue = frappe.new_doc('Drive Task Queue')
    doc_task_queue.name = uuid.uuid4().hex
    doc_file = frappe.get_doc('Drive Entity', name_file)
    obj_task_metadata = {
        'name_file': name_file,
        'parent': parent,
        'type': "video_without_gps",
        'title_file': doc_file.title,
        'file_size': doc_file.file_size
    }
    try:
        doc_file.is_analysis = True
        doc_file.save(ignore_permissions=True)

        convert_mb_to_pupv = frappe.db.get_single_value('Drive Instance Settings', 'convert_mb_to_pupv')
        if convert_mb_to_pupv is None or convert_mb_to_pupv == 0:
            convert_mb_to_pupv = 1

        ppuv_used = round((doc_file.file_size/1048576) * convert_mb_to_pupv)
        doc_task_queue.task_metadata = json.dumps(obj_task_metadata)
        doc_task_queue.pupv = ppuv_used
        doc_task_queue.uploaded_time = datetime.now()
        if exist_pupv(ppuv_used) == False:
            doc_task_queue.status = "Error"
            doc_task_queue.error_message = "Insufficient Process Unit Per's Video(PUPV). Please upgrade the package to use"
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
            return
        
        #Triển khai code
        #video_url = frappe.utils.get_url(f"/api/method/drive.api.files.get_file_content?entity_name={name_file}")
        #hook_url = frappe.utils.get_url("/api/method/drive.api.analysis_video.send_result_detect")
        #status_hook_url = frappe.utils.get_url("/api/method/drive.api.analysis_video.send_status_tasking")

        #Trên local
        video_url = f"http://10.0.1.85:8005/api/method/drive.api.files.get_file_content?entity_name={name_file}"
        hook_url = "http://10.0.1.85:8005/api/method/drive.api.analysis_video.send_result_detect"
        status_hook_url = "http://10.0.1.85:8005/api/method/drive.api.analysis_video.send_status_tasking"

        #BASE_URL_AI
        sdk = RoadSDK(BASE_URL_AI)
        response = sdk.process_single_video_velocity(doc_task_queue.name, video_url, 7, hook_url, status_hook_url)
        doc_task_queue.status = "Pending"
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
    except Exception as e:
        doc_task_queue.task_metadata = json.dumps(obj_task_metadata)
        doc_task_queue.pupv = 0
        doc_task_queue.status = "Error"
        doc_task_queue.uploaded_time = datetime.now()
        doc_task_queue.error_message = str(e)
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)

#API nhận trạng thái bắt đầu phân tích từ server AI trả về
##Tham số đầu vào:
###result: Kết quả server trả về
@frappe.whitelist(methods=["POST"], allow_guest=True)
def send_status_tasking(result):
    task_id = result["task_id"]
    if result["status"] == "PROCESSING":
        doc_tasking = frappe.get_doc("Drive Task Queue", task_id)
        doc_tasking.status = "Processing"
        doc_tasking.start_processing_time = datetime.now()
        doc_tasking.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=result["task_id"], user=frappe.session.user)

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
        if task_metadata["type"] == "video_with_gps":
            #Tạo dữ liệu không gian và ảnh
            #save_result_analysis_video_with_gps_job(task_metadata["name_file"], task_metadata["parent"], aws_access_key, aws_secret_access_key, result, task_metadata["name_gpx"])
            frappe.enqueue(
                save_result_analysis_video_with_gps_job,
                queue="long",
                timeout=None,
                name_fvideo=task_metadata["name_file"],
                parent=task_metadata["parent"],
                aws_access_key=aws_access_key,
                aws_secret_access_key=aws_secret_access_key,
                result=result,
                name_gpx=task_metadata["name_gpx"],
                base_url=frappe.utils.get_url()
            )
        else:
            #Tạo dữ liệu phi không gian excel và ảnh
            #save_result_analysis_with_velocity_job(task_metadata["name_file"], task_metadata["parent"], aws_access_key, aws_secret_access_key, result)
            frappe.enqueue(
                save_result_analysis_with_velocity_job,
                queue="long",
                timeout=None,
                name_fvideo=task_metadata["name_file"],
                parent=task_metadata["parent"],
                aws_access_key=aws_access_key,
                aws_secret_access_key=aws_secret_access_key,
                result=result,
                base_url=frappe.utils.get_url()
            )
    except Exception as e:
        doc_task_queue = frappe.get_doc('Drive Task Queue', task_id)
        doc_task_queue.pupv = 0
        doc_task_queue.status = "Error"
        doc_task_queue.error_message = str(e)
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)

@frappe.whitelist(methods=["GET"])
def list_tasks():
    tasks_response = []
    doc_tasks = frappe.db.get_list('Drive Task Queue',
        filters={
            'owner': frappe.session.user
        },
        fields=["name", "task_metadata", "status", "pupv", "error_message", "uploaded_time", "start_processing_time", "end_processing_time"]
    )
    for doc_task in doc_tasks:
        task_metadata = json.loads(doc_task.task_metadata)
        task_response = {
            'name': doc_task.name,
            'title': task_metadata.get("title_file", None),
            'file_size': task_metadata.get("file_size", None),
            'type_analysis': task_metadata.get("type", None),
            'status': doc_task.status,
            'pupv': doc_task.pupv,
            'error_message': doc_task.error_message,
            'uploaded_time': doc_task.uploaded_time,
            'start_processing_time': doc_task.start_processing_time,
            'end_processing_time': doc_task.end_processing_time
        }
        tasks_response.append(task_response)
    return tasks_response


def save_result_analysis_video_with_gps_job(name_fvideo, parent, aws_access_key, aws_secret_access_key, result, name_gpx, base_url):
    try:
        #BASE_URL_AI
        sdk = RoadSDK(BASE_URL_AI)
        doc_video = frappe.get_doc('Drive Entity', name_fvideo)
        doc_task_queue = frappe.get_doc('Drive Task Queue', result["task_id"])
        if result["status"]["process_status"] != "SUCCESS":
            doc_task_queue.status = "Error"
            doc_task_queue.error_message = str(result)
            doc_task_queue.end_processing_time = datetime.now()
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
            return
        metadata_result = result["process_result"]["metadata"]
        connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        new_folder_image = create_folder(f"Images_{int(timestamp)}", new_folder.name)
        spatial_datas = []
        for item in metadata_result:
            image_response = sdk.get_stream_by_url(item["image"])
            title_image = os.path.basename(item["image"])
            file_name_image = secure_filename(f"{title_image}")
            save_path = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_image}"
            #Dữ liệu lưu trên S3
            cache_key = f"s3_cache:{save_path}"
            frappe.cache().setex(cache_key, 3600, image_response.content)
            upload_object_from_stream(connect_s3, image_response, save_path, image_response.headers.get('Content-Type'))

            #Dữ liệu lưu trên disk
            #directory = os.path.dirname(save_path)
            # Tạo thư mục nếu chưa tồn tại
            # if not os.path.exists(directory):
            #     os.makedirs(directory)
            # with open(save_path, "wb") as file:
            #     for chunk in image_response.iter_content(chunk_size=8192):
            #         file.write(chunk)
            
            name = str(uuid.uuid4().hex)
            create_drive_entity(
                name, title_image, new_folder_image.name, save_path, image_response.headers.get('Content-Length'), ".jpg", "image/jpeg", None
            )
            #Tạo thumbnail dựa theo S3
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

            #Tạo thumbnail theo disk
            # frappe.enqueue(
            #     create_thumbnail,
            #     queue="default",
            #     timeout=None,
            #     now=True,
            #     at_front=True,
            #     entity_name=name,
            #     path=save_path,
            #     mime_type="image/jpeg"
            # )

            #Triển khai code
            #image_url = base_url + f"/api/method/drive.api.files.get_file_content?entity_name={name}"
            #Trên local
            image_url = f"http://10.0.1.85:8005/api/method/drive.api.files.get_file_content?entity_name={name}"
            if item["gps"]["longitude"] is not None and item["gps"]["longitude"] != 0 and item["gps"]["latitude"] is not None and item["gps"]["latitude"] != 0:
                spatial_data = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [item["gps"]["longitude"], item["gps"]["latitude"]]
                    },
                    "properties": {
                        "area_pixel": item["area_pixel"],
                        "area_real": item["area_real"],
                        "image": image_url,
                        "longitude": item["gps"]["longitude"],
                        "latitude": item["gps"]["latitude"]
                    }
                }
                spatial_datas.append(spatial_data)
        file_name_geojson = secure_filename(f"{doc_video.name}_object.geojson")
        key_object_geojson = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_geojson}"
        # Tạo đối tượng GeoJSON FeatureCollection
        geojson_data = geojson.FeatureCollection(spatial_datas)
        # Sử dụng BytesIO để lưu GeoJSON
        buffer = io.BytesIO()
        buffer.write(geojson.dumps(geojson_data).encode("utf-8"))

        #Lưu dữ liệu trên s3
        upload_image_with_connect_byte(connect_s3, buffer.getvalue(), key_object_geojson)
        
        #Lưu dữ liệu trên disk
        #directory = os.path.dirname(key_object_geojson)
        # Tạo thư mục nếu chưa tồn tại
        # if not os.path.exists(directory):
        #     os.makedirs(directory)
        # buffer.seek(0)
        # with open(key_object_geojson, "wb") as f:
        #     f.write(buffer.getvalue())

        name_geojson = str(uuid.uuid4().hex)
        create_drive_entity(
            name_geojson, f"results.geojson", new_folder.name, key_object_geojson, len(buffer.getvalue()), ".geojson", "application/geo+json", None
        )
        output_video_link = result["process_result"]["output_video"]
        if output_video_link != None:
            video_stream = sdk.get_stream_by_url(output_video_link)
            title_output_video = os.path.basename(output_video_link)
            file_name_output_video = secure_filename(f"{title_output_video}")
            key_object_video_output = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_output_video}"
            
            temp_path = f"{Path(get_user_uploads_directory(user=frappe.session.user))}/{new_folder.name}/{file_name_output_video}"
            directory = os.path.dirname(temp_path)
            #Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(temp_path, 'wb') as file:
                for chunk in video_stream.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            #Lưu vào redis cache
            with open(temp_path, 'rb') as f:
                cache_key = f"s3_cache:{key_object_video_output}"
                frappe.cache().setex(cache_key, 3600, f.read())

            #Lưu dữ liệu trên S3
            upload_file_with_connect(connect_s3, temp_path, key_object_video_output)

            name_output_video = str(uuid.uuid4().hex)
            #thay temp_path bằng key_object_video_output nếu thay S3
            create_drive_entity(
                name_output_video, title_output_video, new_folder.name, key_object_video_output, video_stream.headers.get('Content-Length'), ".mp4", "video/mp4", None, name_gpx
            )
            #Tạo thumb bằng S3
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

            #Tạo thumb dựa trên disk
            # frappe.enqueue(
            #     create_thumbnail,
            #     queue="default",
            #     timeout=None,
            #     now=True,
            #     at_front=True,
            #     entity_name=name_output_video,
            #     path=temp_path,
            #     mime_type="video/mp4"
            # )
        doc_task_queue.status = "Success"
        doc_task_queue.end_processing_time = datetime.now()
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=result["task_id"], user=frappe.session.user)
        frappe.publish_realtime('event_load_entities', user=frappe.session.user)
    except Exception as err:
        update_doc_task_queue(result["task_id"], "Error", str(err))
        frappe.publish_realtime('event_analytic_video_job', message=result["task_id"], user=frappe.session.user)

def save_result_analysis_with_velocity_job(name_fvideo, parent, aws_access_key, aws_secret_access_key, result, base_url):
    try:
        #BASE_URL_AI
        sdk = RoadSDK(BASE_URL_AI)
        doc_video = frappe.get_doc('Drive Entity', name_fvideo)
        doc_task_queue = frappe.get_doc('Drive Task Queue', result["task_id"])
        if result["status"]["process_status"] != "SUCCESS":
            doc_task_queue.status = "Error"
            doc_task_queue.error_message = str(result)
            doc_task_queue.end_processing_time = datetime.now()
            doc_task_queue.save(ignore_permissions=True)
            frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
            return
        metadata_result = result["process_result"]["metadata"]
        connect_s3 = get_connect_s3(aws_access_key, aws_secret_access_key)
        timestamp = datetime.timestamp(datetime.now())
        title_folder = f"Result_{int(timestamp)}_{doc_video.title}"
        new_folder = create_folder(title_folder, parent)
        new_folder_image = create_folder(f"Images_{int(timestamp)}", new_folder.name)
        data_xlsx = []
        headers = ["S_Real (m)", "S_pixel (pixel)", "Image"]
        data_xlsx.append(headers)
        for item in metadata_result:
            image_response = sdk.get_stream_by_url(item["image"])
            title_image = os.path.basename(item["image"])
            file_name_image = secure_filename(f"{title_image}")
            save_path = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_image}"

            #Upload dữ liệu lên S3
            upload_object_from_stream(connect_s3, image_response, save_path, image_response.headers.get('Content-Type'))
            
            #Lưu dữ liệu trên ổ đĩa disk
            #directory = os.path.dirname(save_path)
            # Tạo thư mục nếu chưa tồn tại
            # if not os.path.exists(directory):
            #     os.makedirs(directory)
            # with open(save_path, "wb") as file:
            #     for chunk in image_response.iter_content(chunk_size=8192):
            #         file.write(chunk)

            name = str(uuid.uuid4().hex)
            create_drive_entity(
                name, title_image, new_folder_image.name, save_path, image_response.headers.get('Content-Length'), ".jpg", "image/jpeg", None
            )
            #Tạo thumb với object S3
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

            #Tạo thumb trên disk
            # frappe.enqueue(
            #     create_thumbnail,
            #     queue="default",
            #     timeout=None,
            #     now=True,
            #     at_front=True,
            #     entity_name=name,
            #     path=save_path,
            #     mime_type="image/jpeg"
            # )

            #Triển khai code
            #image_url = base_url + f"/api/method/drive.api.files.get_file_content?entity_name={name}"

            #Trên local
            image_url = f"http://10.0.1.85:8005/api/method/drive.api.files.get_file_content?entity_name={name}"
            item_xlsx = [
                item["area_real"],
                item["area_pixel"],
                image_url
            ]
            data_xlsx.append(item_xlsx)
        byte_xlsx = make_xlsx(data_xlsx, "Data Export")
        file_name_xlsx = secure_filename(f"{doc_video.name}_object.xlsx")
        save_path_xlsx = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_xlsx}"
        #Lưu dữ liệu trên S3
        upload_image_with_connect_byte(connect_s3, byte_xlsx.getvalue(), save_path_xlsx)

        #Lưu dữ liệu trực tiếp trên disk
        #directory = os.path.dirname(save_path_xlsx)
        # Tạo thư mục nếu chưa tồn tại
        # if not os.path.exists(directory):
        #     os.makedirs(directory)
        # with open(save_path_xlsx, "wb") as file:
        #     file.write(byte_xlsx.getvalue())
        
        name_xlsx = str(uuid.uuid4().hex)
        create_drive_entity(
            name_xlsx, f"results.xlsx", new_folder.name, save_path_xlsx, len(byte_xlsx.getvalue()), ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", None
        )
        output_video_link = result["process_result"]["output_video"]
        if output_video_link != None:
            video_stream = sdk.get_stream_by_url(output_video_link)
            title_output_video = os.path.basename(output_video_link)
            file_name_output_video = secure_filename(f"{title_output_video}")
            key_object_video_output = f"{_get_user_directory_name()}/{new_folder.name}/{file_name_output_video}"

            #Lưu dữ liệu lên S3
            #upload_object_from_stream(connect_s3, video_stream, key_object_video_output, video_stream.headers.get('Content-Type'))

            #Lưu dữ liệu trên disk
            directory = os.path.dirname(key_object_video_output)
            # Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(key_object_video_output, 'wb') as file:
                for chunk in video_stream.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            #Lưu vào redis cache
            with open(key_object_video_output, 'rb') as f:
                cache_key = f"s3_cache:{key_object_video_output}"
                frappe.cache().setex(cache_key, 3600, f.read())

            #Lưu dữ liệu trên S3
            upload_file_with_connect(connect_s3, key_object_video_output, key_object_video_output)

            name_output_video = str(uuid.uuid4().hex)
            create_drive_entity(
                name_output_video, title_output_video, new_folder.name, key_object_video_output, video_stream.headers.get('Content-Length'), ".mp4", "video/mp4", None
            )
            #Tạo thumb dựa trên object S3
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

            #Tạo thumb trên disk
            # frappe.enqueue(
            #     create_thumbnail,
            #     queue="default",
            #     timeout=None,
            #     now=True,
            #     at_front=True,
            #     entity_name=name_output_video,
            #     path=key_object_video_output,
            #     mime_type="video/mp4"
            # )
        doc_task_queue.status = "Success"
        doc_task_queue.end_processing_time = datetime.now()
        doc_task_queue.save(ignore_permissions=True)
        frappe.publish_realtime('event_analytic_video_job', message=doc_task_queue.name, user=frappe.session.user)
        frappe.publish_realtime('event_load_entities', user=frappe.session.user)
    except Exception as err:
        update_doc_task_queue(result["task_id"], "Error", str(err))
        frappe.publish_realtime('event_analytic_video_job', message=result["task_id"], user=frappe.session.user)

def update_doc_task_queue(taskId, status, errorMessage=None):
    doc_task_queue = frappe.get_doc('Drive Task Queue', taskId)
    doc_task_queue.status = status
    doc_task_queue.error_message = errorMessage
    doc_task_queue.pupv = 0
    doc_task_queue.end_processing_time = datetime.now()
    doc_task_queue.save(ignore_permissions=True)