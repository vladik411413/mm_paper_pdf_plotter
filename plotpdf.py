from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from scale import Transform
from enum import Enum

class SType(Enum):
    MM = 1
    UNITS = 2

class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point(Pair):  # Inherit from Pair
    def __init__(self, x, y, stype=SType.MM):
        # Call parent constructor
        super().__init__(x, y)
        self.type = stype
    
    def mm(self, origin: Pair, tr: Transform):
        """Convert to units (Origin in MM)"""

        if self.type == SType.MM:
            return self
        # Else convert self from untis to mm
        else:
            x_mm = origin.x + (self.x) / tr.ox.scale
            y_mm = origin.y + (self.y) / tr.oy.scale
            return Point(x_mm, y_mm, SType.MM)
    
    
    def units(self, origin: Pair, tr: Transform):
        """Convert to units"""

        if self.type == SType.UNITS:
            return self
        else:
            x_units = (- origin.x + (self.x)) * tr.ox.scale
            y_units = (- origin.y + (self.y)) * tr.oy.scale
            return Point(x_units, y_units, SType.UNITS)
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, type={self.type})"

class Paper:
    def __init__(self,width,height, dw, dh, pdf_filename):
        self.c = canvas.Canvas(pdf_filename, pagesize=(width, height))
        self.w = width / mm
        self.h = height / mm
        self.dw = dw / mm
        self.dh = dh / mm
    @property
    def center(self):
        return Point((self.w) / 2, (self.h) / 2, SType.MM)
    @property
    def left(self):
        return (self.w - self.dw) / 2
    @property
    def bottom(self):
        return (self.h - self.dh) / 2
    @property
    def right(self):
        return (self.w + self.dw) / 2
    @property
    def top(self):
        return (self.h + self.dh) / 2

class Plot:
    def __init__(self, csv_filenames):
        """Read one or more CSV files into datasets."""
        if isinstance(csv_filenames, str):
            csv_filenames = [csv_filenames]

        self.datasets = []  # list of (points, name)
        self.xmin = float("inf")
        self.xmax = float("-inf")
        self.ymin = float("inf")
        self.ymax = float("-inf")

        for fname in csv_filenames:
            try:
                df = pd.read_csv(fname, header=None)
                if df.shape[1] < 2:
                    raise ValueError(f"{fname}: CSV must have at least two columns (x, y)")
                df = df.iloc[:, :2]
                df.columns = ["x", "y"]
                df = df.dropna()

                points = list(zip(df["x"], df["y"]))
                self.datasets.append({
                    "filename": fname,
                    "points": points,
                    "x": df["x"],
                    "y": df["y"],
                })

                # Update global min/max
                self.xmin = min(self.xmin, df["x"].min())
                self.xmax = max(self.xmax, df["x"].max())
                self.ymin = min(self.ymin, df["y"].min())
                self.ymax = max(self.ymax, df["y"].max())

                print(f"✅ Read {len(points)} points from {fname}")
                print(f"   X range: {df['x'].min():.2f} → {df['x'].max():.2f}")
                print(f"   Y range: {df['y'].min():.2f} → {df['y'].max():.2f}")

            except Exception as e:
                print(f"❌ Error reading {fname}: {e}")

        if not self.datasets:
            raise ValueError("No valid datasets loaded")

    @property
    def range(self):
        return Point(self.xmax - self.xmin, self.ymax - self.ymin, SType.UNITS)


def draw_scaled_grid(page: Paper, origin: Pair,  plot: Plot, tr: Transform):
    """Draw millimeter grid + scaled axes and labels"""

    # Tick step every 10 mm
    tick_step_x = 10*tr.ox.scale # ticks n labels every 10 mm (adjust if needed)
    tick_step_y = 10*tr.oy.scale # ticks n labels every 10 mm (adjust if needed)

    page.c.setFont("Schoolbell", 7)
    page.c.setFillColorRGB(0, 0, 0)

    # Grid X
    tx0 = Point(plot.xmin - (plot.xmin % tick_step_x),0,SType.UNITS)
    tx=tx0

    while tx.mm(origin,tr).x > page.left + 10:
        tx.x -= tick_step_x
    corrx = tx.mm(origin,tr).x 
    for x in range(-int(page.w),int(page.w)):
        x_pos = corrx + x
        if x % 10 == 0:
            page.c.setStrokeColorRGB(0.6, 0.6, 0.6)
            page.c.setLineWidth(0.6)
        else:
            page.c.setStrokeColorRGB(0.85, 0.85, 0.85)
            page.c.setLineWidth(0.25)
        page.c.line(x_pos*mm, 0*mm, x_pos*mm, page.h*mm)


    # Grid Y
    ty0 = Point(plot.ymin - (plot.ymin % tick_step_y),0,SType.UNITS)
    ty=ty0
    while ty.mm(origin,tr).y > page.bottom + 10:
        ty.y -= tick_step_y
    corry = tx.mm(origin,tr).y
    for y in range(-int(page.h),int(page.h)):
        y_pos = corry + float(y)
        if y % 10 == 0:
            page.c.setStrokeColorRGB(0.6, 0.6, 0.6)
            page.c.setLineWidth(0.6)
        else:
            page.c.setStrokeColorRGB(0.85, 0.85, 0.85)
            page.c.setLineWidth(0.25)
        page.c.line(0*mm, y_pos*mm, page.w*mm, y_pos*mm)

    page.c.setLineWidth(0.8)
    page.c.setStrokeColorRGB(0, 0, 0)

    corry = corry % 10.0 + 10
    while tx.mm(origin,tr).x < page.right - 10:
        page.c.line(
            tx.mm(origin,tr).x*mm, 
            corry*mm  - 1*mm , 
            tx.mm(origin,tr).x*mm , 
            corry*mm  + 1*mm )
        page.c.drawString(
            tx.mm(origin,tr).x*mm  - 1*mm ,
            corry*mm  - 6*mm , 
            f"{tx.x:.0f}")
        tx.x += tick_step_x

    corrx = corrx % 10.0 + 5
    while ty.mm(origin,tr).y < page.top - 10:
        page.c.line(
            corrx*mm  - 1*mm ,
            ty.mm(origin,tr).y*mm , 
            corrx*mm  + 1*mm ,
            ty.mm(origin,tr).y*mm )
            
        page.c.drawString(
            corrx*mm  - 6*mm , 
            ty.mm(origin,tr).y*mm  - 1*mm ,
            f"{ty.y:.0f}")
        ty.y += tick_step_y
    


    # Axes lines
    page.c.setStrokeColorRGB(0, 0, 0)
    page.c.setLineWidth(0.8)
    page.c.line(corrx*mm, corry*mm, corrx*mm, page.top*mm)
    page.c.line(corrx*mm, corry*mm, page.right*mm, corry*mm)


def plot_points(page, origin, plot, tr):
    """Plot all datasets with different colors."""
    colors = [
        (1, 0, 0), (0, 0, 1), (0, 0.6, 0),
        (0.8, 0.4, 0), (0.5, 0, 0.5), (0, 0.7, 0.7)
    ]

    for i, ds in enumerate(plot.datasets):
        r, g, b = colors[i % len(colors)]
        page.c.setFillColorRGB(r, g, b)
        for x, y in ds["points"]:
            point = Point(x, y, SType.UNITS)
            page.c.circle(point.mm(origin, tr).x * mm, point.mm(origin, tr).y * mm, 1.5, fill=1, stroke=0)
        # ✅ Print dataset info in terminal instead of drawing it on PDF
        print(f"[{i+1}] {ds['filename']} → Color RGB({r:.2f}, {g:.2f}, {b:.2f}), {len(ds['points'])} points")

def create_pdf_from_csv(csv_filenames, pdf_filename="multi_plot.pdf"):

    # Register your custom font
    pdfmetrics.registerFont(TTFont("Schoolbell", "Schoolbell-Regular.ttf"))

    """Create a PDF with all CSVs plotted together."""
    if isinstance(csv_filenames, str):
        csv_filenames = [csv_filenames]

    page = Paper(A4[1], A4[0], 275 * mm, 190 * mm, pdf_filename)
    plot = Plot(csv_filenames)

    # Determine scale based on all datasets
    tr = Transform(plot.range.x, page.dw, plot.range.y, page.dh)
    print("📏 Scale computed by Transform:")
    print(tr)

    # Origin (mm)
    origin = Pair(
        (page.center.x - (plot.xmax + plot.xmin) / (2 * tr.ox.scale)),
        (page.center.y - (plot.ymax + plot.ymin) / (2 * tr.oy.scale)),
    )

    # Draw background grid and axes
    draw_scaled_grid(page, origin, plot, tr)

    # Plot all datasets
    plot_points(page, origin, plot, tr)

    page.c.save()
    print(f"✅ PDF created: {pdf_filename}")


if __name__ == "__main__":
    csvs = ["./zhenya_lab_1.csv", "./zhenya_lab_2.csv", "./zhenya_lab_3.csv"]
    create_pdf_from_csv(csvs, "multi_plot.pdf")
