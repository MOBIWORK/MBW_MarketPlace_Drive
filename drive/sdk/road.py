import requests
from typing import Union, Dict

class RoadSDK:
    def __init__(self, base_url: str):
        """
        Khởi tạo SDK với URL gốc của API.

        Args:
            base_url (str): URL gốc của API (ví dụ: "http://example.com/api").
        """
        self.base_url = base_url

    def process_single_video(self,task_id: str, video_url: str, hook_url: str, status_hook_url: str) -> Dict:
        """
        Gửi yêu cầu xử lý video đơn lẻ.

        Args:
            video_url (str): URL của video cần xử lý.

        Returns:
            dict: Kết quả trả về từ API.
        """
        endpoint = f"{self.base_url}/process-single-video/"
        payload = {"task_id": task_id, "video_url": video_url, "hook_url": hook_url, "status_hook_url": status_hook_url}
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def process_single_video_velocity(self, task_id: str,  video_url: str, velocity: float, hook_url: str, status_hook_url: str) -> Dict:
        """
        Gửi yêu cầu xử lý video đơn lẻ.

        Args:
            video_url (str): URL của video cần xử lý.

        Returns:
            dict: Kết quả trả về từ API.
        """
        endpoint = f"{self.base_url}/process-single-video-velocity/"
        payload = {"task_id": task_id, "video_url": video_url, "velocity": velocity, "hook_url": hook_url, "status_hook_url": status_hook_url}
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    def process_video_gpx(self,task_id: str,  video_url: str, gpx_url: str, hook_url: str, status_hook_url: str) -> Dict:
        """
        Gửi yêu cầu xử lý video và file GPX.

        Args:
            video_url (str): URL của video cần xử lý.
            gpx_url (str): URL của file GPX.

        Returns:
            dict: Kết quả trả về từ API.
        """
        endpoint = f"{self.base_url}/process-video-gpx/"
        payload = {"task_id": task_id, "video_url": video_url, "gpx_url": gpx_url, "hook_url": hook_url, "status_hook_url": status_hook_url}
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    # def process_dual_video_gpx(self,task_id: str,  left_video_url: str, right_video_url: str, gpx_url: str, hook_url: str, status_hook_url: str) -> Dict:
    #     """
    #     Gửi yêu cầu xử lý hai video và file GPX.

    #     Args:
    #         left_video_url (str): URL của video bên trái.
    #         right_video_url (str): URL của video bên phải.
    #         gpx_url (str): URL của file GPX.

    #     Returns:
    #         dict: Kết quả trả về từ API.
    #     """
    #     endpoint = f"{self.base_url}/process-dual-video-gpx/"
    #     payload = {
    #         "task_id": task_id, 
    #         "left_video_url": left_video_url,
    #         "right_video_url": right_video_url,
    #         "gpx_url": gpx_url,
            # "status_hook_url": status_hook_url
            # "hook_url": hook_url
    #     }
    #     response = requests.post(endpoint, json=payload)
    #     response.raise_for_status()
    #     return response.json()

    def get_status(self, task_id: str) -> Dict:
        """
        Lấy trạng thái của một tác vụ.

        Args:
            task_id (str): ID của tác vụ cần kiểm tra trạng thái.

        Returns:
            dict: Kết quả trả về từ API.
        """
        endpoint = f"{self.base_url}/status/{task_id}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()

    def download_image(self, image_url: str, output_file: str):
        """
        Tải ảnh từ server.

        Args:
            image_path (str): Đường dẫn của ảnh trên server.
            output_file (str): Đường dẫn lưu file ảnh cục bộ.

        Returns:
            None
        """
        # endpoint = f"{self.base_url}/images/{image_path}"
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def get_stream_by_url(self, url: str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response
    
    def delete_task(self, task_id: str):
        url_delete_task = f"{self.base_url}/delete-result/{task_id}"
        requests.delete(url_delete_task)