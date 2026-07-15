from dash import html
from config.app_config import AppConfig


def build_stats(sim):

    total_cooling = sim.total_reduction()

    type_cooling = {"tree": 0.0, "greenroof": 0.0, "leaves": 0.0}
    for iv in sim.interventions:
        type_cooling[iv["type"]] += iv["cooling_effect"]

    intervention_types = [
        ("/assets/images/tree.png", "tree"),
        ("/assets/images/greenroof.png", "greenroof"),
        ("/assets/images/leaves.png", "leaves"),
    ]

    stats_item = []
    for icon, name in intervention_types:
        info = AppConfig.INTERVENTION_META[name]
        row = html.Div(
            className="d-flex justify-content-between align-items-center py-2",
            children=[
                html.Span(
                    [html.Img(src=icon, className="stats-row-icon me-2"), info["label"]],
                    className="text-white",
                ),
                html.Span(
                    "−" + str(round(type_cooling[name], 3)) + "°C",
                    className="fw-semibold text-white",
                ),
            ],
        )
        stats_item.append(row)

    card = html.Div(
        className="card bg-dark bg-opacity-75 border-secondary p-3 mb-2",
        children=[
            html.Div(
                className="d-flex align-items-baseline",
                children=[
                    html.Span("−" + str(round(total_cooling, 3)), className="text-white fw-bold", style={"fontSize": "36px"}),
                    html.Span(" °C cooled", className="text-white ms-1"),
                ],
            ),
            html.Hr(className="text-secondary my-2"),
        ] + stats_item,
    )

    return [card]


def build_modal(block_summary):

    if block_summary is None:
        return []

    content = []

    content.append(html.Div("Block ID: " + str(block_summary["block_id"]), className="text-white mb-3"))

    content.append(html.Div("Temperature", className="fw-bold text-uppercase small mt-3 mb-2 text-white", style={"letterSpacing": "2px"}))
    content.append(_modal_row("Current Temperature", str(round(block_summary["current_temp"], 1)) + "°C"))
    content.append(_modal_row("Baseline Temperature", str(round(block_summary["base_temp"], 1)) + "°C"))

    content.append(_modal_row("Cooling Effect", "−" + str(round(block_summary["reduction"], 3)) + "°C"))

    if block_summary.get("area_m2"):
        content.append(_modal_row("Footprint Area", str(round(block_summary["area_m2"])) + " m²"))

    content.append(html.Div("Interventions", className="fw-bold text-uppercase small mt-3 mb-2 text-white", style={"letterSpacing": "2px"}))

    if block_summary["interventions"]:
        for iv in block_summary["interventions"]:
            info = AppConfig.INTERVENTION_META[iv["type"]]
            cooling = "−" + str(round(iv["cooling_effect"], 3)) + "°C"
            content.append(html.Div(
                className="d-flex justify-content-between align-items-center py-2",
                children=[
                    html.Span(
                        [html.Img(src=info["icon"], className="modal-intervention-icon me-2"), info["label"]],
                        className="fw-semibold text-white",
                    ),
                    html.Span(cooling, className="fw-bold text-white"),
                ],
            ))
    else:
        content.append(html.Div("No interventions placed yet", className="text-white fst-italic py-2"))

    return content


def _modal_row(label, value):
    return html.Div(
        className="d-flex justify-content-between align-items-center py-2 border-bottom border-secondary",
        children=[
            html.Span(label, className="fw-bold text-white"),
            html.Span(value, className="fw-bold text-white"),
        ],
    )


def build_validation_results(validation_output):

    results = validation_output["results"]
    mse = validation_output["mse"]
    total_cases = validation_output["total_cases"]

    if total_cases == 0:
        msg = validation_output.get("status", "No cases to validate")
        return [
            html.Div(msg, className="text-white"),
        ]

    avg_expected = sum(r["expected_temp"] for r in results) / total_cases
    avg_simulated = sum(r["simulated_temp"] for r in results) / total_cases
    avg_error = sum(r["error"] for r in results) / total_cases

    return [
        html.Div(str(total_cases) + " blocks validated", className="text-white mb-3"),
        html.Hr(className="text-secondary"),
        html.Div("Expected (Avg)", className="fw-bold text-uppercase small mt-2 mb-1 text-white", style={"letterSpacing": "2px"}),
        html.Div("{:.3g}°C".format(avg_expected), className="text-white", style={"fontSize": "24px"}),
        html.Hr(className="text-secondary"),
        html.Div("Simulated (Avg)", className="fw-bold text-uppercase small mt-2 mb-1 text-white", style={"letterSpacing": "2px"}),
        html.Div("{:.3g}°C".format(avg_simulated), className="text-white", style={"fontSize": "24px"}),
        html.Hr(className="text-secondary"),
        html.Div("Error (Avg)", className="fw-bold text-uppercase small mt-2 mb-1 text-white", style={"letterSpacing": "2px"}),
        html.Div("{:.3g}°C".format(avg_error), className="text-white", style={"fontSize": "24px"}),
        html.Hr(className="text-secondary"),
        html.Div("Mean Squared Error (MSE)", className="fw-bold text-uppercase small mt-2 mb-1 text-white", style={"letterSpacing": "2px"}),
        html.Div("{:.3g}".format(mse), className="text-white", style={"fontSize": "24px"}),
    ]


def build_consistency_table(gdf):

    rows = []
    blocks = gdf[["block_id", "base_temp_2022", "base_temp_2023", "base_temp_2024"]].drop_duplicates()
    blocks = blocks.sort_values("block_id")

    rows.append(html.Div(
        className="d-flex justify-content-between align-items-center py-2 border-bottom border-secondary fw-bold text-white",
        children=[
            html.Span("Block", className="flex-fill"),
            html.Span("2022", className="flex-fill text-center"),
            html.Span("2023", className="flex-fill text-center"),
            html.Span("2024", className="flex-fill text-center"),
            html.Span("Avg Diff", className="flex-fill text-end"),
        ],
    ))

    for _, row in blocks.iterrows():
        t22 = float(row["base_temp_2022"])
        t23 = float(row["base_temp_2023"])
        t24 = float(row["base_temp_2024"])
        avg_diff = (abs(t23 - t22) + abs(t24 - t23)) / 2

        rows.append(html.Div(
            className="d-flex justify-content-between align-items-center py-2 text-white",
            children=[
                html.Span(str(int(row["block_id"])), className="flex-fill fw-bold"),
                html.Span("{:.3g}".format(t22), className="flex-fill text-center"),
                html.Span("{:.3g}".format(t23), className="flex-fill text-center"),
                html.Span("{:.3g}".format(t24), className="flex-fill text-center"),
                html.Span("{:.3g}".format(avg_diff), className="flex-fill text-end"),
            ],
        ))

    return rows
