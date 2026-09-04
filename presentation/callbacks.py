from dash import Input, Output, State, callback_context, no_update, html
from config.app_config import AppConfig
from presentation import map_builder
from presentation import panels
from domain.validation_model import ValidationModel


def register(app, sim):


    @app.callback(
        Output("store-active-tool", "data"),
        Output("card-tree", "style"),
        Output("card-greenroof", "style"),
        Output("card-leaves", "style"),
        Output("active-tool-display", "children"),
        Input("card-tree", "n_clicks"),
        Input("card-greenroof", "n_clicks"),
        Input("card-leaves", "n_clicks"),
        State("store-active-tool", "data"),
        prevent_initial_call=True,
    )
    def select_tool(tree_clicks, greenroof_clicks, leaves_clicks, active_intervention):

        if not callback_context.triggered:
            return no_update, no_update, no_update, no_update, no_update

        card_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        clicked_tool = card_id.replace("card-", "")

        Unselected_Card = {"border": "1px solid rgba(255,255,255,0.05)", "boxShadow": "none"}

        if clicked_tool == active_intervention:
            Guide_Card = html.Div("Click an intervention to get started", className="p-4 text-center text-white border border-success border-2 rounded-3", style={"background": "rgba(255,255,255,0.08)", "fontSize": "17px"})
            return None, Unselected_Card, Unselected_Card, Unselected_Card, Guide_Card

        Selected_Intervention = AppConfig.INTERVENTION_META[clicked_tool]
        Selected_Card = {"border": "2px solid rgba(255,255,255,0.8)", "boxShadow": "0 0 12px rgba(255,255,255,0.15)"}

        tree_style = Unselected_Card
        greenroof_style = Unselected_Card
        leaves_style = Unselected_Card

        if clicked_tool == "tree":
            tree_style = Selected_Card
        elif clicked_tool == "greenroof":
            greenroof_style = Selected_Card
        else:
            leaves_style = Selected_Card

        UpdateGuide_Card = html.Div(
            className="d-flex flex-wrap align-items-center p-4 rounded-3 border border-success border-2 text-white",
            style={"background": "rgba(255,255,255,0.1)"},
            children=[
                html.Img(src=Selected_Intervention["icon"], className="me-2", style={"height": "32px"}),
                html.Span(Selected_Intervention["label"] + " selected", className="fw-bold me-2", style={"fontSize": "18px"}),
                html.Div("Click a building to apply, or click the card again to deselect", className="w-100 mt-1", style={"fontSize": "15px"}),
            ],
        )

        return (
            clicked_tool,
            tree_style,
            greenroof_style,
            leaves_style,
            UpdateGuide_Card,
        )


    @app.callback(
        Output("deck-map", "data", allow_duplicate=True),
        Output("stats-panel", "children", allow_duplicate=True),
        Output("building-modal", "is_open"),
        Output("building-modal-content", "children"),
        Output("error-toast", "is_open"),
        Output("error-toast", "children"),
        Input("deck-map", "clickInfo"),
        Input("btn-undo", "n_clicks"),
        State("store-active-tool", "data"),
        prevent_initial_call=True,
    )
    def handle_map_click(click_info, undo_clicks, active_intervention):

        try:
            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "btn-undo":
                sim.undo_last()
                return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), False, [], False, ""

            if trigger_id == "deck-map" and click_info:
                clicked_object = click_info.get("object") or {}
                block_id = clicked_object.get("block_id")

                if block_id is None:
                    return no_update, no_update, no_update, no_update, False, ""

                building_info = sim.block_summary(int(block_id))
                modal_content = panels.build_modal(building_info)

                if not active_intervention:
                    return no_update, no_update, True, modal_content, False, ""

                sim.place_intervention(int(block_id), active_intervention)

                return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), False, [], False, ""

            return no_update, no_update, False, [], False, ""

        except Exception as e:
            return no_update, no_update, no_update, no_update, True, "An unexpected error occurred. Please try clicking a different building."


    @app.callback(
        Output("validation-modal", "is_open"),
        Output("validation-modal-content", "children"),
        Output("error-toast", "is_open", allow_duplicate=True),
        Output("error-toast", "children", allow_duplicate=True),
        Input("btn-validate", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_validate(validate_clicks):
        try:
            validation_output = ValidationModel.Run_Validation(sim)
            results_content = panels.build_validation_results(validation_output)
            return True, results_content, False, ""
        except Exception as e:
            return True, [html.Div("Unable to run validation. Make sure you have placed at least one intervention.", className="text-white")], False, ""


    @app.callback(
        Output("reset-modal", "is_open"),
        Input("btn-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_reset_modal(clicks):
        return True


    @app.callback(
        Output("reset-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_reset_modal(clicks):
        return False


    @app.callback(
        Output("deck-map", "data", allow_duplicate=True),
        Output("stats-panel", "children", allow_duplicate=True),
        Output("reset-modal", "is_open", allow_duplicate=True),
        Input("btn-confirm-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_confirm_reset(clicks):
        try:
            sim.reset()
            return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), False
        except Exception:
            return no_update, no_update, False
