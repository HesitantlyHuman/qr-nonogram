from typing import List, Tuple

import numpy as np


def calculate_certain(known: np.ndarray, runs: List[int], length: int) -> np.ndarray:
    # 2  - Undetermined
    # 1  - Must be filled
    # 0  - Could be either
    # -1 - Must be empty
    certain = known + 2 * (known == 0)

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
            for idx, (specific_example, current_understanding) in enumerate(
                zip(vector_so_far, certain)
            ):
                if current_understanding == 0:
                    continue
                if current_understanding == 2:
                    certain[idx] = specific_example
                elif current_understanding != specific_example:
                    certain[idx] = 0
            return

        # Iterate over placements of the first section
        run = remaining_runs[0]
        for run_start in range(start_idx, length - run + 1):
            # Place run at this start location, then increment the start idx
            new_vector = vector_so_far.copy()
            new_vector[run_start : run_start + run] = 1
            if sum(remaining_runs[1:]) + len(remaining_runs[1:]) > length - (
                run_start + run
            ):
                continue
            _place_runs(new_vector, remaining_runs[1:], run_start + run + 1)

    _place_runs(-np.ones(length), runs, 0)
    return certain


def update_board(
    current_board: np.ndarray, row_runs: List[int], column_runs: List[int]
) -> np.ndarray:
    current_board = current_board.copy()
    width, height = current_board.shape

    # First, update the rows
    for row_idx, runs in enumerate(row_runs):
        current_row_values = current_board[:, row_idx]
        next_certain_values = calculate_certain(current_row_values, runs, width)
        current_board[:, row_idx] = next_certain_values

    # Then, update the columns
    for column_idx, runs in enumerate(column_runs):
        current_column_values = current_board[column_idx]
        next_certain_values = calculate_certain(current_column_values, runs, height)
        current_board[column_idx] = next_certain_values

    return current_board


def solve_nonogram(rows: List[int], columns: List[int]) -> np.ndarray:
    size = (len(columns), len(rows))
    board = np.zeros(size)

    for step in range(100):
        next_board = update_board(board, rows, columns)
        if np.all(board == next_board):
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
