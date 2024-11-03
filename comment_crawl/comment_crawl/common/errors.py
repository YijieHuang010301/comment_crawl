class BaseError(Exception):
    """自定义错误的基类"""
    def __init__(self, message="发生了一个错误"):
        self.message = message
        super().__init__(self.message)

class InnerIpError(BaseError):
    def __init__(self, message="cannot find inner ip"):
        super().__init__(message)

class UploadFileOpenError(BaseError):
    def __init__(self, message="open upload file error"):
        super().__init__(message)

class UploadFileCheckError(BaseError):
    def __init__(self, message="upload file check error"):
        super().__init__(message)

class SaveRowFailedError(BaseError):
    def __init__(self, message="save the row failed"):
        super().__init__(message)

class ExecQueryError(BaseError):
    def __init__(self, message="execute query error"):
        super().__init__(message)