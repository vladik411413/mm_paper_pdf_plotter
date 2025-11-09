from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
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
        """Convert to units"""

        if self.type == SType.MM:
            return self
        # Else convert self from untis to mm
        elif origin.type == SType.MM:
            x_mm = origin.x + (self.x) / tr.ox.scale
            y_mm = origin.y + (self.y) / tr.oy.scale
            return Point(x_mm, y_mm, SType.MM)
        elif origin.type == SType.UNITS:
            x_mm = (- origin.x + (self.x)) / tr.ox.scale
            y_mm = (- origin.y + (self.y)) / tr.oy.scale
            return Point(x_mm, y_mm, SType.MM)
    
    
    def units(self, origin: Point, tr: Transform):
        """Convert to units"""

        if self.type == SType.UNITS:
            return self
        # Else convert self from mm to units
        elif origin.type == SType.UNITS:
            x_units = origin.x + (self.x) * tr.ox.scale
            y_units = origin.y + (self.y) * tr.oy.scale
            return Point(x_units, y_units, SType.UNITS)
        elif origin.type == SType.MM:
            x_units = (- origin.x + (self.x)) * tr.ox.scale
            y_units = (- origin.y + (self.y)) * tr.oy.scale
            return Point(x_units, y_units, SType.UNITS)
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, type={self.type})"

class Paper:
    def __init__(self,width,height, dw, dh, pdf_filename):
        self.w = width
        self.h = height
        self.c = canvas.Canvas(pdf_filename, pagesize=(width, height))
        self.dw = dw
        self.dh = dh
    @property
    def center(self):
        return Point((self.w) / 2, (self.h) / 2, SType.MM)
    @property
    def left(self):
        return (self.w - self.dw) / 2
    @property
    def down(self):
        return (self.h - self.dh) / 2
    @property
    def right(self):
        return (self.w + self.dw) / 2
    @property
    def top(self):
        return (self.h + self.dh) / 2
             
class Plot:
    def __init__(self,csv_filename: str):
        """Read points (x,y) from CSV file"""
        try:
            df = pd.read_csv(csv_filename, header=None)
            if df.shape[1] < 2:
                raise ValueError("CSV must have at least two columns (x, y)")
            df = df.iloc[:, :2]
            df.columns = ["x", "y"]
            df = df.dropna()
            self.points = list(zip(df["x"], df["y"]))
            self.x = df["x"]
            self.y = df["y"]
            self.xmin, self.xmax = df["x"].min(), df["x"].max()
            self.ymin, self.ymax = df["y"].min(), df["y"].max()
            print(f"✅ Read {len(points)} points from {csv_filename}")
            print(f"   X range: {xmin:.2f} → {xmax:.2f}")
            print(f"   Y range: {ymin:.2f} → {ymax:.2f}")

        except Exception as e:
            print(f"❌ Error reading CSV: {e}")

    @property
    def range(self):
        return Point(xmax-xmin,ymax-ymin,SType.UNITS)

    


def draw_scaled_grid(page: Paper, plot: Plot, tr: Transform):
    """Draw millimeter grid + scaled axes and labels"""
    # === Millimeter grid ===
    page.c.saveState()
    for x in range(-int(page.dw)/2,int(page.dw)/2 + 1):
        x_pos = page.center.x + x
        if x % 10 == 0:
            page.c.setStrokeColorRGB(0.6, 0.6, 0.6)
            page.c.setLineWidth(0.6)
        else:
            page.c.setStrokeColorRGB(0.85, 0.85, 0.85)
            page.c.setLineWidth(0.25)
        page.c.line(x_pos*mm, page.bottom*mm, x_pos*mm, page.top * mm)

    for y in range(-int(page.dh)/2,int(page.dh)/2 + 1):
        y_pos = page.center.y + y
        if y % 10 == 0:
            page.c.setStrokeColorRGB(0.6, 0.6, 0.6)
            page.c.setLineWidth(0.6)
        else:
            page.c.setStrokeColorRGB(0.85, 0.85, 0.85)
            page.c.setLineWidth(0.25)
        page.c.line(page.left*mm, y_pos*mm, page.right*mm, y_pos*mm)
    page.c.restoreState()

    # === Axes and ticks ===
    origin = Point(page.left, page.bottom, SType.MM)

    # Axes lines
    page.c.setStrokeColorRGB(0, 0, 0)
    page.c.setLineWidth(1.8)
    page.c.line(origin.x*mm, origin.y*mm, origin.x*mm, page.top*mm)
    page.c.line(origin.x*mm, origin.y*mm, page.right*mm, origin.y*mm)

    # Tick step [units]
    tick_step_x = tr.ox.power / 10
    tick_step_y = tr.oy.power / 10

    page.c.setFont("Helvetica", 6)
    page.c.setFillColorRGB(0, 0, 0)

    # X ticks and labels
    tx0 = Point(plot.xmin - (plot.xmin % tick_step_x),0,SType.UNITS)
    tx=tx0
    while tx.mm(origin,tr).x <= plot.xmax:
        page.c.line(
            tx.mm(origin,tr).x, 
            origin.y - 2 * mm, 
            tx.mm(origin,tr).x, 
            origin.y + 2 * mm)
        page.c.drawString(
            tx.mm(origin,tr).x - 2,
            origin.y - 6 * mm, 
            f"{tx:g}")
        tx.x += tick_step_x

    # X ticks and labels
    tx=tx0
    while tx.mm(origin,tr).x >= plot.xmin:
        page.c.line(
            tx.mm(origin,tr).x, 
            origin.y - 2 * mm, 
            tx.mm(origin,tr).x, 
            origin.y + 2 * mm)
        page.c.drawString(
            tx.mm(origin,tr).x - 2,
            origin.y - 6 * mm, 
            f"{tx:g}")
        tx.x -= tick_step_x

    # Y ticks and labels
    ty0 = Point(plot.ymin - (plot.ymin % tick_step_y),0,SType.UNITS)
    ty=ty0
    while ty.mm(origin,tr).y <= plot.ymay:
        page.c.line(
            ty.mm(origin,tr).y, 
            origin.y - 2 * mm, 
            ty.mm(origin,tr).y, 
            origin.y + 2 * mm)
        page.c.drawString(
            ty.mm(origin,tr).y - 2,
            origin.y - 6 * mm, 
            f"{ty:g}")
        ty.y += tick_step_y

    
    # X ticks and labels
    ty=ty0
    while ty.mm(origin,tr).y >= plot.ymin:
        page.c.line(
            ty.mm(origin,tr).y, 
            origin.y - 2 * mm, 
            ty.mm(origin,tr).y, 
            origin.y + 2 * mm)
        page.c.drawString(
            ty.mm(origin,tr).y - 2,
            origin.y - 6 * mm, 
            f"{ty:g}")
        ty.y -= tick_step_y


def plot_points(c, points, x_offset, y_offset, xmin, xmax, ymin, ymax, sx, sy):
    """Plot data points"""
    page.c.setFillColorRGB(1, 0, 0)
    for x, y in points:
        px = x_offset + ((x - (xmin+xmax)/2) / sx) * mm
        py = y_offset + ((y - (ymin+ymax)/2) / sy) * mm
        page.c.circle(px, py, 1.5, fill=1, stroke=0)


def create_pdf_from_csv(csv_filename, pdf_filename="auto_scaled_plot.pdf"):

    page = Paper(A4[1], A4[0], 275 * mm, 190 * mm, pdf_filename)

    plot = Plot(csv_filename)

    if not plot.points:
        return

    # === Determine scale using Transform ===
    tr = Transform(plot.range.x, page.dw, plot.range.y, page.dh)
    print("📏 Scale computed by Transform:")
    print(tr)

    # Draw background grid and axes
    draw_scaled_grid(page, plot, tr)

    '''
    bottom_left_corner = Point((page.width - drawing.width) / 2,
     (page.height - drawing.height) / 2)

    # Draw border
    page.c.setStrokeColorRGB(0, 0, 0)
    page.c.setLineWidth(1)
    page.c.rect(x_offset, y_offset, DRAWING_WIDTH_MM * mm, DRAWING_HEIGHT_MM * mm)

    # Plot data points
    plot_points(c, points, x_offset, y_offset, xmin, xmax, ymin, ymax, sx, sy)

    # Info
    page.c.setFont("Helvetica", 9)
    page.c.setFillColorRGB(0, 0, 0)
    page.c.drawString(x_offset, y_offset - 15, f"Points plotted: {len(points)}")
    page.c.drawString(x_offset, y_offset - 30, f"Scale X: {sx:.4f} units/mm | Scale Y: {sy:.4f} units/mm")
    '''
    page.c.save()
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
