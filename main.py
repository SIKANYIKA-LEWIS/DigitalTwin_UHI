import dash
import dash_bootstrap_components as dbc
from config.app_config import AppConfig
from infrastructure.buildings_loader import BuildingsLoader, Load_Roads
from infrastructure.temperature_processor import TemperatureProcessor
from application.simulation_service import SimulationService
from presentation.layout import build_layout
from presentation.callbacks import register as register_callbacks


class KitweDigitalTwinApplication:

    def __init__(self, footprints_path=AppConfig.FOOTPRINTS_PATH, port=8050):
        self._footprints_path = footprints_path
        self._port = port

    def run(self):

        buildings_gdf = BuildingsLoader.Load_Footprints(self._footprints_path)

        buildings_gdf_2022 = TemperatureProcessor.Process_Real_Temperatures(AppConfig.TEMPERATURE_PATH_2022, buildings_gdf.copy())
        buildings_gdf["base_temp_2022"] = buildings_gdf_2022["base_temp"]

        buildings_gdf_2023 = TemperatureProcessor.Process_Real_Temperatures(AppConfig.TEMPERATURE_PATH_2023, buildings_gdf.copy())
        buildings_gdf["base_temp_2023"] = buildings_gdf_2023["base_temp"]

        buildings_gdf = TemperatureProcessor.Process_Real_Temperatures(AppConfig.TEMPERATURE_PATH, buildings_gdf)
        buildings_gdf["base_temp_2024"] = buildings_gdf["base_temp"]

        roads_gdf = Load_Roads(AppConfig.ROADS_PATH)

        sim = SimulationService(buildings_gdf)

        app = dash.Dash(
            __name__,
            title="DIGITALTWIN UHI MITIGATION",
            suppress_callback_exceptions=True,
            assets_folder="presentation/assets",
            external_stylesheets=[dbc.themes.DARKLY],
        )
        app.layout = build_layout(sim)
        register_callbacks(app, sim)

        app.run(debug=True, port=self._port)


if __name__ == "__main__":
    KitweDigitalTwinApplication().run()
