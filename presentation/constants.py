#MAP VIEW COORDINATES
LAT = -12.8189       
LON = 28.2088        

#MAP VIEW SETTINGS
ZOOM = 17.8
PITCH = 52
BEARING = -15

#BACKGROUND BASEMAP
TILE_URL = (
    "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
)


#KITWE CBD TEMPERATURE RANGE
TEMP_MIN = 43.0    
TEMP_MAX = 45.0


#-----------------------------
# CONVERT TEMPERATURE TO RGB
#----------------------------
def Temp_RGB(temp, temp_min=None, temp_max=None):

    if temp_min is None:
        temp_min = TEMP_MIN
    if temp_max is None:
        temp_max = TEMP_MAX

    #CONVERT TEMP TO RATIO
    ratio = (temp - temp_min) / (temp_max - temp_min)

    if ratio < 0:
        ratio = 0
    if ratio > 1:
        ratio = 1

   #ASSIGN COLOUR TO RATIO
    colour_codes= [
        (0.00, (41, 182, 246)),    # Blue   (cool)
        (0.25, (102, 217, 145)),   # Green
        (0.45, (241, 196, 15)),    # Yellow
        (0.65, (230, 126, 34)),    #  Orange
        (0.85, (231, 76, 60)),     # Red
        (1.00, (123, 0, 0)),       # Dark red (very hot)
    ]

 
    for i in range(len(colour_codes) - 1):
        
        position1, colour1 = colour_codes[i]
        position2, colour2 = colour_codes[i + 1]

        #Check if the ratio falls between the two positions
        if ratio >= position1 and ratio <= position2:

            #Find how far the ratio is between the two positions
            relative_position = (ratio - position1) / (position2 - position1)

            red = int(colour1[0] + relative_position * (colour2[0] - colour1[0]))
            green = int(colour1[1] + relative_position * (colour2[1] - colour1[1]))
            blue = int(colour1[2] + relative_position * (colour2[2] - colour1[2]))

            return [red, green, blue, 225]  

    #Fallback:return dark red
    return [123, 0, 0, 225]

