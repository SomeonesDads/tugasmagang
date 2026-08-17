"""Async client used by Telegram handlers to talk to the FastAPI API."""

from config import API_BASE_URL


class BackendAPIError(Exception):
    """User-safe error returned by the backend integration."""


async def _request(method, path, **kwargs):
    try:
        import httpx
    except ImportError as exc:
        raise BackendAPIError("Klien backend belum terpasang. Install dependensi bot terlebih dahulu.") from exc

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
        if "RCA" in str(detail) or "rca" in str(detail):
            raise BackendAPIError("RCA untuk tiket ini sudah dikirim.")
        raise BackendAPIError(str(detail))
    if response.status_code == 404:
        raise BackendAPIError(str(detail))
    if response.status_code == 422:
        raise BackendAPIError(f"Data RCA tidak valid: {detail}")
    raise BackendAPIError("Backend gagal memproses permintaan. Coba lagi.")


async def get_tickets(telegram_id, district_id=None, as_role=None, page=1, page_size=10):
    params = {key: value for key, value in {
        "district_id": district_id,
        "as_role": as_role,
        "page": page,
        "page_size": page_size,
    }.items() if value is not None}
    return await _request("GET", f"/tickets/{telegram_id}", params=params)


async def get_ticket_history(
    telegram_id, status="all", district_id=None, as_role=None, site_id=None,
    ticket_type=None, rca_id=None, created_from=None, created_to=None,
    search=None, page=1, page_size=10, sort="created_date", order="desc",
):
    values = {
        "status": status, "district_id": district_id, "as_role": as_role,
        "site_id": site_id, "ticket_type": ticket_type, "rca_id": rca_id,
        "created_from": created_from, "created_to": created_to,
        "search": search, "page": page, "page_size": page_size,
        "sort": sort, "order": order,
    }
    return await _request(
        "GET", f"/tickets/{telegram_id}/history",
        params={key: value for key, value in values.items() if value is not None},
    )


async def get_ticket_history_detail(telegram_id, ticket_id, district_id=None, as_role=None):
    values = {"district_id": district_id, "as_role": as_role}
    return await _request(
        "GET", f"/tickets/{telegram_id}/history/{ticket_id}",
        params={key: value for key, value in values.items() if value is not None},
    )


async def get_identity(telegram_id):
    return await _request("GET", f"/identity/{telegram_id}")


async def get_management_recap(telegram_id, district_id=None):
    return await _request("GET", f"/management/recap/{telegram_id}", params={"district_id": district_id} if district_id else {})


async def get_management_districts(telegram_id, npo=None):
    return await _request(
        "GET",
        f"/management/recap/{telegram_id}/districts",
        params={"district_id": npo} if npo else {},
    )


async def get_management_analytics(telegram_id, npo=None, days=30, as_role=None):
    params = {"days": days}
    if npo:
        params["district_id"] = npo
    if as_role:
        params["as_role"] = as_role
    return await _request(
        "GET",
        f"/management/analytics/{telegram_id}",
        params=params,
    )


async def get_master_analytics(telegram_id, npo=None, days=30):
    params = {"days": days}
    if npo:
        params["npo"] = npo
    return await _request("GET", f"/master/analytics/{telegram_id}", params=params)


async def get_management_details(telegram_id, district_id=None):
    return await _request("GET", f"/management/recap/{telegram_id}/details", params={"district_id": district_id} if district_id else {})


async def get_management_sites(telegram_id, district_id=None):
    return await _request("GET", f"/management/recap/{telegram_id}/sites", params={"district_id": district_id} if district_id else {})


async def get_management_site_recap(telegram_id, site_id, district_id=None):
    return await _request("GET", f"/management/recap/{telegram_id}/sites/{site_id}", params={"district_id": district_id} if district_id else {})


async def get_management_site_details(telegram_id, site_id, district_id=None):
    return await _request("GET", f"/management/recap/{telegram_id}/sites/{site_id}/details", params={"district_id": district_id} if district_id else {})


async def get_engineers():
    return await _request("GET", "/engineers")


async def get_rca_options():
    return await _request("GET", "/rca-options")


async def submit_rca(ticket_id, rca, rca_detail):
    return await _request("PATCH", f"/tickets/{ticket_id}", json={"rca": rca, "rca_detail": rca_detail})
