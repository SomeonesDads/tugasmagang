"""Async client used by Telegram handlers to talk to the FastAPI API."""

import httpx

from config import API_BASE_URL


class BackendAPIError(Exception):
    """User-safe error returned by the backend integration."""


async def _request(method, path, **kwargs):
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15.0) as client:
            response = await client.request(method, path, **kwargs)
    except httpx.RequestError as exc:
        raise BackendAPIError("Backend tidak dapat dihubungi. Coba lagi beberapa saat.") from exc

    if response.is_success:
        return response.json()

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    if response.status_code == 409:
        raise BackendAPIError("RCA untuk tiket ini sudah dikirim.")
    if response.status_code == 404:
        raise BackendAPIError("Tiket tidak ditemukan atau sudah tidak tersedia.")
    if response.status_code == 422:
        raise BackendAPIError(f"Data RCA tidak valid: {detail}")
    raise BackendAPIError("Backend gagal memproses permintaan. Coba lagi.")


async def get_tickets(district):
    return await _request("GET", f"/tickets/{district}")


async def get_engineers():
    return await _request("GET", "/engineers")


async def get_mock_engineer_tickets(telegram_id):
    return await _request("GET", f"/mock/engineers/{telegram_id}/tickets")


async def get_rca_options():
    return await _request("GET", "/rca-options")


async def submit_rca(ticket_id, rca, rca_detail):
    return await _request("PATCH", f"/tickets/{ticket_id}", json={"rca": rca, "rca_detail": rca_detail})
