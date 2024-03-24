import warnings
from minizinc import Instance, Model, Solver, Status
class MZSolver:
    @staticmethod
    def solve_minizinc_instance(model_path, max_height,max_width,height, width, grid_data,all_solutions=False):
        # Ignore MiniZinc model inconsistency detected warnings
        warnings.filterwarnings("ignore", message=".*model inconsistency detected.*")
        # Load MiniZinc model and solver
        model = Model(model_path)
        gecode = Solver.lookup("gecode")
        instance = Instance(gecode, model)
        instance["Max_Height"] = max_height
        instance["Max_Width"] = max_width
        instance["Height"] = height
        instance["Width"] = width
        # instance["MineNum"] = mineNum
        instance["grid"] = grid_data
        if all_solutions:
            result = instance.solve()
            if result.status == Status.SATISFIED:
                result = instance.solve(all_solutions=all_solutions)
                return result.statistics["nSolutions"]
            else:
                return 0
        else:
            result = instance.solve()
            return result.status