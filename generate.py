from typing import Tuple, List

from dataclasses import dataclass

import numpy as np
import qrcode
import qrcode.constants

from nonogram import calculate_nonogram, solve_nonogram


@dataclass
class QRNonogram:
    solution: np.ndarray
    puzzle: Tuple[List[int], List[int]]


def error_proportion(qr_data: np.ndarray, nonogram_solution: np.ndarray) -> float:
    # Anywhere that nonogram_solution is 0, needs to be an error
    num_different = np.sum(
        qr_data.astype(int) != ((nonogram_solution == 1) + (2 * nonogram_solution == 0))
    )
    return num_different / qr_data.size


def generate_from_text(text: str) -> QRNonogram | None:
    qr = qrcode.QRCode(
        version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, border=0
    )
    qr.add_data(text)
    qr.make(fit=True)

    qr_data = np.array(qr.get_matrix())
    rows, columns = calculate_nonogram(qr_data)
    potential_nonogram = solve_nonogram(rows, columns)

    # Check if the nonogram works as is
    num_uncertain = np.sum(potential_nonogram == 0)
    if num_uncertain == 0:
        return QRNonogram(solution=potential_nonogram, puzzle=(rows, columns))

    # Otherwise, we need to adjust our input to make the nonogram deterministic
    for _ in range(5):
        # Try setting the uncertain entries to be true, and then solve again
        adjusted_nonogram = potential_nonogram + (potential_nonogram == 0)
        rows, columns = calculate_nonogram(adjusted_nonogram == 1)
        potential_nonogram = solve_nonogram(rows, columns)

        if error_proportion(qr_data, potential_nonogram) >= 0.25:
            break

        # Check if the nonogram works as is
        num_uncertain = np.sum(potential_nonogram == 0)
        if num_uncertain == 0:
            return QRNonogram(solution=potential_nonogram, puzzle=(rows, columns))
    return None


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    text_to_puzzlify = input("What message would you like to encode?:")
    nonogram = generate_from_text(text_to_puzzlify)
    if nonogram is None:
        print("Unable to generate qr nonogram puzzle with provided input!")
    else:
        print(nonogram.puzzle)
        plt.imshow(nonogram.solution)
        plt.show()
