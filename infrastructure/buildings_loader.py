import geopandas as geo_utils

class BuildingsLoader:

    """---------------------
    EXTRACT BUILDING NAMES
    ---------------------"""
    @staticmethod
    def Extract_Building_Names(buildings):
        names = []
        for i in range(len(buildings)):
            row = buildings.iloc[i]
            name = ""
            if "name" in row:
               if row["name"]:
                    if str(row["name"]):
                        name = str(row["name"])

            names.append(name)

        return names
        

    @staticmethod
    def Extract_Building_Heights(buildings):
        heights = []
        for i in range(len(buildings)):
            row = buildings.iloc[i]
            height = 10.0 
            if "height" in row:
                if row["height"] is not None:
                    try:
                        height = float(row["height"])
                    except:
                        height = 10.0
            heights.append(height)
        return heights


    """---------------------
    GENERATE BUILDING BLOCKS
    ---------------------"""
    @staticmethod
    def Generate_Building_Blocks(Building_footprints):
        
        buildings_utm = Building_footprints.to_crs("EPSG:32735")
        number_of_buildings = len(buildings_utm)
        
        #BUILDING GEOMETRIES
        Buildings_geometry = []
        for building in buildings_utm.geometry:
            Buildings_geometry.append(building)
        
        #INITIALIZE EACH BUILDING BLOCKS AS SEPARATE BLOCKS 
        Building_blocks = []
        for i in range(number_of_buildings):
            Building_blocks.append(i)
        
        #BUILDING BLOCK ASSIGNMENT
        for i in range(number_of_buildings):
            for j in range(i + 1, number_of_buildings):
                
                if Buildings_geometry[i].touches(Buildings_geometry[j]) or Buildings_geometry[i].intersects(Buildings_geometry[j]):
                    
                    Block_i = Building_blocks[i]
                    Block_j = Building_blocks[j]
                    
                    if Block_i == Block_j:
                        continue
                    
                    # MERGE BUILDING FOOTPRINTS INTO A SINGLE BLOCK
                    for k in range(number_of_buildings):
                        if Building_blocks[k] == Block_j:
                            Building_blocks[k] = Block_i
        
        # ADD BLOCK IDs TO THE RESULT
        result = Building_footprints.copy()
        result["block_id"] = Building_blocks
        return result


    #-------------------------
    #LOAD BUILDING FOOTPRINTS
    #--------------------------
    @staticmethod
    def Load_Footprints(filepath):
        
        # LOAD BUILDINGS FROM FILE
        buildings = geo_utils.read_file(filepath)
        buildings = buildings.to_crs("EPSG:4326")

        # GROUP BUILDINGS BLOCKS
        buildings = BuildingsLoader.Generate_Building_Blocks(buildings)

        # EXTRACT BUILDING NAMES
        names = BuildingsLoader.Extract_Building_Names(buildings)
        buildings["name"] = names

        # EXTRACT BUILDING HEIGHTS
        heights = BuildingsLoader.Extract_Building_Heights(buildings)
        buildings["height"] = heights

        buildings["base_temp"] = 36.0
        buildings_utm = buildings.to_crs("EPSG:32735")

        # GET CENTROID COORDINATES
        centroids = buildings_utm.geometry.centroid
        centroids_latlon = centroids.to_crs("EPSG:4326")

        cx_values = []
        cy_values = []
        for centroid in centroids_latlon:
            cx_values.append(centroid.x)
            cy_values.append(centroid.y)

        buildings["cx"] = cx_values
        buildings["cy"] = cy_values

        # CALCULATE AREA
        areas = []
        for building in buildings_utm.geometry:
            area = building.area
            area = round(area, 1)
            areas.append(area)

        buildings["area_m2"] = areas

        result = buildings[["block_id", "name", "geometry", "height", "base_temp", "cx", "cy", "area_m2"]]
        return result


"""---------------------
LOAD ROADS FROM FILE
---------------------"""
def Load_Roads(filepath):

    roads_data = geo_utils.read_file(filepath)
    roads_data = roads_data.to_crs("EPSG:4326")

    if "name" not in roads_data.columns:
        roads_data["name"] = "Unnamed Road"
    return roads_data[["name", "geometry"]]


