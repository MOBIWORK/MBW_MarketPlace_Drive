import frappe

BUCKET_NAME = frappe.db.get_single_value("Drive Instance Settings", "aws_bucket")
BASE_URL_AI = "http://deepvision.ekgis.vn:2023/vision/roads/v1"
REDIS_HOST="localhost"
REDIS_PORT=6379