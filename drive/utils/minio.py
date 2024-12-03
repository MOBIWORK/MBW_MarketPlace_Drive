from minio import Minio

connect_minio = None

def get_connect_minio(host_url, access_key, secret_key):
    global connect_minio
    if connect_minio is None:
        connect_minio = Minio(host_url, 
            access_key=access_key,
            secret_key=secret_key
        )
    return connect_minio

