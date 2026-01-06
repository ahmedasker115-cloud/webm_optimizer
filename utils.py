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


def sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename by removing problematic characters."""
    # remove path separators and control characters
    invalid = r'<>:"/\\|?*\0'
    cleaned = ''.join(c for c in name if c not in invalid)
    # also strip whitespace at ends
    cleaned = cleaned.strip()
    # fall back to a generic name if empty
    if not cleaned:
        return "file"
    return cleaned
