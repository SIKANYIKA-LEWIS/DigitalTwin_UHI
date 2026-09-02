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
    total_cases = validation_output["total_cases"]
    coefficient_results = validation_output["coefficient_results"]
    quantity_results = validation_output["quantity_results"]
    performance_results = validation_output["performance_results"]

    content = []

    # Keep the live result at the top so it is the first table users see.
    content += [
         html.H5(
             [
                 "Current Simulation Validation ",
                 html.Span(
                     "LIVE",
                     className="badge rounded-pill ms-2",
                     style={
                         "backgroundColor": "#20c997",
                         "color": "#071b16",
                         "fontSize": "11px",
                         "letterSpacing": "1px",
                         "verticalAlign": "middle",
                     },
                 ),
             ],
             className="text-white mb-2",
             style={"borderLeft": "4px solid #20c997", "paddingLeft": "10px"},
         ),
         html.Div(
             "This table uses the interventions currently placed on the map.",
             className="mb-3 px-3 py-2 rounded",
             style={
                 "color": "#123c32",
                 "backgroundColor": "#d1e7dd",
                 "fontWeight": "600",
             },
         ),
    ]

    if total_cases == 0:
        msg = validation_output.get("status", "No cases to validate")
        content.append(html.Div(msg, className="text-white"))
    else:
        rmse = (sum(r["squared_error"] for r in results) / total_cases) ** 0.5
        content += [
            _build_current_simulation_table(results),
            html.Div(
                "Overall RMSE: {:.4f} °C across {} active block(s).".format(rmse, total_cases),
                className="text-white fw-bold text-center mt-3",
            ),
            html.H6("Conclusion", className="text-white fw-bold text-center mt-4 mb-2"),
            _build_rmse_conclusion(rmse),
        ]

    content += [
        html.Div(
            [
                html.Hr(className="text-secondary my-3"),
                html.Div(
                    "REFERENCE TABLES",
                    className="text-center fw-bold rounded py-2",
                    style={
                        "color": "#343a40",
                        "backgroundColor": "#f1f3f5",
                        "letterSpacing": "2px",
                        "fontSize": "13px",
                    },
                ),
            ],
            className="mt-4 mb-3",
        ),
        html.Div(
            [
                "RMSE shows, in °C, how closely the system’s simulated temperatures are to the temperatures calculated using literature coefficients, where a lower value means better agreement.",
                html.Br(),
                "Formula: RMSE = √[Σ(Simulated Temperature − Literature Temperature)² ÷ Number of Blocks]",
            ],
            className="text-center fw-bold mb-3",
            style={
                "color": "#111",
                "background": "#f1f3f5",
                "border": "2px solid #111",
                "borderRadius": "8px",
                "padding": "14px",
                "fontSize": "17px",
            },
        ),
        _build_rmse_key(),
        html.H5("Reference Table 1: Intervention Coefficient", className="text-white mt-2 mb-2"),
        _build_coefficient_table(coefficient_results),
        html.H5("Reference Table 2: Intervention Validation", className="text-white mt-4 mb-2"),
        _build_quantity_table(quantity_results),
        html.H5("Reference Table 3: Intervention Performance Comparison", className="text-white mt-4 mb-2"),
        _build_performance_table(performance_results),
    ]

    return content


def _build_current_simulation_table(results):
    """Render values from the interventions currently in the simulation."""
    rows = []
    for result in results:
        error_color = "#20c997" if abs(result["error"]) <= 0.5 else "#ffc107" if abs(result["error"]) <= 1 else "#ff6b6b"
        rows.append(html.Tr([
            html.Td(str(result["block_id"]), className="fw-bold"),
            html.Td(
                html.Span(
                    result["interventions"],
                    className="badge",
                    style={"backgroundColor": "#145c4a", "color": "#d8fff4", "fontSize": "13px"},
                )
            ),
            html.Td("{:.2f} °C".format(result["base_temp"])),
            html.Td("{:.2f} °C".format(result["expected_temp"])),
            html.Td(
                "{:.2f} °C".format(result["simulated_temp"]),
                style={"backgroundColor": "#123f38", "color": "#8ff5d5", "fontWeight": "700"},
            ),
            html.Td(
                "{:.2f} °C".format(result["base_temp"] - result["simulated_temp"]),
                style={"color": "#20c997", "fontWeight": "700"},
            ),
            html.Td(
                "{:.4f} °C".format(result["error"]),
                style={"color": error_color, "fontWeight": "700"},
            ),
        ]))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Block"),
            html.Th("Active Interventions"),
            html.Th("Baseline"),
            html.Th("Expected Literature"),
            html.Th("Current Simulated"),
            html.Th("Actual Reduction"),
            html.Th("Error"),
        ])),
        html.Tbody(rows),
    ], className="table validation-table table-bordered table-lg text-center mb-0", style={
        "fontSize": "16px",
        "verticalAlign": "middle",
        "borderColor": "#20c997",
        "boxShadow": "0 0 12px rgba(32, 201, 151, 0.18)",
    })

    return html.Div(table, className="table-responsive")


#---------------------------------------
# BUILD COEFFICIENT TABLE
#---------------------------------------
def _build_coefficient_table(coefficient_results):

    header = html.Thead(html.Tr([
        html.Th("Intervention"),
        html.Th("Literature Coefficient"),
        html.Th("System Coefficient"),
        html.Th("Coefficient RMSE"),
    ]))

    rows = []
    for result in coefficient_results:
        rows.append(html.Tr([
            html.Td(result["name"]),
            html.Td("{:.4f} °C/m²".format(result["literature"])),
            html.Td("{:.4f} °C/m²".format(result["system"])),
            html.Td("{:.4f} °C/m²".format(result["rmse"])),
        ]))

    return html.Div(
        html.Table(
            [header, html.Tbody(rows)],
            className="table validation-table table-bordered table-lg text-center mb-0",
            style={"fontSize": "17px", "verticalAlign": "middle"},
        ),
        className="table-responsive",
    )


#---------------------------------------
# BUILD QUANTITY VALIDATION TABLE
#---------------------------------------
def _build_quantity_table(quantity_results):

    first_header = [html.Th("Quantity", rowSpan=2)]
    second_header = []

    for intervention in quantity_results:
        first_header.append(html.Th(intervention["name"], colSpan=3, className="text-center"))
        second_header += [
            html.Th("Simulated (°C)"),
            html.Th("Synthetic (°C)"),
            html.Th("RMSE"),
        ]

    rows = []
    for row_number in range(5):
        row = [html.Td(str(row_number + 1), className="fw-bold")]

        for intervention in quantity_results:
            result = intervention["results"][row_number]
            row += [
                html.Td("{:.2f} °C".format(result["simulated"])),
                html.Td("{:.2f} °C".format(result["synthetic"])),
                html.Td("{:.4f}".format(result["rmse"])),
            ]

        rows.append(html.Tr(row))

    table = html.Table([
        html.Thead([
            html.Tr(first_header),
            html.Tr(second_header),
        ]),
        html.Tbody(rows),
    ],
        className="table validation-table table-bordered table-lg text-center mb-0",
        style={"fontSize": "16px", "verticalAlign": "middle"},
    )

    return html.Div(table, className="table-responsive")


#---------------------------------------
# BUILD PERFORMANCE COMPARISON TABLE
#---------------------------------------
def _build_performance_table(performance_results):

    header = html.Thead(html.Tr([
        html.Th("Intervention"),
        html.Th("Base Temperature"),
        html.Th("Average Simulated Temperature"),
        html.Th("Temperature Reduction"),
    ]))

    rows = []
    for result in performance_results:
        rows.append(html.Tr([
            html.Td(result["name"], className="fw-bold"),
            html.Td("{:.2f} °C".format(result["base_temperature"])),
            html.Td("{:.2f} °C".format(result["simulated_temperature"])),
            html.Td("{:.2f} °C".format(result["temperature_reduction"])),
        ]))

    return html.Div(
        html.Table(
            [header, html.Tbody(rows)],
            className="table validation-table table-bordered table-lg text-center mb-0",
            style={"fontSize": "16px", "verticalAlign": "middle"},
        ),
        className="table-responsive",
    )


#---------------------------------------
# BUILD RMSE CONCLUSION
#---------------------------------------
def _build_rmse_conclusion(rmse):

    if rmse <= 0.50:
        conclusion = "The RMSE is low, indicating that the simulated results closely agree with the literature results."
    elif rmse <= 1.00:
        conclusion = "The RMSE is moderate, indicating reasonable agreement with the literature results."
    else:
        conclusion = "The RMSE is high, indicating poor agreement with the literature results."

    return html.Div(
        conclusion,
        className="text-center fw-bold mb-3",
        style={
            "color": "#111",
            "background": "#f1f3f5",
            "border": "2px solid #111",
            "borderRadius": "8px",
            "padding": "14px",
            "fontSize": "17px",
        },
    )


#---------------------------------------
# BUILD RMSE KEY
#---------------------------------------
def _build_rmse_key():

    return html.Div(
        [
            html.Div("RMSE KEY", className="fw-bold text-center mb-2"),
            html.Div(
                [
                    html.Span("LOW: 0.00–0.50°C", style={"background": "#fff", "color": "#111", "border": "2px solid #111", "padding": "6px 12px", "borderRadius": "5px", "fontWeight": "700"}),
                    html.Span("MODERATE: 0.51–1.00°C", style={"background": "#fff", "color": "#111", "border": "2px solid #111", "padding": "6px 12px", "borderRadius": "5px", "fontWeight": "700"}),
                    html.Span("HIGH: ABOVE 1.00°C", style={"background": "#fff", "color": "#111", "border": "2px solid #111", "padding": "6px 12px", "borderRadius": "5px", "fontWeight": "700"}),
                ],
                className="d-flex justify-content-center gap-3 flex-wrap",
            ),
        ],
        className="text-center mb-3",
        style={"color": "#111"},
    )
