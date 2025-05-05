from typing import List, Tuple

import itertools
import numpy as np

PERMUTATION_CACHE = {}


def partitions(n, k):
    for c in itertools.combinations(range(n + k - 1), k - 1):
        yield [b - a - 1 for a, b in zip((-1,) + c, c + (n + k - 1,))]


def build_permutation(empty: List[int], full: List[int], length: int) -> np.ndarray:
    result = -np.ones(length)
    position = 0
    for space, run in zip(empty, full):
        position += space
        result[position : position + run] = 1
        position += run + 1
    return result


def get_possible_permutations(runs: List[int], length: int) -> List[np.ndarray]:
    key = (tuple(runs), length)
    if key in PERMUTATION_CACHE:
        return PERMUTATION_CACHE[key]

    num_forced_spaces = len(runs) - 1
    num_free_spaces = length - sum(runs) - num_forced_spaces

    permutations = []
    for partition in partitions(num_free_spaces, len(runs) + 1):
        permutations.append(build_permutation(partition, runs, length))

    PERMUTATION_CACHE[key] = permutations

    return permutations


def filter_permutations(
    permutations: List[np.ndarray], known: np.ndarray
) -> List[np.ndarray]:
    filtered = []

    for permutation in permutations:
        if np.any(permutation * known == -1):
            continue
        filtered.append(permutation)

    return filtered


def calculate_certain(known: np.ndarray, runs: List[int], length: int) -> np.ndarray:
    possible_solutions = get_possible_permutations(runs, length)
    filtered_solutions = filter_permutations(possible_solutions, known)

    certain = filtered_solutions[0].copy()
    for possibility in filtered_solutions[1:]:
        certain[certain != possibility] = 0
    return certain


def solve_nonogram(row_runs: List[int], column_runs: List[int]) -> np.ndarray:
    width, height = (len(column_runs), len(row_runs))
    board = np.zeros((width, height))

    row_needs_updating = np.ones(height, dtype=bool)
    column_needs_updating = np.ones(width, dtype=bool)

    for step in range(100):
        # print(f"Starting step {step}")
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
            current_column_values = next_board[column_idx, :]
            if np.sum(current_column_values == 0) == 0:
                continue

            next_column_values = calculate_certain(current_column_values, runs, height)
            diff_indices = np.where(current_column_values != next_column_values)[0]
            for row in diff_indices:
                row_needs_updating[row] = True
            next_board[column_idx, :] = next_column_values
        column_needs_updating[:] = False

        if np.all(row_needs_updating == False):
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
    rows = [
        [5, 5],
        [5, 5],
        [3, 1, 3, 1],
        [2, 1, 2, 1],
        [5, 1, 5],
        [1],
        [2],
        [3, 3],
        [1, 5, 1],
        [2, 2],
        [2, 2],
        [7],
    ]
    columns = [
        [5],
        [5, 3],
        [3, 1, 1, 2],
        [2, 1, 1, 2],
        [5, 1, 1],
        [1, 1, 1],
        [3, 1, 1],
        [1, 1],
        [5, 1, 1],
        [5, 1, 2],
        [3, 1, 1, 2],
        [2, 1, 3],
        [5],
    ]

    solved = solve_nonogram(rows, columns)
    print(solved)
    print(calculate_nonogram(solved == 1))

    # known = np.zeros(13)
    # known[0] = -1
    # print(known)
    # print(calculate_certain(known, [5, 5], 13))
