"""Manager analytics charts rendered as Telegram-ready PNG images."""

from datetime import date
from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def build_manager_analytics_chart(payload):
    districts = payload.get("districts", [])
    if not districts:
        return None

    top = districts
    labels = [item["district"] for item in top]

    figure, axes = plt.subplots(
        2, 2, figsize=(max(13, len(top) * 1.2), 9), constrained_layout=True
    )
    figure.suptitle(
        f"Manager Analytics — {payload['npo']} — {payload['days']} hari",
        fontsize=14,
        fontweight="bold",
    )

    volume_axis = axes[0, 0]
    active = [item["active_tickets"] for item in top]
    closed = [item["closed_tickets"] for item in top]
    positions = list(range(len(top)))
    volume_axis.bar(positions, active, label="Active", color="#f59e0b")
    volume_axis.bar(positions, closed, bottom=active, label="Closed", color="#16a34a")
    volume_axis.set_xticks(positions, labels, rotation=30, ha="right")
    volume_axis.set_title("Total tickets: active vs closed")
    volume_axis.set_ylabel("Tickets")
    volume_axis.legend(fontsize=8)
    volume_axis.grid(axis="y", alpha=0.25)

    rca_axis = axes[0, 1]
    rca_axis.bar(labels, [item["rca_completed"] for item in top], color="#2563eb")
    rca_axis.set_title("Tickets RCA-completed")
    rca_axis.set_ylabel("Tickets")
    rca_axis.tick_params(axis="x", rotation=30)
    rca_axis.grid(axis="y", alpha=0.25)

    service_axis = axes[1, 0]
    service_axis.bar(labels, [item["service_completed"] for item in top], color="#7c3aed")
    service_axis.set_title("Tickets service-completed")
    service_axis.set_ylabel("Tickets")
    service_axis.tick_params(axis="x", rotation=30)
    service_axis.grid(axis="y", alpha=0.25)

    response_axis = axes[1, 1]
    x_positions = list(range(len(top)))
    rca_response = [item["avg_rca_response_days"] or 0 for item in top]
    service_response = [item["avg_service_response_days"] or 0 for item in top]
    width = 0.36
    response_axis.bar(
        [x - width / 2 for x in x_positions], rca_response, width, label="RCA response", color="#2563eb"
    )
    response_axis.bar(
        [x + width / 2 for x in x_positions], service_response, width, label="Service response", color="#7c3aed"
    )
    response_axis.set_xticks(x_positions, labels, rotation=30, ha="right")
    response_axis.set_title("Response time comparison")
    response_axis.set_ylabel("Average days")
    response_axis.legend(fontsize=8)
    response_axis.grid(axis="y", alpha=0.25)
    figure.autofmt_xdate()

    output = BytesIO()
    figure.savefig(output, format="png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    output.seek(0)
    return output
