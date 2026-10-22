"""match...case 模式匹配（Python 3.10+ 新增）

运行：python match_case.py  (需要 Python >= 3.10)
"""


def http_status(status):
    """match 后的对象会依次与 case 匹配，_ 匹配一切"""
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Internal Server Error"
        case _:
            return "Unknown"


if __name__ == "__main__":
    print(http_status(200))
    print(http_status(404))
    print(http_status(500))
    print(http_status(999))