import os


def ensure_folder(folder_path):
    """تأكد أن الفولدر موجود، لو مش موجود انشئه"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def mb_to_bytes(mb):
    """تحويل ميجا بايت إلى بايت"""
    return mb * 1024 * 1024


def format_size(bytes_size):
    """تحويل البايت لميجا و صياغة نصية"""
    return f"{bytes_size / (1024*1024):.2f} MB"
