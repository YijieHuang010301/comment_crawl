import hashlib
import json

HEX_OUTPUT = 0
BINARY_OUTPUT = 1

def get_hash(data, output_format=0, hash_type='md5'):
    """
    生成指定类型的哈希值.

    参数:
    - data: 待哈希的数据，可以是字符串、字典、列表或整数。
    - output_format: 返回哈希值的格式，0 表示返回十六进制字符串，1 表示返回二进制数据。
    - hash_type: 使用的哈希算法，默认为 'md5'，支持 'sha1', 'sha256', 'sha384', 'sha512' 等。

    返回:
    - 哈希值，根据 c_type 返回不同格式。
    """
    hash_type = hash_type.lower()

    # Convert data types to string before hashing
    if isinstance(data, (dict, list)):
        data = json.dumps(data)
    elif isinstance(data, int):
        data = str(data)
    elif isinstance(data, str):
        data = data.encode("utf-8")

    # Mapping hash_type to appropriate hashlib function
    hash_funcs = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha-1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha-256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha-384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'sha-512': hashlib.sha512
    }

    # Get hash function based on hash_type
    md = hash_funcs.get(hash_type, hashlib.md5)()

    # Update hash with data
    md.update(data)

    # Return based on c_type
    if output_format == HEX_OUTPUT:
        return md.hexdigest()  # Hexadecimal string
    elif output_format == BINARY_OUTPUT:
        return md.digest()  # Raw binary data
