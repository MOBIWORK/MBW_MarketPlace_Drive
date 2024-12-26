import requests

def calculate_content_length(url: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_length = 0
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            total_length += len(chunk)
    return total_length