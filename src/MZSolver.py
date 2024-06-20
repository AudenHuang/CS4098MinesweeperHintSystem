import warnings
from minizinc import Instance, Model, Solver, Status
class MZSolver:
    @staticmethod
    def solve_minizinc_instance( max_height,max_width,height, width, grid_data,all_solutions=False, model_path="./model/constraint.mzn"):
        '''
        Solves a MiniZinc instance for a given Minesweeper board or board section.

        This method takes a grid representing part or the entirety of a Minesweeper board, sets up a MiniZinc instance with this grid, and solves it using the Gecode solver. It can return either the status of the first solution found or count all possible solutions, depending on the `all_solutions` parameter.

        :param max_height: The maximum height of the board this instance represents, used for scaling in the model.
        :param max_width: The maximum width of the board this instance represents, used for scaling in the model.
        :param height: The actual height of the board or board section being solved.
        :param width: The actual width of the board or board section being solved.
        :param grid_data: A 2D array representing the current state of the board or board section. Values typically indicate whether a cell is a mine, flagged, revealed, etc.
        :param all_solutions: A boolean indicating whether to count all solutions (True) or stop after finding the first solution (False).
        :param model_path: The path to the MiniZinc model file (.mzn) that defines the problem constraints and variables.

        :return: If `all_solutions` is False, returns the status (SATISFIED, UNSATISFIABLE, etc.) of solving the instance. If True, returns the number of solutions found.
        '''
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