class AppConfig:

    FOOTPRINTS_PATH = "resources/footprints/kitwe_buildings.geojson"
    TEMPERATURE_PATH = "resources/tempreature/Kitwe_CBD_LST_October_2024.tif"
    ROADS_PATH = "resources/footprints/kitwe_roads.geojson"

    # --- INTERVENTION INFO ---   
    INTERVENTION_META = {
        "tree": {
            "label": "Tree",
            "icon": "/assets/images/tree.png",
            "color": "#27ae60",
            "description": "Urban tree planting ",
            "coefficient": "C = 0.0450  \u00b0C/m\u00b2",
            "default_area": 43,
        },
        "greenroof": {
            "label": "Green Roof",
            "icon": "/assets/images/greenroof.png",
            "color": "#16a085",
            "description": "Vegetated roof surface",
            "coefficient": "C = 0.0250 \u00b0C/m\u00b2",
            "default_area": 200,
        },
        "leaves": {
            "label": "Leaf Litter",
            "icon": "/assets/images/leaves.png",
            "color": "#2980b9",
            "description": "Leaf litter",
            "coefficient": "C = 0.0180  \u00b0C/m\u00b2",
            "default_area": 100,
        },
    }

