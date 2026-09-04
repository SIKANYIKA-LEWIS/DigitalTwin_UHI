import dash
import dash_bootstrap_components as dbc
import os
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

    def create_app(self):
        buildings_gdf = BuildingsLoader.Load_Footprints(self._footprints_path)

        buildings_gdf = TemperatureProcessor.Process_Real_Temperatures(AppConfig.TEMPERATURE_PATH, buildings_gdf)

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
        return app

    def run(self):
        app = self.create_app()
        app.run(
            debug=True,
            host="0.0.0.0" if os.environ.get("PORT") else "127.0.0.1",
            port=int(os.environ.get("PORT", self._port)),
        )


app = KitweDigitalTwinApplication().create_app()
server = app.server


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0" if os.environ.get("PORT") else "127.0.0.1",
        port=int(os.environ.get("PORT", 8050)),
    )
