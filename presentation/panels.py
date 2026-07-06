from dash import html
from config.app_config import AppConfig


#---------------------------
# BUILDING STATS PANEL
#---------------------------
def build_stats(sim):
    
    total_cooling = sim.total_reduction()

    # Calculate total cooling per intervention type
    type_cooling = {"tree": 0.0, "greenroof": 0.0, "leaves": 0.0}
    for iv in sim.interventions:
        type_cooling[iv["type"]] += iv["cooling_effect"]

    # Intervention types
    intervention_types = [
        ("/assets/images/tree.png", "tree"),
        ("/assets/images/greenroof.png", "greenroof"),
        ("/assets/images/leaves.png", "leaves"),
    ]

    # Add stats information about each intervention type
    stats_item = []
    for icon, name in intervention_types:
        info = AppConfig.INTERVENTION_META[name]
        row = html.Div(
            className="stats-row",
            children=[
                html.Span(
                    [html.Img(src=icon, className="stats-row-icon"), info["label"]],
                    className="stats-row-label",
                ),
                html.Span(
                    "\u2212" + str(round(type_cooling[name], 3)) + "\u00b0C",
                    className="stats-row-count stats-row-count-" + name,
                ),
            ],
        )
        stats_item.append(row)

    # Put it all together in one card
    card = html.Div(
        className="stats-card",
        children=[
            html.Div(
                className="stats-total",
                children=[
                    html.Span("\u2212" + str(round(total_cooling, 3)), className="stats-value"),
                    html.Span(" \u00b0C cooled", className="stats-label"),
                ],
            ),
            html.Hr(className="stats-divider"),
        ] + stats_item,
    )

    return [card]


#------------------------------
# BUILDING Details Modal
#------------------------------
def build_modal(block_summary):
  
    if block_summary is None:
        return []

    content = []

    # --- Block ID ---
    content.append(html.Div("Block ID: " + str(block_summary["block_id"]), className="modal-building-id"))

    # --- Temperature Section ---
    content.append(html.Div("Temperature", className="modal-section-label"))
    content.append(_modal_row("Current Temperature", str(round(block_summary["current_temp"], 1)) + "\u00b0C"))
    content.append(_modal_row("Baseline Temperature", str(round(block_summary["base_temp"], 1)) + "\u00b0C"))

    # --- Cooling effect ---
    content.append(_modal_row("Cooling Effect", "\u2212" + str(round(block_summary["reduction"], 3)) + "\u00b0C"))

    # --- Footprint Area if available ---
    if block_summary.get("area_m2"):
        content.append(_modal_row("Footprint Area", str(round(block_summary["area_m2"])) + " m\u00b2"))

    # --- Interventions Section ---
    content.append(html.Div("Interventions", className="modal-section-label"))

    if block_summary["interventions"]:
        for iv in block_summary["interventions"]:
            info = AppConfig.INTERVENTION_META[iv["type"]]
            cooling = "\u2212" + str(round(iv["cooling_effect"], 3)) + "\u00b0C"
            content.append(html.Div(
                className="modal-intervention-row",
                children=[
                    html.Span(
                        [html.Img(src=info["icon"], className="modal-intervention-icon"), info["label"]],
                        className="modal-intervention-name",
                    ),
                    html.Span(cooling, className="modal-intervention-delta"),
                ],
            ))

    else:
        content.append(html.Div("No interventions placed yet", className="modal-no-interventions"))

    return content


#------------------------
# CREATE MODAL ROW
#------------------------
def _modal_row(label, value):
    return html.Div(
        className="modal-row",
        children=[
            html.Span(label, className="modal-row-label"),
            html.Span(value, className="modal-row-value"),
        ],
    )


#---------------------------
# VALIDATION RESULTS PANEL
#---------------------------
def build_validation_results(validation_output):
    """Build the HTML for the validation results modal."""

    results = validation_output["results"]
    mse = validation_output["mse"]
    total_cases = validation_output["total_cases"]

    # Handle no interventions case
    if total_cases == 0:
        msg = validation_output.get("status", "No cases to validate")
        return [
            html.Div("VALIDATION RESULTS", className="modal-building-name"),
            html.Hr(className="modal-divider"),
            html.Div(msg, className="modal-section-label"),
        ]

    # Compute aggregate stats
    avg_expected = sum(r["expected_temp"] for r in results) / total_cases
    avg_simulated = sum(r["simulated_temp"] for r in results) / total_cases
    avg_error = sum(r["error"] for r in results) / total_cases

    return [
        html.Div("VALIDATION RESULTS", className="modal-building-name"),
        html.Div(str(total_cases) + " blocks validated", className="modal-building-id"),
        html.Hr(className="modal-divider"),
        html.Div("Expected (Avg)", className="modal-section-label"),
        html.Div("{:.3g}\u00b0C".format(avg_expected), className="modal-building-name"),
        html.Hr(className="modal-divider"),
        html.Div("Simulated (Avg)", className="modal-section-label"),
        html.Div("{:.3g}\u00b0C".format(avg_simulated), className="modal-building-name"),
        html.Hr(className="modal-divider"),
        html.Div("Error (Avg)", className="modal-section-label"),
        html.Div("{:.3g}\u00b0C".format(avg_error), className="modal-building-name"),
        html.Hr(className="modal-divider"),
        html.Div("Mean Squared Error (MSE)", className="modal-section-label"),
        html.Div("{:.3g}".format(mse), className="modal-building-name", style={"color": "#fff"}),
    ]


#---------------------------
# CONSISTENCY TABLE
#---------------------------
def build_consistency_table(gdf):
    """Build a table showing 2022 vs 2023 vs 2024 base temps and Avg Diff."""

    rows = []
    blocks = gdf[["block_id", "base_temp_2022", "base_temp_2023", "base_temp_2024"]].drop_duplicates()
    blocks = blocks.sort_values("block_id")

    rows.append(html.Div(
        className="modal-row",
        children=[
            html.Span("Block", className="modal-row-label"),
            html.Span("2022", className="modal-row-value"),
            html.Span("2023", className="modal-row-value"),
            html.Span("2024", className="modal-row-value"),
            html.Span("Avg Diff", className="modal-row-value"),
        ],
    ))
    rows.append(html.Hr(className="modal-divider"))

    for _, row in blocks.iterrows():
        t22 = float(row["base_temp_2022"])
        t23 = float(row["base_temp_2023"])
        t24 = float(row["base_temp_2024"])
        avg_diff = (abs(t23 - t22) + abs(t24 - t23)) / 2

        rows.append(html.Div(
            className="modal-row",
            children=[
                html.Span(str(int(row["block_id"])), className="modal-row-label"),
                html.Span("{:.3g}".format(t22), className="modal-row-value"),
                html.Span("{:.3g}".format(t23), className="modal-row-value"),
                html.Span("{:.3g}".format(t24), className="modal-row-value"),
                html.Span("{:.3g}".format(avg_diff), className="modal-row-value"),
            ],
        ))

    return [
        html.Div("DATA CONSISTENCY CHECK", className="modal-building-name"),
        html.Hr(className="modal-divider"),
    ] + rows
