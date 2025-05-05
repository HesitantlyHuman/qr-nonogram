from typing import List, Tuple

import numpy as np


def calculate_certain(known: np.ndarray, runs: List[int], length: int) -> np.ndarray:
    # TODO: we can cace the possible solutions, and then just filter those by the known
    # TODO: calculating the possible solutions really is just splitting the gaps between
    # the runs. So take length - sum(runs), place the mandatory space between each, and
    # then find all possible distributions of the remaining. Seems like itd be faster.
    # 2  - Undetermined
    # 1  - Must be filled
    # 0  - Could be either
    # -1 - Must be empty
    possible_solutions = []

    def _place_runs(
        vector_so_far: np.ndarray,
        remaining_runs: List[int],
        start_idx: int,
    ):
        if len(remaining_runs) == 0:
            # Check if this configuration is valid, based on the preset
            if np.any(known * vector_so_far == -1):
                # We have a mismatch
                return
            possible_solutions.append(vector_so_far)
            return

        # Iterate over placements of the first section
        run = remaining_runs[0]
        for run_start in range(start_idx, length - run + 1):
            # Place run at this start location, then increment the start idx
            new_vector = vector_so_far.copy()
            new_vector[run_start : run_start + run] = 1
            if np.any(known[run_start : run_start + run] == -1):
                # We already know this cannot work, since one of these squares
                # needs to be empty
                continue
            if sum(remaining_runs[1:]) + len(remaining_runs[1:]) - 1 > length - (
                run_start + run
            ):
                continue
            _place_runs(new_vector, remaining_runs[1:], run_start + run + 1)

    _place_runs(-np.ones(length), runs, 0)

    certain = possible_solutions[0]
    for possibility in possible_solutions[1:]:
        certain[certain != possibility] = 0
    return certain


def solve_nonogram(row_runs: List[int], column_runs: List[int]) -> np.ndarray:
    width, height = (len(column_runs), len(row_runs))
    board = np.zeros((width, height))

    row_needs_updating = np.ones(height, dtype=bool)
    column_needs_updating = np.ones(width, dtype=bool)

    for step in range(100):
        print(f"Starting step {step}")
        next_board = board.copy()

        # First, update the rows
        for row_idx, runs in enumerate(row_runs):
            if not row_needs_updating[row_idx]:
                continue
            current_row_values = next_board[:, row_idx]
            # If there are no undetermined entries, we don't bother
            if np.sum(current_row_values == 0) == 0:
                continue

            next_row_values = calculate_certain(current_row_values, runs, width)
            # Find all the entries that have changed
            diff_indices = np.where(current_row_values != next_row_values)[0]
            for column in diff_indices:
                column_needs_updating[column] = True
            next_board[:, row_idx] = next_row_values
        # Next time, we will only try to update rows where the column calcs changed something
        row_needs_updating[:] = False

        if np.all(column_needs_updating == False):
            break

        # Then, update the columns
        for column_idx, runs in enumerate(column_runs):
            if not column_needs_updating[column_idx]:
                continue
            current_column_values = next_board[column_idx]
            if np.sum(current_column_values == 0) == 0:
                continue

            next_column_values = calculate_certain(current_column_values, runs, height)
            diff_indices = np.where(current_column_values != next_column_values)[0]
            for row in diff_indices:
                row_needs_updating[row] = True
            next_board[column_idx] = next_column_values
        column_needs_updating[:] = False

        # Prepare for the next iteration
        if np.all(board == next_board) or np.all(row_needs_updating == False):
            break
        board = next_board

    return board


def run_lengths(slice: np.ndarray) -> List[int]:
    padded = np.pad(slice.astype(int), (1, 1), constant_values=0)
    diff = np.diff(padded)

    run_starts = np.where(diff == 1)[0]
    run_ends = np.where(diff == -1)[0]

    try:
        return (run_ends - run_starts).tolist()
    except ValueError as e:
        print(run_starts)
        print(run_ends)
        print(slice)
        raise e


def calculate_nonogram(array: np.ndarray) -> Tuple[List[int], List[int]]:
    size = array.shape

    rows = []
    for row_idx in range(size[1]):
        rows.append(run_lengths(array[:, row_idx]))

    columns = []
    for column_idx in range(size[0]):
        columns.append(run_lengths(array[column_idx]))

    return rows, columns


if __name__ == "__main__":
    # rows = [
    #     [5, 5],
    #     [5, 5],
    #     [3, 1, 3, 1],
    #     [2, 1, 2, 1],
    #     [5, 1, 5],
    #     [1],
    #     [2],
    #     [3, 3],
    #     [1, 5, 1],
    #     [2, 2],
    #     [2, 2],
    #     [7],
    # ]
    # columns = [
    #     [5],
    #     [5, 3],
    #     [3, 1, 1, 2],
    #     [2, 1, 1, 2],
    #     [5, 1, 1],
    #     [1, 1, 1],
    #     [3, 1, 1],
    #     [1, 1],
    #     [5, 1, 1],
    #     [5, 1, 2],
    #     [3, 1, 1, 2],
    #     [2, 1, 3],
    #     [5],
    # ]

    # solved = solve_nonogram(rows, columns) == 1
    # print(calculate_nonogram(solved))

    run_lengths(
        np.array(
            [
                -1,
                1,
                1,
                1,
                -1,
                -1,
                1,
                1,
                1,
                1,
                -1,
                1,
                1,
                1,
                -1,
                1,
                1,
                1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                1,
            ]
        )
    )
