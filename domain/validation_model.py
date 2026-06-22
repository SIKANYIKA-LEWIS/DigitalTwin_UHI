from domain.cooling_model import CoolingModel


class ValidationModel:

    # Literature coefficients from published studies
    LITERATURE_COEFFS = {
        "tree": 0.040,
        "greenroof": 0.030,
        "leaves": 0.015,
    }

    #---------------------------
    # RUN VALIDATION
    #---------------------------
    def Run_Validation(sim):
        """Validate current simulation state against literature coefficients."""

        results = []
        total_squared_error = 0

        blocks_with_interventions = set()
        for iv in sim.interventions:
            blocks_with_interventions.add(iv["block_id"])

        if not blocks_with_interventions:
            return {
                "results": [],
                "mse": 0,
                "total_cases": 0,
                "status": "No interventions placed to validate"
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
        }
