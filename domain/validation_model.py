import math

from domain.cooling_model import CoolingModel


class ValidationModel:

    # Literature coefficients for cooling interventions (in °C per m²)
    LITERATURE_COEFFS = {
        "tree": 0.040,
        "greenroof": 0.030,
        "leaves": 0.015,
    }

    
    INTERVENTION_NAMES = {
        "tree": "Tree",
        "greenroof": "Green Roof",
        "leaves": "Leaf Litter",
    }


    #---------------------------------------
    # COEFFICIENT VALIDATION 
    #---------------------------------------
    def Coefficient_Results():

        results = []

        for intervention_type, name in ValidationModel.INTERVENTION_NAMES.items():
            literature_coefficient = ValidationModel.LITERATURE_COEFFS[intervention_type]
            system_coefficient = CoolingModel.CoolingCoefficient(intervention_type)

            results.append({
                "name": name,
                "literature": literature_coefficient,
                "system": system_coefficient,
                "rmse": round(
                    math.sqrt((system_coefficient - literature_coefficient) ** 2),
                    4,
                ),
            })

        return results


    #---------------------------------------
    # MULTIPLE QUANTITY VALIDATION RESULTS
    #---------------------------------------
    def Quantity_Results(sim):

        results = []
        base_temperatures = [float(value) for value in sim.gdf["base_temp"]]

        for intervention_type, name in ValidationModel.INTERVENTION_NAMES.items():
            intervention_results = []
            system_coefficient = CoolingModel.CoolingCoefficient(intervention_type)
            literature_coefficient = ValidationModel.LITERATURE_COEFFS[intervention_type]
            area = CoolingModel.DefaultArea(intervention_type)

            for quantity in range(1, 6):
                system_temperatures = []
                literature_temperatures = []

                for base_temperature in base_temperatures:
                    system_cooling = system_coefficient * area * quantity
                    literature_cooling = literature_coefficient * area * quantity

                    system_temperatures.append(max(base_temperature - system_cooling, CoolingModel.MIN_TEMP))
                    literature_temperatures.append(base_temperature - literature_cooling)

                simulated_temperature = sum(system_temperatures) / len(system_temperatures)
                synthetic_temperature = sum(literature_temperatures) / len(literature_temperatures)

                squared_errors = []
                for i in range(len(system_temperatures)):
                    error = system_temperatures[i] - literature_temperatures[i]
                    squared_errors.append(error * error)

                rmse = math.sqrt(sum(squared_errors) / len(squared_errors))

                intervention_results.append({
                    "quantity": quantity,
                    "simulated": round(simulated_temperature, 2),
                    "synthetic": round(synthetic_temperature, 2),
                    "rmse": round(rmse, 4),
                })

            results.append({
                "name": name,
                "results": intervention_results,
            })

        return results


    #---------------------------------
    # SIMULATION RESULTS VALIDATION
    #--------------------------------
    def Run_Validation(sim):
        results = []
        total_squared_error = 0

        coefficient_results = ValidationModel.Coefficient_Results()
        quantity_results = ValidationModel.Quantity_Results(sim)

        #------------------------------------
        # Identify Blocks with Interventions
        #------------------------------------
        blocks = set()
        for intervention in sim.interventions:
            blocks.add(intervention["block_id"])

        if not blocks:
            return {
                "results": [],
                "rmse": 0,
                "total_cases": 0,
                "status": "No interventions placed to validate",
                "coefficient_results": coefficient_results,
                "quantity_results": quantity_results,
            }

        #----------------------------------------
        # Validate Each Block with Interventions
        #---------------------------------------
        for block_id in blocks:
            block = sim.gdf[sim.gdf["block_id"] == block_id].iloc[0]
            base_temp = float(block["base_temp"])
            simulated_temp = float(block["current_temp"])

            type_counts = {"tree": 0, "greenroof": 0, "leaves": 0}
            for intervention in sim.interventions:
                if intervention["block_id"] == block_id:
                    type_counts[intervention["type"]] = type_counts.get(intervention["type"], 0) + 1
            
            #-----------------------------
            # Calculate Expected Cooling 
            #-----------------------------
            expected_cooling = 0
            intervention_summary = []
            for intervention_type, count in type_counts.items():
                if count > 0:
                    coeff = ValidationModel.LITERATURE_COEFFS.get(intervention_type, 0)
                    area = CoolingModel.DefaultArea(intervention_type)
                    expected_cooling += coeff * area * count
                    intervention_summary.append(f"{count} x {intervention_type}")

            expected_temp = base_temp - expected_cooling
            
            #------------------------------------
            #  Calculate Error And Squared Error
            #------------------------------------
            error = simulated_temp - expected_temp
            squared_error = error * error
            total_squared_error += squared_error

            results.append({
                "block_id": block_id,
                "base_temp": round(base_temp, 2),
                "simulated_temp": round(simulated_temp, 2),
                "expected_temp": round(expected_temp, 2),
                "error": round(error, 4),
                "squared_error": round(squared_error, 6),
                "interventions": ", ".join(intervention_summary),
            })

        total_cases = len(results)
        rmse = math.sqrt(total_squared_error / total_cases)

        return {
            "results": results,
            "rmse": round(rmse, 6),
            "total_cases": total_cases,
            "coefficient_results": coefficient_results,
            "quantity_results": quantity_results,
        }
