import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os


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
    max_col_clues = max(len(c) for c in col_clues)
    cell_size = 25

    total_height = max_col_clues + num_rows

    fig_width = (max_row_clues + num_cols) * cell_size / 100
    fig_height = (max_col_clues + num_rows) * cell_size / 100

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Draw alternating 5x5 grid background shading
    for i in range(num_rows):
        for j in range(num_cols):
            x = (j + max_col_clues) * cell_size
            y = (num_rows - i - 1 + max_row_clues) * cell_size
            if (i // 5 + j // 5) % 2 == 0:
                ax.add_patch(
                    patches.Rectangle((x, y), cell_size, cell_size, facecolor="#e6e6e6")
                )

    # Draw grid lines
    for i in range(num_rows + 1):
        y = (num_rows - i + max_row_clues) * cell_size
        ax.plot(
            [max_col_clues * cell_size, (max_col_clues + num_cols) * cell_size],
            [y, y],
            color="black",
            linewidth=1 if (i % 5 == 0 or i == num_rows) else 0.5,
        )
    for j in range(num_cols + 1):
        x = (j + max_col_clues) * cell_size
        ax.plot(
            [x, x],
            [max_row_clues * cell_size, (max_row_clues + num_rows) * cell_size],
            color="black",
            linewidth=1 if (j % 5 == 0 or j == num_cols) else 0.5,
        )

    # Draw row clues
    for i, clues in enumerate(row_clues):
        y = (num_rows - 1 - i + max_row_clues + 0.5) * cell_size
        for j, clue in enumerate(reversed(clues)):
            x = (max_col_clues - j - 0.5) * cell_size
            ax.text(x, y, str(clue), va="center", ha="center", fontsize=10)

    # Draw column clues
    for j, clues in enumerate(col_clues):
        x = (j + max_col_clues + 0.5) * cell_size
        for i, clue in enumerate(reversed(clues)):
            y = (total_height + i - 0.5) * cell_size
            ax.text(x, y, str(clue), va="center", ha="center", fontsize=10)

    ax.axis("off")

    # Save to temporary image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        image_path = tmpfile.name
    plt.savefig(image_path, bbox_inches="tight", dpi=600)
    plt.close(fig)

    # Create PDF
    c = canvas.Canvas(os.path.join(filepath, filename + ".pdf"), pagesize=letter)
    page_width, page_height = letter

    img_width = (max_col_clues + num_cols) * cell_size
    img_height = (max_row_clues + num_rows) * cell_size

    scale = min(page_width / img_width, page_height / img_height)
    img_width_scaled = img_width * scale
    img_height_scaled = img_height * scale

    x_pos = (page_width - img_width_scaled) / 2
    y_pos = (page_height - img_height_scaled) / 2

    c.drawImage(
        image_path, x_pos, y_pos, width=img_width_scaled, height=img_height_scaled
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

    generate_nonogram_pdf(puzzle=puzzle, filepath="")
