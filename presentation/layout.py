import dash_bootstrap_components as dbc
import dash_deck
from dash import dcc, html
from presentation import map_builder
from presentation import panels


def build_layout(sim):

    initial_stats = panels.build_stats(sim)

    return html.Div(
        className="d-flex vh-100 overflow-hidden",
        children=[

            # LEFT SIDEBAR
            html.Div(
                className="sidebar d-flex flex-column",
                children=[

                    # Sidebar header
                    html.Div(
                        className="text-center p-3 border-bottom border-secondary",
                        children=[
                            html.Div("DIGITAL TWIN UHI MITIGATION", className="fw-bold text-white", style={"fontSize": "26px", "letterSpacing": "2px"}),
                            html.Div("Simulation-Based Decision Support System", className="text-white", style={"fontSize": "18px"}),
                        ],
                    ),

                    # Interventions section
                    html.Div("INTERVENTIONS", className="small fw-bold text-uppercase px-3 pt-3 pb-1 text-white", style={"letterSpacing": "2px"}),

                    html.Div(
                        className="px-3 pb-2 d-flex flex-column gap-2",
                        children=[

                            # Tree card
                            html.Div(
                                id="card-tree",
                                n_clicks=0,
                                className="card bg-dark border-secondary d-flex flex-column align-items-center py-2 px-3",
                                style={"cursor": "grab"},
                                children=[
                                    html.Img(src="/assets/images/tree.png", className="intervention-img"),
                                    html.Span("Trees", className="mt-1 fw-semibold text-white", style={"fontSize": "20px"}),
                                ],
                            ),

                            # Green Roof card
                            html.Div(
                                id="card-greenroof",
                                n_clicks=0,
                                className="card bg-dark border-secondary d-flex flex-column align-items-center py-2 px-3",
                                style={"cursor": "grab"},
                                children=[
                                    html.Img(src="/assets/images/greenroof.png", className="intervention-img"),
                                    html.Span("Green Roof", className="mt-1 fw-semibold text-white", style={"fontSize": "20px"}),
                                ],
                            ),

                            # Leaves card
                            html.Div(
                                id="card-leaves",
                                n_clicks=0,
                                className="card bg-dark border-secondary d-flex flex-column align-items-center py-2 px-3",
                                style={"cursor": "grab"},
                                children=[
                                    html.Img(src="/assets/images/leaves.png", className="intervention-img"),
                                    html.Span("Leaf Litter", className="mt-1 fw-semibold text-white", style={"fontSize": "20px"}),
                                ],
                            ),

                        ],
                    ),

                    # Active tool display
                    html.Div(
                        id="active-tool-display",
                        className="px-3 pb-2",
                        children=html.Div(
                            "Click an intervention to get started",
                            className="p-4 text-center text-white border border-success border-2 rounded-3",
                            style={"background": "rgba(255,255,255,0.08)", "fontSize": "17px"},
                        ),
                    ),

                    html.Hr(className="mx-3 text-secondary"),

                    # Spacer
                    html.Div(className="flex-grow-1"),

                    # Buttons
                    html.Div(
                        className="px-3 pb-2 d-flex gap-2",
                        children=[
                            dbc.Button("↩ Undo", id="btn-undo", n_clicks=0, color="light", outline=True, className="flex-fill", style={"fontSize": "18px", "padding": "14px"}),
                            dbc.Button("↺ Reset All", id="btn-reset", n_clicks=0, color="danger", outline=True, className="flex-fill", style={"fontSize": "18px", "padding": "14px"}),
                        ],
                    ),

                    html.Div(
                        className="px-3 pb-2 d-flex gap-2",
                        children=[
                            dbc.Button("✔ Validate Results", id="btn-validate", n_clicks=0, color="light", outline=True, className="flex-fill", style={"fontSize": "18px", "padding": "14px"}),
                        ],
                    ),

                    html.Div(
                        className="px-3 pb-2 d-flex gap-2",
                        children=[
                            dbc.Button("↔ Data Consistency", id="btn-consistency", n_clicks=0, color="light", outline=True, className="flex-fill", style={"fontSize": "18px", "padding": "14px"}),
                        ],
                    ),

                ],
            ),

            # MAP AREA
            html.Div(
                className="map-area",
                children=[

                    dash_deck.DeckGL(
                        id="deck-map",
                        data=map_builder.build_deck(sim).to_json(),
                        mapboxKey="",
                        enableEvents=["click"],
                        style={"width": "100%", "height": "100%"},
                    ),

                    # Temperature legend
                    html.Div(
                        className="temp-legend",
                        children=[
                            html.Div("Temperature (°C)", className="temp-legend-title"),
                            html.Div(
                                className="d-flex align-items-center gap-2",
                                children=[
                                    html.Span("43°", className="temp-legend-min"),
                                    html.Div(className="temp-legend-gradient"),
                                    html.Span("45°", className="temp-legend-max"),
                                ],
                            ),
                        ],
                    ),

                    # Stats overlay
                    html.Div(
                        className="stats-overlay",
                        children=[
                            html.Div("SIMULATION STATS", className="small fw-bold text-uppercase mb-1 text-white", style={"letterSpacing": "2px"}),
                            html.Div(id="stats-panel", className="stats-panel", children=initial_stats),

                            # Cooling effects card
                            html.Div(
                                id="cooling-card",
                                className="card bg-dark bg-opacity-75 border-secondary p-3 mt-2",
                                children=[
                                    html.Div("COOLING EFFECTS", className="small fw-bold text-uppercase mb-2 text-white", style={"letterSpacing": "2px"}),
                                    html.Div(className="d-flex flex-column gap-2", children=[
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Img(src="/assets/images/tree.png", className="cooling-icon"),
                                            html.Span("Trees", className="flex-fill text-white"),
                                            html.Span("−" + str(round(0.0450  * 43, 2)) + "°C", className="fw-bold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Img(src="/assets/images/greenroof.png", className="cooling-icon"),
                                            html.Span("Green Roof", className="flex-fill text-white"),
                                            html.Span("−" + str(round(0.0250 * 200, 2)) + "°C", className="fw-bold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Img(src="/assets/images/leaves.png", className="cooling-icon"),
                                            html.Span("Leaf Litter", className="flex-fill text-white"),
                                            html.Span("−" + str(round(0.0180  * 100, 2)) + "°C", className="fw-bold text-white text-end"),
                                        ]),
                                    ]),
                                ],
                            ),

                            # Temp scale card
                            html.Div(
                                className="card bg-dark bg-opacity-75 border-secondary p-3 mt-2",
                                children=[
                                    html.Div("TEMPERATURE SCALE", className="small fw-bold text-uppercase mb-2 text-white", style={"letterSpacing": "2px"}),
                                    html.Div(className="d-flex flex-column gap-2", children=[
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#7b0000"}),
                                            html.Span("Dark Red", className="flex-fill text-white"),
                                            html.Span("Very Hot", className="fw-semibold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#e74c3c"}),
                                            html.Span("Red", className="flex-fill text-white"),
                                            html.Span("Hot", className="fw-semibold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#e67e22"}),
                                            html.Span("Orange", className="flex-fill text-white"),
                                            html.Span("Warm", className="fw-semibold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#f1c40f"}),
                                            html.Span("Yellow", className="flex-fill text-white"),
                                            html.Span("Moderate", className="fw-semibold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#2ecc71"}),
                                            html.Span("Green", className="flex-fill text-white"),
                                            html.Span("Cool", className="fw-semibold text-white text-end"),
                                        ]),
                                        html.Div(className="d-flex align-items-center gap-2", children=[
                                            html.Span(className="legend-dot", style={"background": "#3498db"}),
                                            html.Span("Blue", className="flex-fill text-white"),
                                            html.Span("Very Cool", className="fw-semibold text-white text-end"),
                                        ]),
                                    ]),
                                ],
                            ),
                        ],
                    ),

                ],
            ),

            # BUILDING INFO MODAL
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Building Info")),
                    dbc.ModalBody(id="building-modal-content"),
                ],
                id="building-modal",
                is_open=False,
                size="lg",
            ),

            # VALIDATION MODAL
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Validation Results")),
                    dbc.ModalBody(id="validation-modal-content"),
                ],
                id="validation-modal",
                is_open=False,
                size="lg",
            ),

            # CONSISTENCY MODAL
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Data Consistency Check")),
                    dbc.ModalBody(id="consistency-modal-content"),
                ],
                id="consistency-modal",
                is_open=False,
                size="lg",
            ),

            # RESET CONFIRMATION MODAL
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(html.Span(["⚠ Reset All Interventions"], style={"fontSize": "24px"})), style={"fontSize": "24px"}),
                    dbc.ModalBody([
                        html.Div("Are you sure you want to reset all interventions?", className="text-white mb-3", style={"fontSize": "20px"}),
                        html.Div("This action cannot be undone. All placed interventions will be permanently removed.", className="text-white-50 mb-4", style={"fontSize": "16px"}),
                        html.Div(
                            className="d-flex gap-3 justify-content-end",
                            children=[
                                dbc.Button("Cancel", id="btn-cancel-reset", color="light", outline=True, className="px-4 py-2", style={"fontSize": "17px"}),
                                dbc.Button("Yes, Reset All", id="btn-confirm-reset", color="danger", className="px-4 py-2", style={"fontSize": "17px", "fontWeight": "700"}),
                            ],
                        ),
                    ]),
                ],
                id="reset-modal",
                is_open=False,
            ),

            # Tooltips
            dbc.Tooltip("Compare simulated results against published literature", target="btn-validate", placement="bottom"),
            dbc.Tooltip("Check how consistent base temperatures are across 2022–2024", target="btn-consistency", placement="bottom"),

            # Error toast notification
            dbc.Toast(
                id="error-toast",
                header="Something went wrong",
                icon="danger",
                is_open=False,
                dismissable=True,
                duration=5000,
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999, "minWidth": "350px"},
            ),

            # Hidden stores
            dcc.Store(id="store-active-tool"),
            html.Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap",
            ),

        ],
    )
