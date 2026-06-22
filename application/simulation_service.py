import numpy as np
from domain.cooling_model import CoolingModel


class SimulationService:
  
    def __init__(self, buildings_gdf):
        
        self.gdf = buildings_gdf.copy()
        self.gdf["current_temp"] = self.gdf["base_temp"]
        self.interventions = []


    #--------------------------
    # PLACE AN INTERVENTIONS
    #--------------------------
    def place_intervention(self, block_id, intervention_type, area_m2=None):
        
        # Find affected buildings
        affected_buildings = self.gdf.index[self.gdf["block_id"] == block_id]
        if affected_buildings.empty:
            raise ValueError("Block ID " + str(block_id) + " not found.")

        reference_building = affected_buildings[0]

        # Calculate the cooling effect of this intervention
        # (uses default area for the intervention type when area_m2 is None)
        cooling_effect = CoolingModel.ComputeCooling(intervention_type, area_m2)
        current_temperature = self.gdf.at[reference_building, "current_temp"]
        new_temperature = max(current_temperature - cooling_effect, CoolingModel.MIN_TEMP)

        # Update all affected buildings
        for i in affected_buildings:
            self.gdf.at[i, "current_temp"] = new_temperature

        # Use default area where not provided
        if area_m2 is None:
            recorded_area = CoolingModel.DefaultArea(intervention_type)
        else:
            recorded_area = area_m2

      
        self.interventions.append({
            "block_id": block_id,
            "type": intervention_type,
            "area_m2": recorded_area,
            "cooling_effect": round(cooling_effect, 4),
        })

        return {
            "block_id": block_id,
            "current_temperature": round(current_temperature, 2),
            "new_temperature": round(new_temperature, 2),
            "cooling_effect": round(cooling_effect, 4),
            "total_reduction": self.total_reduction(),
            "intervention_type": intervention_type,
        }


    # ------------------
    # RESET SIMULATION
    #-------------------
    def reset(self):
        self.gdf["current_temp"] = self.gdf["base_temp"]
        self.interventions = []


    # -----------------------
    # UNDO LAST INTERVENTION
    #------------------------
    def undo_last(self):

        # Check if Block Has Interventions
        if not self.interventions:
            return False

        # Get block ID of last intervention
        block_id = self.interventions.pop()["block_id"]

        # Find all buildings in this block
        affected_buildings = self.gdf.index[self.gdf["block_id"] == block_id]
        current_temperature = self.gdf.at[affected_buildings[0], "base_temp"]

        #Obtain total cooling effect from all interventions
        total_cooling = sum(
            intervention["cooling_effect"]
            for intervention in self.interventions
            if intervention["block_id"] == block_id
        )
        
        new_temperature = max(current_temperature - total_cooling, CoolingModel.MIN_TEMP)

        for i in affected_buildings:
            self.gdf.at[i, "current_temp"] = new_temperature

        return True


    # ---------------------
    # GET TOTAL REDUCTION
    #---------------------
    def total_reduction(self):
        total = 0
        for intervention in self.interventions:
            total = total + intervention["cooling_effect"]
        return round(total, 3)


    #-------------------------
    # GET INFO ABOUT A BLOCK
    #-------------------------
    def block_summary(self, block_id):

        #Get all buildings in block
        rows = self.gdf[self.gdf["block_id"] == block_id]


        if rows.empty:
            raise ValueError("Block ID " + str(block_id) + " not found.")

        first = rows.iloc[0]
        block_interventions = [iv for iv in self.interventions if iv["block_id"] == block_id]

        return {
            "block_id": int(block_id),
            "name": first["name"],
            "base_temp": round(float(first["base_temp"]), 2),
            "current_temp": round(float(first["current_temp"]), 2),
            "reduction": round(float(first["base_temp"] - first["current_temp"]), 3),
            "area_m2": round(float(rows["area_m2"].sum()), 1) if "area_m2" in rows.columns else None,
            "interventions": block_interventions,
        }



    # --- Find the hottest blocks ---
    def get_hotspots(self, threshold_percentile=75):

        threshold = float(np.percentile(self.gdf["current_temp"], threshold_percentile))
        hotspot = self.gdf[self.gdf["current_temp"] >= threshold]
        return hotspot["block_id"].tolist()
