from domain.cooling_model import CoolingModel


class ValidationModel:

    # Literature coefficients from published studies
    LITERATURE_COEFFS = {
        "tree": 0.040,
        "greenroof": 0.030,
        "leaves": 0.015,
    }

    # Names used when displaying validation tables
    INTERVENTION_NAMES = {
        "tree": "Tree",
        "greenroof": "Green Roof",
        "leaves": "Leaf Litter",
    }


    #---------------------------------------
    # BUILD COEFFICIENT VALIDATION RESULTS
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
                "rmse": round(abs(system_coefficient - literature_coefficient), 4),
            })

        return results


    #---------------------------------------
    # BUILD QUANTITY VALIDATION RESULTS
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

                rmse = (sum(squared_errors) / len(squared_errors)) ** 0.5

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


    #---------------------------------------
    # BUILD INTERVENTION PERFORMANCE RESULTS
    #---------------------------------------
    def Performance_Results(sim, quantity_results):

        base_temperatures = [float(value) for value in sim.gdf["base_temp"]]
        average_base_temperature = sum(base_temperatures) / len(base_temperatures)
        performance_results = []

        for intervention in quantity_results:
            simulated_temperatures = [result["simulated"] for result in intervention["results"]]
            average_simulated_temperature = sum(simulated_temperatures) / len(simulated_temperatures)

            performance_results.append({
                "name": intervention["name"],
                "base_temperature": round(average_base_temperature, 2),
                "simulated_temperature": round(average_simulated_temperature, 2),
                "temperature_reduction": round(average_base_temperature - average_simulated_temperature, 2),
            })

        performance_results.sort(key=lambda result: result["temperature_reduction"], reverse=True)

        return performance_results

    #---------------------------
    # RUN VALIDATION
    #---------------------------
    def Run_Validation(sim):
        """Validate current simulation state against literature coefficients."""

        results = []
        total_squared_error = 0

        coefficient_results = ValidationModel.Coefficient_Results()
        quantity_results = ValidationModel.Quantity_Results(sim)
        performance_results = ValidationModel.Performance_Results(sim, quantity_results)

        blocks_with_interventions = set()
        for iv in sim.interventions:
            blocks_with_interventions.add(iv["block_id"])

        if not blocks_with_interventions:
            return {
                "results": [],
                "mse": 0,
                "total_cases": 0,
                "status": "No interventions placed to validate",
                "coefficient_results": coefficient_results,
                "quantity_results": quantity_results,
                "performance_results": performance_results,
            }

        for block_id in blocks_with_interventions:

            row = sim.gdf[sim.gdf["block_id"] == block_id].iloc[0]
            base_temp = float(row["base_temp"])
            simulated_temp = float(row["current_temp"])

            type_counts = {"tree": 0, "greenroof": 0, "leaves": 0}
            for iv in sim.interventions:
                if iv["block_id"] == block_id:
                    type_counts[iv["type"]] = type_counts.get(iv["type"], 0) + 1

            total_expected_cooling = 0
            for iv_type, count in type_counts.items():
                if count > 0:
                    coeff = ValidationModel.LITERATURE_COEFFS.get(iv_type, 0)
                    area = CoolingModel.DefaultArea(iv_type)
                    total_expected_cooling += coeff * area * count

            expected_temp = base_temp - total_expected_cooling

            error = simulated_temp - expected_temp
            squared_error = error * error
            total_squared_error += squared_error

            intervention_summary = []
            for iv_type, count in type_counts.items():
                if count > 0:
                    intervention_summary.append(f"{count} x {iv_type}")

            results.append({
                "block_id": block_id,
                "base_temp": round(base_temp, 2),
                "simulated_temp": round(simulated_temp, 2),
                "expected_temp": round(expected_temp, 2),
                "error": round(error, 4),
                "squared_error": round(squared_error, 6),
                "interventions": ", ".join(intervention_summary),
            })

        number_of_cases = len(results)
        mse = total_squared_error / number_of_cases if number_of_cases > 0 else 0

        return {
            "results": results,
            "mse": round(mse, 6),
            "total_cases": number_of_cases,
            "coefficient_results": coefficient_results,
            "quantity_results": quantity_results,
            "performance_results": performance_results,
        }
