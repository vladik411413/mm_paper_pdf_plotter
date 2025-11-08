from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import pandas as pd
from scale import Graph

# === CONFIG ===
DRAWING_WIDTH_MM = 275   # graph area width
DRAWING_HEIGHT_MM = 190  # graph area height


def read_points_from_csv(csv_filename):
    """Read points (x,y) from CSV file"""
    try:
        df = pd.read_csv(csv_filename, header=None)
        if df.shape[1] < 2:
            raise ValueError("CSV must have at least two columns (x, y)")
        df = df.iloc[:, :2]
        df.columns = ["x", "y"]
        df = df.dropna()
        points = list(zip(df["x"], df["y"]))
        xmin, xmax = df["x"].min(), df["x"].max()
        ymin, ymax = df["y"].min(), df["y"].max()
        print(f"✅ Read {len(points)} points from {csv_filename}")
        print(f"   X range: {xmin:.2f} → {xmax:.2f}")
        print(f"   Y range: {ymin:.2f} → {ymax:.2f}")
        return points, xmin, xmax, ymin, ymax
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return [], 0, 0, 0, 0


def draw_scaled_grid(c, x_offset, y_offset, width_mm, height_mm, xmin, xmax, ymin, ymax, graph):
    """Draw millimeter grid + scaled axes and labels"""
    # === Millimeter grid ===
    c.saveState()
    for x in range(int(width_mm) + 1):
        x_pos = x_offset + x * mm
        if x % 10 == 0:
            c.setStrokeColorRGB(0.6, 0.6, 0.6)
            c.setLineWidth(0.6)
        else:
            c.setStrokeColorRGB(0.85, 0.85, 0.85)
            c.setLineWidth(0.25)
        c.line(x_pos, y_offset, x_pos, y_offset + height_mm * mm)

    for y in range(int(height_mm) + 1):
        y_pos = y_offset + y * mm
        if y % 10 == 0:
            c.setStrokeColorRGB(0.6, 0.6, 0.6)
            c.setLineWidth(0.6)
        else:
            c.setStrokeColorRGB(0.85, 0.85, 0.85)
            c.setLineWidth(0.25)
        c.line(x_offset, y_pos, x_offset + width_mm * mm, y_pos)
    c.restoreState()

    # === Axes and ticks ===
    sx = graph.ox.scale  # units/mm
    sy = graph.oy.scale

    def to_pdf_x(x): return x_offset + ((x - xmin) / sx) * mm
    def to_pdf_y(y): return y_offset + ((y - ymin) / sy) * mm

    origin_x = to_pdf_x(0 if xmin < 0 else xmin)
    origin_y = to_pdf_y(0 if ymin < 0 else ymin)

    # Axes lines
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.line(x_offset, origin_y, x_offset + width_mm * mm, origin_y)
    c.line(origin_x, y_offset, origin_x, y_offset + height_mm * mm)

    # Tick step
    tick_step_x = graph.ox.power / 10
    tick_step_y = graph.oy.power / 10

    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0, 0, 0)

    # X ticks and labels
    tx = xmin - (xmin % tick_step_x)
    while tx <= xmax:
        px = to_pdf_x(tx)
        c.line(px, origin_y - 2 * mm, px, origin_y + 2 * mm)
        c.drawString(px - 5, origin_y - 6 * mm, f"{tx:g}")
        tx += tick_step_x

    # Y ticks and labels
    ty = ymin - (ymin % tick_step_y)
    while ty <= ymax:
        py = to_pdf_y(ty)
        c.line(origin_x - 2 * mm, py, origin_x + 2 * mm, py)
        c.drawString(origin_x - 15, py - 2, f"{ty:g}")
        ty += tick_step_y


def plot_points(c, points, x_offset, y_offset, xmin, ymin, sx, sy):
    """Plot data points"""
    c.setFillColorRGB(1, 0, 0)
    for x, y in points:
        px = x_offset + ((x - xmin) / sx) * mm
        py = y_offset + ((y - ymin) / sy) * mm
        c.circle(px, py, 1.5, fill=1, stroke=0)


def create_pdf_from_csv(csv_filename, pdf_filename="auto_scaled_plot.pdf"):
    points, xmin, xmax, ymin, ymax = read_points_from_csv(csv_filename)
    if not points:
        return

    xrange_units = xmax - xmin
    yrange_units = ymax - ymin

    # === Determine scale using Graph ===
    g = Graph(xrange_units, DRAWING_WIDTH_MM, yrange_units, DRAWING_HEIGHT_MM)
    print("📏 Scale computed by Graph:")
    print(g)

    sx = g.ox.scale
    sy = g.oy.scale

    # Create PDF
    c = canvas.Canvas(pdf_filename, pagesize=(A4[1], A4[0]))
    page_width, page_height = A4[1], A4[0]
    x_offset = (page_width - DRAWING_WIDTH_MM * mm) / 2
    y_offset = (page_height - DRAWING_HEIGHT_MM * mm) / 2

    # Draw background grid and axes
    draw_scaled_grid(c, x_offset, y_offset, DRAWING_WIDTH_MM, DRAWING_HEIGHT_MM, xmin, xmax, ymin, ymax, g)

    # Draw border
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(x_offset, y_offset, DRAWING_WIDTH_MM * mm, DRAWING_HEIGHT_MM * mm)

    # Plot data points
    plot_points(c, points, x_offset, y_offset, xmin, ymin, sx, sy)

    # Info
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_offset, y_offset - 15, f"Points plotted: {len(points)}")
    c.drawString(x_offset, y_offset - 30, f"Scale X: {sx:.4f} units/mm | Scale Y: {sy:.4f} units/mm")

    c.save()
    print(f"✅ PDF created: {pdf_filename}")


# === Sample test ===
def create_sample_csv(filename="sample_points.csv"):
    sample = [
        [17, 0],
        [20, 200],
        [22, 400],
        [24, 600],
        [26, 800],
        [28, 900],
        [30, 950],
        [32, 980],
        [33, 1000],
        [34, 1080],
        [35, 1091],
    ]
    df = pd.DataFrame(sample)
    df.to_csv(filename, index=False, header=False)
    print(f"Sample CSV created: {filename}")


if __name__ == "__main__":
    #create_sample_csv("sample_points.csv")
    create_pdf_from_csv("sample_points.csv", "auto_scaled_plot.pdf")
