import requests
from drive.utils.const import BASE_URL_AI

class PotholeDetectionVelocityAPI:
    def __init__(self, base_url=BASE_URL_AI):
        self.base_url = base_url
    
    def upload_video(self, video_b):
        """
        Uploads a video to the API for pothole detection.

        Parameters:
        - video_binary (binary): Video type binary.

        Returns:
        - dict: The JSON response from the API with detected pothole details.
        """
        url = f"{self.base_url}/process-video"
        files = {"video": video_b}
        response = requests.post(url, files=files)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def upload_video_with_velocity(self, video_b, velocity=7):
        """
        Uploads a video with a specified velocity to the API for pothole detection.

        Parameters:
        - video_binary (binary): Video type binary.
        - velocity (float): Vehicle velocity in m/s.

        Returns:
        - dict: The JSON response from the API with detected pothole details.
        """
        url = f"{self.base_url}/process-velocity"
        files = {"video": video_b}
        data = {"velocity": velocity}
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_image(self, image_url):
        """
        Fetches an image of a detected pothole by its URL.

        Parameters:
        - image_url (str): Full URL of the image to fetch.

        Returns:
        - bytes: The image content in bytes.
        """
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content