import dash
from config.app_config import AppConfig
from infrastructure.buildings_loader import BuildingsLoader, Load_Roads
from infrastructure.temperature_processor import TemperatureProcessor
from application.simulation_service import SimulationService
from presentation.layout import build_layout
from presentation.callbacks import register as register_callbacks

class KitweDigitalTwinApplication:
    """Bootstraps data loading, simulation state, and the Dash + Deck.gl UI."""

    def __init__(self, footprints_path=AppConfig.FOOTPRINTS_PATH, port=8050):
        self._footprints_path = footprints_path
        self._port = port

    def run(self):
        print("\n" + "=" * 60)
        print("  KITWE DIGITAL TWIN - UHI Simulator (Deck.gl + Carto)")
        print("=" * 60)

        print("\n[1/4] Loading real Kitwe building footprints...")
        buildings_gdf = BuildingsLoader.Load_Footprints(self._footprints_path)
        print(f"      {len(buildings_gdf)} real buildings loaded from OSM export (kitwe_buidings.geojson)")

        print("[2/4] Processing real Landsat satellite temperatures...")
        buildings_gdf = TemperatureProcessor.Process_Real_Temperatures(AppConfig.TEMPERATURE_PATH, buildings_gdf)

        print("[3/4] Loading road network from real OSM data...")
        roads_gdf = Load_Roads(AppConfig.ROADS_PATH)
        print(f"      {len(roads_gdf)} real roads loaded from kitwe_roads.geojson")

        print("[4/4] Initialising simulation...")
        sim = SimulationService(buildings_gdf)
        hotspots = sim.get_hotspots(threshold_percentile=75)
        unique_blocks = buildings_gdf["block_id"].nunique()
        print(f"      {len(sim.gdf)} buildings in {unique_blocks} blocks | {len(hotspots)} hotspot blocks (top 25%)")

        app = dash.Dash(
            __name__,
            title="DIGITALTWIN UHI MITIGATION",
            suppress_callback_exceptions=True,
            assets_folder="presentation/assets",
        )
        app.layout = build_layout(sim)
        register_callbacks(app, sim)

        print("\n  [OK]  Ready at: http://127.0.0.1:8050")
        print("  [FREE]  No Mapbox token required -- uses Carto Dark Matter (free)")
        print("=" * 60 + "\n")
        app.run(debug=True, port=self._port)


if __name__ == "__main__":
    KitweDigitalTwinApplication().run()
