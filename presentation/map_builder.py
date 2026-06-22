import pandas as pd
import pydeck as pdk
from shapely.geometry import Polygon, MultiPolygon
from presentation.constants import LAT, LON, ZOOM, PITCH, BEARING, TILE_URL, Temp_RGB


# -------------------------------
# Extract Polygon Coordinates
#--------------------------------
def Extract_Polygon(geom):
   
   #Check if MultiPolygon
    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda p: p.area)
   
   #Check if Polygon and get exterior coords
    if isinstance(geom, Polygon):
        return [list(c) for c in geom.exterior.coords]

    return []


# --------------------------
# INTERVENTION ICONS LAYER
# --------------------------
def build_icon_layer(sim):
    Placed_Interventions = pd.DataFrame(sim.interventions)

    # Get Placed intervention data 
    Intervention_positions = sim.gdf[["block_id", "cy", "cx", "height"]].drop_duplicates("block_id")
    Placed_Interventions = Placed_Interventions.merge(Intervention_positions, on="block_id", how="left")

    # Offset intervention positions 
    offsets = {
        "tree": (0, 0),
        "greenroof": (0.00015, 0.00010),
        "leaves": (-0.00015, 0.00010),
    }
    Placed_Interventions["cx_offset"] = Placed_Interventions.apply(lambda r: r["cx"] + offsets[r["type"]][0], axis=1)
    Placed_Interventions["cy_offset"] = Placed_Interventions.apply(lambda r: r["cy"] + offsets[r["type"]][1], axis=1)

    # Intervention Icons
    icons = {
        "tree": {"url": "/assets/images/tree.png", "width": 100, "height": 100, "anchorX": 50, "anchorY": 50},
        "greenroof": {"url": "/assets/images/greenroof.png", "width": 100, "height": 100, "anchorX": 50, "anchorY": 50},
        "leaves": {"url": "/assets/images/leaves.png", "width": 100, "height": 100, "anchorX": 50, "anchorY": 50},
    }
    Placed_Interventions["icon"] = Placed_Interventions["type"].map(icons)

    # Set Icon Elevation Height
    Placed_Interventions["icon_elevation"] = Placed_Interventions["height"] * 4.5 + 5

    return pdk.Layer(
        "IconLayer",
        data=Placed_Interventions.to_dict("records"),
        get_icon="icon",
        get_position=["cx_offset", "cy_offset", "icon_elevation"],
        get_size=70,
        size_units="pixels",
        size_min_pixels=60,
        size_max_pixels=120,
        pickable=False,
    )


# -----------------------
# FULL BUILDING MAP
# -----------------------
def build_deck(sim):

    # copy building data
    Building_data = sim.gdf.copy()

    Building_data["coordinates"] = [Extract_Polygon(geometry_coordinates) for geometry_coordinates in Building_data["geometry"]]
    Building_data["building_color"] = [Temp_RGB(temperature) for temperature in Building_data["current_temp"]]
    Building_data["Building_data"] = Building_data["height"]

    records = Building_data[["block_id", "name", "base_temp", "current_temp", "coordinates", "building_color", "Building_data"]].to_dict("records")

    buildings_layer = pdk.Layer(
        "PolygonLayer",
        id="buildings",
        data=records,
        get_polygon="coordinates",
        get_elevation="Building_data",
        get_fill_color="building_color",
        get_line_color=[255, 255, 255, 200],
        line_width_min_pixels=1,
        extruded=True,
        wireframe=False,
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 255, 255, 80],
        elevation_scale=1,
    )
    layers = [buildings_layer]

    # Add intervention icons once placed
    if sim.interventions:
        layers.append(build_icon_layer(sim))

    # Camera view
    view = pdk.ViewState(latitude=LAT, longitude=LON, zoom=ZOOM, pitch=PITCH, bearing=BEARING)

    return pdk.Deck(layers=layers, initial_view_state=view, map_style=TILE_URL)
