class CoolingModel:
    
    #---------------------------------------
    #  COOLING COEFFICIENTS FOR INTERVENTION
    #---------------------------------------
    C_TREE = 0.0450       
    C_GREENROOF = 0.0250
    C_LEAVES = 0.0180     



    #---------------------------------------
    #   DEFAULT AREAS FOR INTERVENTIONS (m²) 
    #---------------------------------------
    DEFAULT_TREE_AREA = 43   
    DEFAULT_GREENROOF_AREA = 200 
    DEFAULT_LEAVES_AREA = 100    

    #MINIMUM TEMPERATURE ALLOWED
    MIN_TEMP = 12.0


    #---------------------------------------
    # GET DEFAULT AREA FOR INTERVENTIONS  
    #---------------------------------------
    def DefaultArea(intervention_type):
        
        if intervention_type == "tree":
            return CoolingModel.DEFAULT_TREE_AREA
        
        elif intervention_type == "greenroof":
            return CoolingModel.DEFAULT_GREENROOF_AREA
        
        elif intervention_type == "leaves":
            return CoolingModel.DEFAULT_LEAVES_AREA
        
        else:
            return 100
        

    #-----------------------------------------------
    #  GET COOLING COEFFICIENT FOR INTERVENTION TYPE
    #-----------------------------------------------
    def CoolingCoefficient(intervention_type):
        
        if intervention_type == "tree":
            return CoolingModel.C_TREE
        
        elif intervention_type == "greenroof":
            return CoolingModel.C_GREENROOF
        
        elif intervention_type == "leaves":
            return CoolingModel.C_LEAVES
        else:
            return 0.0


    #-----------------------------------------------
    #   CALCULATE COOLING EFFECT OF INTERVENTIONS 
    #-----------------------------------------------
    def ComputeCooling(intervention_type, area=None):

        if area is None:
            area = CoolingModel.DefaultArea(intervention_type)

        coefficient = CoolingModel.CoolingCoefficient(intervention_type)

        cooling = coefficient * area

        return cooling



    

