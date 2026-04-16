import requests
from fastapi import APIRouter, Depends, HTTPException, Request


async def proxy(request: Request, url: str):
    # Lấy toàn bộ headers từ request gốc
    incoming_headers = dict(request.headers)

    # (Tuỳ chọn) Xoá những header không nên chuyển tiếp
    incoming_headers.pop('host', None)

    # Lấy body
    body = await request.body()

    # Gửi request mới đến một URL khác
    response = requests.post(
        url=url,
        headers=incoming_headers,
        data=body
    )

    return {
        "status_code": response.status_code,
        "response_text": response.text,
    }


async def json_proxy(request: Request, url: str):
    # 1. Lấy JSON body từ request gốc
    json_body = await request.json()

    # 2. Lấy headers và loại bỏ những header không nên forward
    headers = dict(request.headers)
    headers.pop("host", None)
    headers["Content-Type"] = "application/json"  # đảm bảo kiểu JSON

    # 3. Gửi request mới với JSON
    response = requests.post(
        url=url,  # Thay URL mục tiêu tại đây
        headers=headers,
        json=json_body,
        timeout=5
    )

    # 4. Trả về phản hồi từ server target
    return {
        "status_code": response.status_code,
        "response_text": response.text
    }
