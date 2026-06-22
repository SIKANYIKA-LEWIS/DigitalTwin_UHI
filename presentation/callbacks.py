from dash import Input, Output, State, callback_context, no_update, html
from config.app_config import AppConfig
from presentation import map_builder
from presentation import panels
from domain.validation_model import ValidationModel


def register(app, sim):


    #---------------------------
    #  SELECT CARD CALLBACK 
    #---------------------------
    @app.callback(

        # --- Outputs ---
        Output("store-active-tool", "data"),
        Output("card-tree", "style"),
        Output("card-greenroof", "style"),
        Output("card-leaves", "style"),
        Output("active-tool-display", "children"),

        # --- Inputs ---
        Input("card-tree", "n_clicks"),
        Input("card-greenroof", "n_clicks"),
        Input("card-leaves", "n_clicks"),

        # --- State ---
        State("store-active-tool", "data"),

        # Run callback only if input changes
        prevent_initial_call=True,
    )

    #--------------------------------------
    #   SELECT CARD CALLBACK FUNCTION
    #--------------------------------------
    def select_tool(tree_clicks, greenroof_clicks, leaves_clicks, active_intervention):

        if not callback_context.triggered:
            return no_update, no_update, no_update, no_update, no_update

        card_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        clicked_tool = card_id.replace("card-", "")

        #WHEN CARD IS UNSELECTD
        Unselected_Card = {"border": "1px solid rgba(255,255,255,0.05)", "boxShadow": "none"}

        if clicked_tool == active_intervention  :
            Guide_Card = html.Div("Click an intervention to get started", className="guide-message")
            return None, Unselected_Card, Unselected_Card, Unselected_Card, Guide_Card

     
        #WHEN CARD IS SELECTED
        Selected_Intervention = AppConfig.INTERVENTION_META[clicked_tool]
        Selected_Card = {"border": "2px solid rgba(255,255,255,0.8)", "boxShadow": "0 0 12px rgba(255,255,255,0.15)"}

     
        tree_style = Unselected_Card
        greenroof_style = Unselected_Card
        leaves_style = Unselected_Card

        #STYLE FOR EACH SELECTED CARD
        if clicked_tool == "tree":
            tree_style = Selected_Card
        elif clicked_tool == "greenroof":
            greenroof_style = Selected_Card
        else:
            leaves_style = Selected_Card

     
        UpdateGuide_Card = html.Div(
            className="tool-tooltip tool-tooltip-" + clicked_tool,
            children=[
                html.Img(src=Selected_Intervention["icon"], className="tool-tooltip-icon"),
                html.Span(Selected_Intervention["label"] + " selected", className="tool-tooltip-label"),
                html.Div("Now click any building on the map to apply intervention", className="tool-tooltip-hint"),
            ],
        )

        return (
            clicked_tool,
            tree_style,
            greenroof_style,
            leaves_style,
            UpdateGuide_Card,
        )


    #---------------------------
    #  MAP INTERACTION CALLBACK 
    #---------------------------
    @app.callback(
        # --- Outputs ---
        Output("deck-map", "data", allow_duplicate=True),
        Output("stats-panel", "children", allow_duplicate=True),
        Output("building-modal", "className"),
        Output("building-modal-content", "children"),
        # --- Inputs ---
        Input("deck-map", "clickInfo"),
        Input("btn-reset", "n_clicks"),
        Input("btn-undo", "n_clicks"),
        Input("btn-close-modal", "n_clicks"),
        # --- State ---
        State("store-active-tool", "data"),
        # Don't run this when the page first loads
        prevent_initial_call=True,
    )


    #------------------------------
    #  MAP CLICK CALLBACK FUNCTION
    #-------------------------------
    def handle_map_click(click_info, reset_clicks, undo_clicks, close_modal_clicks, active_intervention):

      
        trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        #MODAL DISPLAY STATES(VISIBLE/HIDDEN)
        modal_hidden = "building-modal building-modal-hidden"
        modal_visible = "building-modal"

     
        #CLOSE MODAL BUTTON CLICKED
        if trigger_id == "btn-close-modal":
            return no_update, no_update, modal_hidden, no_update

        #UNDO BUTTON CLICKED
        if trigger_id == "btn-undo":
            sim.undo_last()
            return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), modal_hidden, []

        #RESET BUTTON CLICKED
        if trigger_id == "btn-reset":
            sim.reset()
            return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), modal_hidden, []
        
        #BUILDING BLOCK ON THE MAP IS CLICKED
        if trigger_id == "deck-map" and click_info:
            clicked_object = click_info.get("object") or {}
            block_id = clicked_object.get("block_id")

           
            if block_id is None:
                return no_update, no_update, no_update, no_update

            #DISPLAY BUILDING INFORMATION         
            building_info = sim.block_summary(int(block_id))
            modal_content = panels.build_modal(building_info)

            if not active_intervention:
                return no_update, no_update, modal_visible, modal_content

            #PLACE INTERVENTION
            result = sim.place_intervention(int(block_id), active_intervention)

            return map_builder.build_deck(sim).to_json(), panels.build_stats(sim), modal_hidden, []

        #IF NO BUILDING IS CLICKED
        return no_update, no_update, modal_hidden, []


    #---------------------------
    # VALIDATION CALLBACK
    #---------------------------
    @app.callback(
        Output("validation-modal", "className"),
        Output("validation-modal-content", "children"),
        Input("btn-validate", "n_clicks"),
        Input("btn-close-validation", "n_clicks"),
        prevent_initial_call=True,
    )

    #------------------------------
    #  VALIDATION BUTTON HANDLER
    #-------------------------------
    def handle_validate(validate_clicks, close_clicks):

        modal_hidden = "building-modal building-modal-hidden"
        modal_visible = "building-modal"

        trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        # CLOSE VALIDATION MODAL
        if trigger_id == "btn-close-validation":
            return modal_hidden, []

        # RUN VALIDATION ON CURRENT SIMULATION STATE
        validation_output = ValidationModel.Run_Validation(sim)

        # BUILD RESULTS PANEL
        results_content = panels.build_validation_results(validation_output)

        return modal_visible, results_content
