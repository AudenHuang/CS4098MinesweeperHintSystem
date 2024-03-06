from minizinc import Instance, Model, Solver, Status
class Helper:
    @staticmethod
    def solve_minizinc_instance(model_path, width, height, grid_data,all_solutions=False):
        # Load MiniZinc model and solver
        model = Model(model_path)
        gecode = Solver.lookup("gecode")
        instance = Instance(gecode, model)
        instance["Width"] = width
        instance["Height"] = height
        instance["grid"] = grid_data
        result = instance.solve(all_solutions=all_solutions)
        if all_solutions:
            return result.statistics["nSolutions"]
        else:
            # Return status otherwise
            return result.status