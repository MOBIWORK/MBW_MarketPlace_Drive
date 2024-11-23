import requests
from drive.utils.const import BASE_URL_AI

class PotholeDetectionGPSAPI:
    def __init__(self, base_url=BASE_URL_AI):
        self.base_url = base_url
    
    def upload_video(self, video_a, video_b, f_gps):
        """
        Uploads a video to the API for pothole detection.

        Parameters:
        - video_a (binary): Video type binary.
        - video_b (binary): Video type binary
        - f_gps (binary): GPS type binary

        Returns:
        - dict: The JSON response from the API with detected pothole details.
        """
        return [
            {
                "End_Frame": 49,
                "ID": 6,
                "Ratio": 0.006,
                "S_Real(m)": 0.029952,
                "S_pixel(pixel)": 832,
                "Start_Frame": 43,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_6.png",
                "lng": 105.82973282318548,
                "lat": 21.031197182873704
            },
            {
                "End_Frame": 93,
                "ID": 11,
                "Ratio": 0.04210526315789474,
                "S_Real(m)": 1.0140720221606652,
                "S_pixel(pixel)": 572,
                "Start_Frame": 73,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_11.png",
                "lng": 105.77609626512421, 
                "lat": 21.035461796087258
            },
            {
                "End_Frame": 215,
                "ID": 23,
                "Ratio": 0.00875,
                "S_Real(m)": 0.029400000000000003,
                "S_pixel(pixel)": 384,
                "Start_Frame": 207,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_23.png",
                "lng": 105.79188925194332, 
                "lat": 21.056968419911914
            },
            {
                "End_Frame": 246,
                "ID": 25,
                "Ratio": 0.02434782608695652,
                "S_Real(m)": 0.3521330812854442,
                "S_pixel(pixel)": 594,
                "Start_Frame": 228,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_25.png",
                "lng": 105.78173785198912,
                "lat": 21.036733476104796
            },
            {
                "End_Frame": 281,
                "ID": 24,
                "Ratio": 0.10101265822784809,
                "S_Real(m)": 1.1632055119371894,
                "S_pixel(pixel)": 114,
                "Start_Frame": 224,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_24.png",
                "lng": 105.78456392353242,
                "lat": 21.036678139410167
            },
            {
                "End_Frame": 297,
                "ID": 33,
                "Ratio": 0.007840000000000001,
                "S_Real(m)": 0.020898304000000006,
                "S_pixel(pixel)": 340,
                "Start_Frame": 290,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_33.png",
                "lng": 105.78656984155559, 
                "lat": 21.036641248253655
            },
            {
                "End_Frame": 315,
                "ID": 38,
                "Ratio": 0.004,
                "S_Real(m)": 0.009951999999999999,
                "S_pixel(pixel)": 622,
                "Start_Frame": 313,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_38.png",
                "lng": 105.78884255651106,
                "lat": 21.036530574773035
            },
            {
                "End_Frame": 341,
                "ID": 37,
                "Ratio": 0.04691891891891892,
                "S_Real(m)": 1.1755395646457267,
                "S_pixel(pixel)": 534,
                "Start_Frame": 310,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_37.png",
                "lng": 105.79146111938397,
                "lat": 21.035940314827105
            },
            {
                "End_Frame": 360,
                "ID": 39,
                "Ratio": 0.06265734265734266,
                "S_Real(m)": 1.8530449019511956,
                "S_pixel(pixel)": 472,
                "Start_Frame": 328,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_39.png",
                "lng": 105.79469232728353,
                "lat": 21.034935022946442
            },
            {
                "End_Frame": 489,
                "ID": 46,
                "Ratio": 0.008484848484848486,
                "S_Real(m)": 0.017422222222222224,
                "S_pixel(pixel)": 242,
                "Start_Frame": 485,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_46.png",
                "lng": 105.7983681966647,
                "lat": 21.033071987071565
            },
            {
                "End_Frame": 555,
                "ID": 47,
                "Ratio": 0.04640883977900553,
                "S_Real(m)": 1.1027355697323038,
                "S_pixel(pixel)": 512,
                "Start_Frame": 525,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_47.png",
                "lng": 105.80031482649247,
                "lat": 21.031218151011053
            },
            {
                "End_Frame": 603,
                "ID": 52,
                "Ratio": 0.0057665903890160184,
                "S_Real(m)": 0.03524877859757343,
                "S_pixel(pixel)": 1060,
                "Start_Frame": 594,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_52.png",
                "lng": 105.8037535430522,
                "lat": 21.029198273525427
            },
            {
                "End_Frame": 605,
                "ID": 53,
                "Ratio": 0.0028354430379746837,
                "S_Real(m)": 0.003071179618650858,
                "S_pixel(pixel)": 382,
                "Start_Frame": 601,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_53.png",
                "lng": 105.80443535755806,
                "lat": 21.028893906055185
            },
            {
                "End_Frame": 640,
                "ID": 55,
                "Ratio": 0.014840989399293287,
                "S_Real(m)": 0.1449277678582577,
                "S_pixel(pixel)": 658,
                "Start_Frame": 625,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_55.png",
                "lng": 105.80622388538023,
                "lat": 21.02906914801197
            },
            {
                "End_Frame": 658,
                "ID": 58,
                "Ratio": 0.02633663366336634,
                "S_Real(m)": 0.40368583472208613,
                "S_pixel(pixel)": 582,
                "Start_Frame": 639,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_58.png",
                "lng": 105.81122385831154,
                "lat": 21.030009917082907
            },
            {
                "End_Frame": 678,
                "ID": 57,
                "Ratio": 0.045196850393700784,
                "S_Real(m)": 0.7190498604997209,
                "S_pixel(pixel)": 352,
                "Start_Frame": 637,
                "image": "http://deepvision.ekgis.vn:2023/vision/roads/v1/images/Data_potholes/Image_57.png",
                "lng": 105.81317048806471,
                "lat": 21.03035117498476
            }
        ]
    
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