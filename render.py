import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os


# TODO: generate numbers for the number of forced and free spaces for each vector.
def generate_nonogram_pdf(
    puzzle: Tuple[List[List[int]], List[List[int]]],
    filepath: str,
    filename: str = "nonogram",
):
    row_clues, col_clues = puzzle
    num_rows = len(row_clues)
    num_cols = len(col_clues)

    # Padding space for clues
    max_row_clues = max(len(r) for r in row_clues)
    row_hint_size = max_row_clues + 2
    row_forced = [sum(runs) + len(runs) - 1 for runs in row_clues]
    max_col_clues = max(len(c) for c in col_clues)
    col_hint_size = max_col_clues + 2
    col_forced = [sum(runs) + len(runs) - 1 for runs in col_clues]
    cell_size = 35

    total_height = col_hint_size + num_rows

    fig_width = (row_hint_size + num_cols) * cell_size / 100
    fig_height = (col_hint_size + num_rows) * cell_size / 100

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Draw alternating 5x5 grid background shading
    for i in range(num_rows):
        for j in range(num_cols):
            x = (j + row_hint_size) * cell_size
            y = (num_rows - i - 1) * cell_size
            if (i // 5 + j // 5) % 2 == 0:
                ax.add_patch(
                    patches.Rectangle((x, y), cell_size, cell_size, facecolor="#e6e6e6")
                )

    # Draw helper value boxes
    for i in range(len(row_clues)):
        ax.add_patch(
            patches.Rectangle(
                (0, (num_rows - 1 - i) * cell_size),
                cell_size,
                cell_size,
                facecolor="#e6e6e6",
            )
        )
    for j in range(len(col_clues)):
        ax.add_patch(
            patches.Rectangle(
                ((row_hint_size + j) * cell_size, (total_height - 1) * cell_size),
                cell_size,
                cell_size,
                facecolor="#e6e6e6",
            )
        )

    # Draw grid lines
    for i in range(num_rows + 1):
        y = (num_rows - i) * cell_size
        ax.plot(
            [0, (row_hint_size + num_cols) * cell_size],
            [y, y],
            color="black",
            linewidth=1 if (i % 5 == 0 or i == num_rows) else 0.5,
        )
    ax.plot(
        [row_hint_size * cell_size, (row_hint_size + num_cols) * cell_size],
        [total_height * cell_size, total_height * cell_size],
        color="black",
        linewidth=1,
    )
    ax.plot(
        [row_hint_size * cell_size, (row_hint_size + num_cols) * cell_size],
        [(total_height - 1) * cell_size, (total_height - 1) * cell_size],
        color="black",
        linewidth=0.5,
    )
    ax.plot(
        [row_hint_size * cell_size, (row_hint_size + num_cols) * cell_size],
        [(total_height - 2) * cell_size, (total_height - 2) * cell_size],
        color="black",
        linewidth=1,
    )
    for j in range(num_cols + 1):
        x = (j + row_hint_size) * cell_size
        ax.plot(
            [x, x],
            [0, (num_rows + col_hint_size) * cell_size],
            color="black",
            linewidth=1 if (j % 5 == 0 or j == num_cols) else 0.5,
        )
    ax.plot([0, 0], [0, num_rows * cell_size], color="black", linewidth=1)
    ax.plot(
        [cell_size, cell_size],
        [0, num_rows * cell_size],
        color="black",
        linewidth=0.5,
    )
    ax.plot(
        [2 * cell_size, 2 * cell_size],
        [0, num_rows * cell_size],
        color="black",
        linewidth=1,
    )

    # Draw row clues
    for i, clues in enumerate(row_clues):
        y = (num_rows - 1 - i + 0.5) * cell_size
        for j, clue in enumerate(reversed(clues)):
            x = (row_hint_size - j - 0.5) * cell_size
            ax.text(x, y, str(clue), va="center", ha="center", fontsize=10)

        forced = row_forced[i]
        ax.text(
            0.5 * cell_size,
            y,
            str(forced),
            va="center",
            ha="center",
            fontsize=10,
        )
        ax.text(
            1.5 * cell_size,
            y,
            str(num_cols - forced),
            va="center",
            ha="center",
            fontsize=10,
        )

    # Draw column clues
    for j, clues in enumerate(col_clues):
        x = (j + row_hint_size + 0.5) * cell_size
        for i, clue in enumerate(reversed(clues)):
            y = (i + num_rows + 1 - 0.5) * cell_size
            ax.text(x, y, str(clue), va="center", ha="center", fontsize=10)

        forced = col_forced[j]
        ax.text(
            x,
            (total_height - 0.5) * cell_size,
            str(forced),
            va="center",
            ha="center",
            fontsize=10,
        )
        ax.text(
            x,
            (total_height - 1.5) * cell_size,
            str(num_rows - forced),
            va="center",
            ha="center",
            fontsize=10,
        )

    ax.axis("off")

    # Save to temporary image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        image_path = tmpfile.name
    ax.set_aspect("equal")
    plt.savefig(image_path, bbox_inches="tight", dpi=300)
    plt.close(fig)

    # Create PDF
    c = canvas.Canvas(os.path.join(filepath, filename + ".pdf"), pagesize=letter)
    page_width, page_height = letter

    img_height = (max_col_clues + num_cols + 2) * cell_size
    img_width = (max_row_clues + num_rows + 2) * cell_size

    scale = min(page_width / img_width, page_height / img_height)
    img_width_scaled = img_width * scale
    img_height_scaled = img_height * scale

    x_pos = (page_width - img_width_scaled) / 2
    y_pos = (page_height - img_height_scaled) / 2

    c.drawImage(
        image_path,
        x_pos,
        y_pos,
        width=img_width_scaled,
        height=img_height_scaled,
        preserveAspectRatio=True,
    )
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2, page_height - 40, filename)
    c.save()

    os.remove(image_path)


if __name__ == "__main__":
    puzzle = (
        [
            [7, 2, 2, 1, 1, 1, 1, 7],
            [1, 1, 1, 2, 5, 2, 1, 1, 1],
            [1, 3, 1, 7, 3, 2, 1, 1, 3, 1],
            [1, 3, 1, 1, 1, 3, 1, 2, 1, 3, 1],
            [1, 3, 1, 1, 6, 1, 2, 2, 1, 3, 1],
            [1, 1, 4, 4, 2, 1, 1, 1],
            [7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
            [1, 2, 1, 1],
            [1, 1, 1, 4, 1, 7, 1, 1, 1, 1],
            [4, 1, 1, 1, 1, 2, 5, 2, 3],
            [1, 3, 2, 3, 3, 1, 3, 1],
            [2, 1, 1, 1, 4, 1, 1, 2, 1],
            [3, 1, 1, 1, 1, 2, 4, 2, 1],
            [1, 3, 3, 1, 6, 1, 1, 2, 1, 2],
            [8, 5, 3, 3, 1, 1, 1],
            [2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
            [5, 1, 6, 1, 1, 5],
            [1, 4, 3, 1, 1, 2, 2, 1, 3, 1, 1, 2],
            [8, 4, 2, 1, 4],
            [3, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1],
            [1, 4, 2, 4, 2, 1, 6],
            [1, 2, 1, 3, 1, 2, 2, 1, 3, 1, 4],
            [5, 1, 4, 1, 4],
            [2, 1, 1, 1, 1, 2, 3, 1, 1],
            [2, 1, 7, 2, 1, 2, 7, 2],
            [1, 4, 2, 1, 2, 1, 1],
            [7, 1, 4, 2, 4, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 3],
            [1, 3, 1, 1, 2, 2, 7],
            [1, 3, 1, 2, 1, 1, 2, 1, 1],
            [1, 3, 1, 1, 2, 1, 1, 2, 1],
            [1, 1, 7, 1, 2, 4, 3, 2],
            [7, 2, 7, 1, 1, 3, 2, 1],
        ],
        [
            [7, 2, 3, 3, 4, 7],
            [1, 1, 2, 2, 2, 3, 3, 1, 1],
            [1, 3, 1, 1, 3, 4, 2, 1, 3, 1],
            [1, 3, 1, 1, 8, 4, 1, 3, 1],
            [1, 3, 1, 2, 2, 3, 1, 1, 1, 1, 3, 1],
            [1, 1, 1, 8, 1, 1, 1],
            [7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
            [2, 3, 3, 1, 1],
            [1, 1, 1, 1, 3, 2, 2, 2, 1, 1],
            [3, 1, 4, 1, 1, 2, 1, 1, 2],
            [5, 1, 3, 1, 1, 1, 1, 2, 5],
            [3, 2, 2, 6, 2, 1, 4, 1],
            [3, 5, 1, 1, 1, 1, 1, 1, 3, 2],
            [1, 1, 1, 1, 7, 1, 2, 4],
            [2, 1, 1, 3, 3, 2, 3, 1, 3],
            [1, 3, 1, 3, 2, 2, 1, 1],
            [3, 2, 1, 3, 1, 3, 1, 1, 1, 2],
            [5, 4, 2, 1, 1, 3, 1, 1],
            [3, 4, 5, 1, 3, 1, 1, 1, 3],
            [2, 7, 1, 1, 1, 2, 1, 1],
            [3, 1, 1, 2, 1, 4, 1],
            [3, 1, 2, 2, 2, 1, 1, 1, 1],
            [1, 5, 3, 1, 1, 1, 4],
            [4, 2, 2, 2, 1, 1, 2, 2, 1, 1],
            [1, 4, 2, 1, 2, 6, 1],
            [1, 2, 1, 2, 1, 2, 1, 3],
            [7, 1, 1, 1, 1, 1, 3, 1, 3, 1],
            [1, 1, 2, 2, 8, 1, 1, 2],
            [1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 1],
            [1, 3, 1, 1, 1, 9, 3, 2],
            [1, 3, 1, 2, 3, 3, 2, 1, 1],
            [1, 1, 1, 1, 1, 2, 2, 3, 1],
            [7, 3, 2, 1, 1, 1, 1, 1, 2],
        ],
    )

    _puzzle = (
        [
            [1, 1, 1, 2, 5, 2, 1, 1, 1],
            [1, 3, 1, 7, 3, 2, 1, 1, 3, 1],
            [1, 3, 1, 1, 1, 3, 1, 2, 1, 3, 1],
            [1, 3, 1, 1, 6, 1, 2, 2, 1, 3, 1],
            [7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7],
        ],
        [
            [7, 2, 3, 3, 4, 7],
            [1, 1, 2, 2, 2, 3, 3, 1, 1],
            [1, 3, 1, 1, 8, 4, 1, 3, 1],
            [1, 1, 1, 8, 1, 1, 1],
            [2, 3, 3, 1, 1],
            [1, 1, 1, 1, 3, 2, 2, 2, 1, 1],
            [3, 1, 4, 1, 1, 2, 1, 1, 2],
        ],
    )

    generate_nonogram_pdf(puzzle=puzzle, filepath="", filename="")
