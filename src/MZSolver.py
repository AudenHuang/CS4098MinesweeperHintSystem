import warnings
from minizinc import Instance, Model, Solver, Status
class MZSolver:
    @staticmethod
    def solve_minizinc_instance(model_path, max_width, max_height, width, height, grid_data,all_solutions=False):
        # Ignore MiniZinc model inconsistency detected warnings
        warnings.filterwarnings("ignore", message=".*model inconsistency detected.*")

        # Load MiniZinc model and solver
        model = Model(model_path)
        gecode = Solver.lookup("gecode")
        instance = Instance(gecode, model)
        instance["Max_Width"] = max_width
        instance["Max_Height"] = max_height
        instance["Width"] = width
        instance["Height"] = height
        instance["grid"] = grid_data
        if all_solutions:
            result = instance.solve()
            if result.status == Status.SATISFIED:
                result = instance.solve(all_solutions=all_solutions)
                return result.statistics["nSolutions"]
            else:
                return 0
        else:
            # with warnings.catch_warnings(record=True) as w:
            #     warnings.simplefilter("always")  # Catch all warnings
            #     result = instance.solve()
            #     if w:
            #         for warning in w:
            #             print(f"Warning: {warning}")
            #             if "model inconsistency detected" in str(warning.message):
            #                 print("Grid data causing the warning:", grid_data)
            #                 print(result.status)
            result = instance.solve()
            return result.status