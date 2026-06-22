import geopandas as geo_utils
import rasterio
from shapely.geometry import Point

class TemperatureProcessor:

    # Landsat constants
    SCALE_FACTOR = 0.00341802
    ADDITIVE_CONST = 149.0
    KELVIN_OFFSET = 273.15

    """---------------------
    LOAD AND PROCESS TEMPERATURE DATA
    ---------------------"""
    @staticmethod
    def Load_Temperature(filepath):
        
        try:
            dataset = rasterio.open(filepath)
            temperature_data = dataset.read(1)
            width = dataset.width
            height = dataset.height
            transform_coordinate = dataset.transform
            
          
            pixel_locations = []
            pixel_temps = []
            
          
            for row in range(height):
                for col in range(width):
                    pixel_value = temperature_data[row, col]
                    
                    if pixel_value == 0 or pixel_value is None:
                        continue
                    
                    if pixel_value > 1000:
                        temp_celsius = TemperatureProcessor.Convert_Celsius(pixel_value)
                    else:
                        temp_celsius = float(pixel_value)
                    
                    if temp_celsius < 0 or temp_celsius > 70:
                        continue
                    
                    x, y = transform_coordinate * (col, row)
                    pixel_locations.append(Point(x, y))
                    pixel_temps.append(temp_celsius)

            # CREATE GEODATAFRAME
            Temperature_GeoData = geo_utils.GeoDataFrame({
                'geometry': pixel_locations,
                'surface_temperature': pixel_temps
            }, crs="EPSG:4326")
                
            dataset.close()
            return Temperature_GeoData
            
        except Exception as e:
            return {
                "Error": "Error Loading Temperature data: " + str(e)
            }

    
    """---------------------
    CONVERT DN TO CELSIUS
    ---------------------"""
    @staticmethod
    def Convert_Celsius(dn_value):
        temperature_kelvin = TemperatureProcessor.SCALE_FACTOR * dn_value + TemperatureProcessor.ADDITIVE_CONST
        temperature_celsius = temperature_kelvin - TemperatureProcessor.KELVIN_OFFSET
        return round(temperature_celsius, 2)


    """------------------------------------------
    AGGREGATE TEMPERATURES TO BUILDING BLOCKS
    ------------------------------------------"""
    @staticmethod
    def Block_Temperatures(temperature_data, buildings_data, temp_column="surface_temperature"):

        #ALIGN BUILDING AND TEMPERATURE COORDINATES
        if temperature_data.crs != buildings_data.crs:
            temperature_data = temperature_data.to_crs(buildings_data.crs)
            
        Temperature_Data = temperature_data[["geometry", temp_column]]
        building_data = buildings_data[["block_id", "geometry"]]
        
        # JOIN TEMPERATURE PIXELS WITH BUILDINGS 
        joined_data = geo_utils.sjoin(
            Temperature_Data,
            building_data,
            how="inner",
            predicate="intersects"
        )
        
        if len(joined_data) == 0:
            return TemperatureProcessor.Nearest_Temperature(temperature_data, buildings_data, temp_column)
        
    
        #BLOCK LEVEL AGGREGATION CALCULATION
        block_temperatures = []  
        block_ids = []  
        
        unique_blocks = joined_data["block_id"].unique()
        
        for block_id in unique_blocks:
            block_mask = joined_data["block_id"] == block_id
            block_temps = joined_data[block_mask][temp_column]
            
            Avg_Temp = round(block_temps.mean(), 2)
            
            block_temperatures.append(Avg_Temp)
            block_ids.append(block_id)
        
        #BLOCK TEMPERATURE GEODATAFRAME
        blocktemp_Geodataframe = geo_utils.GeoDataFrame({
            "block_id": block_ids,
            "base_temp": block_temperatures
        })
        
        # REMOVE OLD BASE_TEMP COLUMN IF EXISTS
        if "base_temp" in buildings_data.columns:
            buildings_data = buildings_data.drop(columns=["base_temp"])
            
        # MERGE BLOCK TEMPERATURES WITH BUILDING DATA
        result = buildings_data.merge(blocktemp_Geodataframe, on="block_id", how="left")
                
        median_temp = result["base_temp"].median()
        result["base_temp"] = result["base_temp"].fillna(median_temp)
        return result



    #------------------------------------------
    #AGGREGATE TEMPERATURES BY NEAREST PIXEL
    #------------------------------------------
    @staticmethod
    def Nearest_Temperature(temperature_data, buildings_data, temp_column="surface_temperature"):
     
        block_temperatures = []
        block_ids = []
        
        unique_blocks = buildings_data["block_id"].unique()
      
        for block_id in unique_blocks:
            building = buildings_data[buildings_data["block_id"] == block_id].iloc[0]
            building_geom = building["geometry"]
            
            if hasattr(building_geom, 'centroid'):
                centroid = building_geom.centroid
            else:
                continue
            
            #FIND THE NEAREST TEMPERATURE PIXEL
            min_dist = float('inf')
            nearest_temp = None
            
            for idx, pixel in temperature_data.iterrows():
                dist = centroid.distance(pixel["geometry"])
                if dist < min_dist:
                    min_dist = dist
                    nearest_temp = pixel[temp_column]
            
           
            if nearest_temp is not None:
                block_temperatures.append(round(nearest_temp, 2))
                block_ids.append(block_id)
        
       
        #BLOCK TEMPERATURE GEODATAFRAME
        block_temp_table = geo_utils.GeoDataFrame({
            "block_id": block_ids,
            "base_temp": block_temperatures
        })
        
        if "base_temp" in buildings_data.columns:
            buildings_data = buildings_data.drop(columns=["base_temp"])
        
        result = buildings_data.merge(block_temp_table, on="block_id", how="left")
        
        #FILL ANY MISSING TEMPERATURES
        if "base_temp" in result.columns:
            median_temp = result["base_temp"].median()
            result["base_temp"] = result["base_temp"].fillna(median_temp)
        else:
            result["base_temp"] = 33.0
        
        return result



    """----------------------------------
    PROCESS SATLLITE SURFACE TEMPERATURES
    ----------------------------------"""
    @staticmethod
    def Process_Real_Temperatures(temperature_file, buildings_data):
     
        temperature_pixels = TemperatureProcessor.Load_Temperature(temperature_file)
        
        if temperature_pixels is None or len(temperature_pixels) == 0:
           if "base_temp" not in buildings_data.columns:
                buildings_data["base_temp"] = 33.0
                return buildings_data
        
        Building_Temperature = TemperatureProcessor.Block_Temperatures(temperature_pixels, buildings_data)
        
        return Building_Temperature
