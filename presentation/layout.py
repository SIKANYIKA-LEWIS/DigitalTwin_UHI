import dash_deck
from dash import dcc, html
from presentation import map_builder
from presentation import panels


def build_layout(sim):

    # Build initial stats to display on load
    initial_stats = panels.build_stats(sim)

    return html.Div(
        className="app",
        children=[

            # ============================================================
            # LEFT SIDEBAR STARTS HERE
            # ============================================================
            html.Div(
                className="sidebar",
                children=[

                    # -- Sidebar header --
                    html.Div(
                        className="sidebar-header",
                        children=[
                            html.Div("DIGITAL TWIN UHI MITIGATION", className="sidebar-title"),
                            html.Div(" Simulation-Based Decision Support System", className="sidebar-tagline"),
                        ],
                    ),

                    # -- Intervention cards section --
                    html.Div("INTERVENTIONS", className="section-label"),

                    html.Div(
                        className="cards-container",
                        children=[

                            # Tree card
                            html.Div(
                                id="card-tree",
                                n_clicks=0,
                                className="intervention-item",
                                children=[
                                    html.Img(src="/assets/images/tree.png", className="intervention-img"),
                                    html.Span("Trees", className="intervention-label"),
                                ],
                            ),

                            # Green Roof card
                            html.Div(
                                id="card-greenroof",
                                n_clicks=0,
                                className="intervention-item",
                                children=[
                                    html.Img(src="/assets/images/greenroof.png", className="intervention-img"),
                                    html.Span("Green Roof", className="intervention-label"),
                                ],
                            ),

                            # Leaves card
                            html.Div(
                                id="card-leaves",
                                n_clicks=0,
                                className="intervention-item",
                                children=[
                                    html.Img(src="/assets/images/leaves.png", className="intervention-img"),
                                    html.Span("Leaf Litter", className="intervention-label"),
                                ],
                            ),

                        ],
                    ),

                    # -- Active tool display with initial guide --
                    html.Div(
                        id="active-tool-display",
                        className="active-tool",
                        children=html.Div(
                            "Click to select an intervention to get started",
                            className="guide-message",
                        ),
                    ),

                    html.Hr(className="divider"),

                    # -- Spacer --
                    html.Div(className="sidebar-spacer"),

                    # -- Undo and Reset buttons --
                    html.Div(
                        className="button-row",
                        children=[
                            html.Button("\u21a9  Undo", id="btn-undo", n_clicks=0, className="btn-undo"),
                            html.Button("\u21ba  Reset All", id="btn-reset", n_clicks=0, className="btn-reset"),
                        ],
                    ),

                    # -- Validate button --
                    html.Div(
                        className="button-row",
                        children=[
                            html.Button("\u2714  Validate Results", id="btn-validate", n_clicks=0, className="btn-undo"),
                        ],
                    ),

                ],
            ),
            #------- LEFT SIDE SIDEBAR ENDS HERE ------------#
       

            # ============================================================
            # RIGHT SIDEBAR STARTS HERE - THE MAP AREA
            # ============================================================
            html.Div(
                className="map-area",
                children=[

                    # -- The map itself --
                    dash_deck.DeckGL(
                        id="deck-map",
                        data=map_builder.build_deck(sim).to_json(),
                        mapboxKey="",
                        enableEvents=["click"],
                        style={"width": "100%", "height": "100%"},
                    ),

                    # -- Temperature Scale --
                    html.Div(
                        className="temp-legend",
                        children=[
                            html.Div("Temperature (\u00b0C)", className="temp-legend-title"),
                            html.Div(
                                className="temp-legend-bar",
                                children=[
                                    html.Span("43\u00b0", className="temp-legend-min"),
                                    html.Div(className="temp-legend-gradient"),
                                    html.Span("45\u00b0", className="temp-legend-max"),
                                ],
                            ),
                        ],
                    ),

                    # -- Simulation stats overlay (right side of map) --
                    html.Div(
                        className="stats-overlay",
                        children=[
                            html.Div("SIMULATION STATS", className="stats-overlay-title"),
                            html.Div(id="stats-panel", className="stats-panel", children=initial_stats),

                            # -- Cooling effect card --
                            html.Div(
                                id="cooling-card",
                                className="cooling-card",
                                children=[
                                    html.Div("COOLING EFFECTS", className="cooling-card-title"),
                                    html.Div(className="cooling-card-body", children=[
                                        html.Div(className="cooling-row", children=[
                                            html.Img(src="/assets/images/tree.png", className="cooling-icon"),
                                            html.Span("Trees", className="cooling-label"),
                                            html.Span("\u2212" + str(round(0.0450  * 43, 2)) + "\u00b0C", className="cooling-value"),
                                        ]),
                                        html.Div(className="cooling-row", children=[
                                            html.Img(src="/assets/images/greenroof.png", className="cooling-icon"),
                                            html.Span("Green Roof", className="cooling-label"),
                                            html.Span("\u2212" + str(round(0.0250 * 200, 2)) + "\u00b0C", className="cooling-value"),
                                        ]),
                                        html.Div(className="cooling-row", children=[
                                            html.Img(src="/assets/images/leaves.png", className="cooling-icon"),
                                            html.Span("Leaf Litter", className="cooling-label"),
                                            html.Span("\u2212" + str(round(0.0180  * 100, 2)) + "\u00b0C", className="cooling-value"),
                                        ]),
                                    ]),
                                ],
                            ),

                            # -- Temperature  card --
                            html.Div(
                                className="cooling-card",
                                children=[
                                    html.Div("TEMPERATURE SCALE", className="cooling-card-title"),
                                    html.Div(className="cooling-card-body", children=[
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#7b0000"}),
                                            html.Span("Dark Red", className="cooling-label"),
                                            html.Span("Very Hot", className="legend-desc"),
                                        ]),
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#e74c3c"}),
                                            html.Span("Red", className="cooling-label"),
                                            html.Span("Hot", className="legend-desc"),
                                        ]),
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#e67e22"}),
                                            html.Span("Orange", className="cooling-label"),
                                            html.Span("Warm", className="legend-desc"),
                                        ]),
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#f1c40f"}),
                                            html.Span("Yellow", className="cooling-label"),
                                            html.Span("Moderate", className="legend-desc"),
                                        ]),
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#2ecc71"}),
                                            html.Span("Green", className="cooling-label"),
                                            html.Span("Cool", className="legend-desc"),
                                        ]),
                                        html.Div(className="legend-row", children=[
                                            html.Span(className="legend-dot", style={"background": "#3498db"}),
                                            html.Span("Blue", className="cooling-label"),
                                            html.Span("Very Cool", className="legend-desc"),
                                        ]),
                                    ]),
                                ],
                            ),
                        ],
                    ),

                ],
            ),
            #------- RIGHT SIDEBAR ENDS HERE ------------#


            # ============================================================
            # MODAL BOX (shows building details)
            # ============================================================
            html.Div(
                id="building-modal",
                className="building-modal building-modal-hidden",
                children=[
                    html.Div(className="building-modal-backdrop"),
                    html.Div(
                        className="building-modal-box",
                        children=[
                            html.Button("\u2715", id="btn-close-modal", n_clicks=0, className="building-modal-close"),
                            html.Div(id="building-modal-content"),
                        ],
                    ),
                ],
            ),

            # ============================================================
            # VALIDATION RESULTS MODAL
            # ============================================================
            html.Div(
                id="validation-modal",
                className="building-modal building-modal-hidden",
                children=[
                    html.Div(className="building-modal-backdrop"),
                    html.Div(
                        className="building-modal-box",
                        children=[
                            html.Button("\u2715", id="btn-close-validation", n_clicks=0, className="building-modal-close"),
                            html.Div(id="validation-modal-content"),
                        ],
                    ),
                ],
            ),

            # ============================================================
            # HIDDEN STUFF (stores and scripts)
            # ============================================================
            dcc.Store(id="store-active-tool"),
            html.Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap",
            ),

        ],
    )
