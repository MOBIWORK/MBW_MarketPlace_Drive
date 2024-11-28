from drive.api.storage import total_storage_used_by_user, get_max_storage, total_pupv_used_by_user, get_max_pupv

def exist_storage_file(file_lengthy):
    exist_storage = False
    total_size = 0
    total_storage_useds = total_storage_used_by_user()
    if len(total_storage_useds) > 0:
        total_storage_used = total_storage_useds[0]
        total_size = total_storage_used["total_size"]
    max_storage = get_max_storage()
    if (file_lengthy + total_size) <= max_storage["limit"]:
        exist_storage = True
    else:
        exist_storage = False
    return exist_storage

def exist_pupv(pupv):
    exist_pupv = False
    total_pupv = 0
    total_pupv_useds = total_pupv_used_by_user()
    if len(total_pupv_useds) > 0:
        total_pupv_used = total_pupv_useds[0]
        total_pupv = total_pupv_used["total_pupv"]
    max_pupv = get_max_pupv()
    if (pupv + total_pupv) <= max_pupv["limit"]:
        exist_pupv = True
    else:
        exist_pupv = False
    return exist_pupv