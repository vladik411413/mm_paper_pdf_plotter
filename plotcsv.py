from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import pandas as pd

def read_points_from_csv(csv_filename):
    """Read points from CSV file with x,y coordinates in units using pandas"""
    try:
        # Read CSV with pandas - auto-detect columns
        df = pd.read_csv(csv_filename, header=None)
        
        # Check if we have at least 2 columns
        if df.shape[1] < 2:
            print(f"Error: CSV file needs at least 2 columns, but has {df.shape[1]}")
            return []
        
        # Use first two columns for x and y
        df = df.iloc[:, :2]  # Take only first two columns
        df.columns = ['x', 'y']  # Rename columns
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        # Convert to list of tuples
        points = list(zip(df['x'], df['y']))
        print(f"Successfully read {len(points)} points from {csv_filename}")
        print(f"Point range: x=[{df['x'].min():.2f}, {df['x'].max():.2f}], y=[{df['y'].min():.2f}, {df['y'].max():.2f}]")
        return points
        
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_filename}' not found")
        return []
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file '{csv_filename}' is empty")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def create_grid_with_points(csv_filename, units_per_mm, pdf_filename="grid_with_points.pdf", circle_radius=2):
    # Grid dimensions
    grid_width = 275 * mm
    grid_height = 190 * mm
    
    # Create PDF with landscape A4
    c = canvas.Canvas(pdf_filename, pagesize=(A4[1], A4[0]))
    
    # Calculate position to center the grid on landscape A4 page
    page_width, page_height = A4[1], A4[0]
    x_offset = (page_width - grid_width) / 2
    y_offset = (page_height - grid_height) / 2
    
    # Draw the grid background first
    draw_grid(c, x_offset, y_offset, grid_width, grid_height)
    
    # Read points from CSV using pandas
    points = read_points_from_csv(csv_filename)
    
    # Plot points as circles with unit conversion
    if points:
        plot_points_with_units(c, points, x_offset, y_offset, grid_width, grid_height, units_per_mm, circle_radius)
    else:
        print("No points to plot")
    
    # Add border and labels
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(x_offset, y_offset, grid_width, grid_height)
    
    add_dimension_labels(c, x_offset, y_offset, grid_width, grid_height)
    
    # Add point count and scale information
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(x_offset, y_offset - 20, f"Points plotted: {len(points)}")
    c.drawString(x_offset, y_offset - 35, f"Scale: {units_per_mm} units/mm")
    
    c.save()
    print(f"PDF created with points: {pdf_filename}")

def plot_points_with_units(c, points, x_offset, y_offset, grid_width, grid_height, units_per_mm, circle_radius):
    """Plot points as circles on the grid with unit conversion"""
    # Convert all points to find data range
    all_x = [point[0] for point in points]
    all_y = [point[1] for point in points]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    print(f"Data range in units: x=[{min_x:.2f}, {max_x:.2f}], y=[{min_y:.2f}, {max_y:.2f}]")
    
    # Calculate data dimensions in units
    data_width = max_x - min_x
    data_height = max_y - min_y
    
    # Calculate scale factors to fit data within grid
    scale_x = grid_width / (data_width / units_per_mm)
    scale_y = grid_height / (data_height / units_per_mm)
    
    # Use the smaller scale to maintain aspect ratio
    scale = min(scale_x, scale_y)
    
    print(f"Using scale factor: {scale:.4f} mm per data unit")
    
    # Set point color (red circles with black border)
    c.setFillColorRGB(1, 0, 0)  # Red fill
    c.setStrokeColorRGB(0, 0, 0)  # Black border
    c.setLineWidth(0.5)
    
    for i, (x_unit, y_unit) in enumerate(points):
        # Convert from units to millimeters relative to data origin
        x_mm = (x_unit - min_x) / units_per_mm
        y_mm = (y_unit - min_y) / units_per_mm
        
        # Convert to PDF coordinates (centered in grid)
        margin_x = (grid_width - (data_width / units_per_mm) * scale) / 2
        margin_y = (grid_height - (data_height / units_per_mm) * scale) / 2
        
        x_pdf = x_offset + margin_x + (x_mm * scale)
        y_pdf = y_offset + margin_y + (y_mm * scale)
        
        # Draw circle
        c.circle(x_pdf, y_pdf, circle_radius, fill=1, stroke=1)
        
        # Optional: Add point numbers (comment out if not needed)
        # c.setFillColorRGB(0, 0, 0)
        # c.setFont("Helvetica", 6)
        # c.drawString(x_pdf + 5, y_pdf + 5, f"({x_unit:.1f},{y_unit:.1f})")

def draw_grid(c, x_offset, y_offset, grid_width, grid_height):
    """Draw the millimeter grid"""
    # Set light grey color for thin lines
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.2)
    
    # Draw vertical lines
    for x in range(int(grid_width / mm) + 1):
        x_pos = x_offset + x * mm
        # Every 10th line is thicker
        if x % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
        c.line(x_pos, y_offset, x_pos, y_offset + grid_height)
    
    # Draw horizontal lines
    for y in range(int(grid_height / mm) + 1):
        y_pos = y_offset + y * mm
        # Every 10th line is thicker
        if y % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
        c.line(x_offset, y_pos, x_offset + grid_width, y_pos)

def add_dimension_labels(c, x_offset, y_offset, grid_width, grid_height):
    """Add millimeter labels around the grid"""
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    
    # Label vertical lines (every 10mm)
    for x in range(0, int(grid_width / mm) + 1, 10):
        x_pos = x_offset + x * mm
        c.drawString(x_pos - 5, y_offset - 10, str(x))
    
    # Label horizontal lines (every 10mm)
    for y in range(0, int(grid_height / mm) + 1, 10):
        y_pos = y_offset + y * mm
        c.drawString(x_offset - 15, y_pos - 3, str(y))

def create_sample_csv_with_negative(filename="points_with_negative.csv"):
    """Create a sample CSV file with negative values"""
    # Create sample data with negative values
    sample_data = [
        [-50, -30],
        [-25, 40],
        [0, -10],
        [25, 60],
        [50, -20],
        [75, 80],
        [100, 10],
        [-40, 70],
        [90, -40],
        [-10, -50]
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(filename, index=False, header=False)
    print(f"Sample CSV with negative values created: {filename}")
    
    # Display the CSV content for verification
    print("CSV content:")
    print(df.to_string(header=False, index=False))

if __name__ == "__main__":
    # Install required packages: 
    # pip install reportlab pandas
    
    # Create a sample CSV file with negative values for testing
    create_sample_csv_with_negative("sample_points_negative.csv")
    
    # Create PDF with points from CSV using unit conversion
    # Example: 10 units per millimeter
    create_grid_with_points(
        csv_filename="sample_points_negative.csv",
        units_per_mm=10.0,  # Adjust this scale factor as needed
        pdf_filename="grid_with_scaled_points.pdf",
        circle_radius=2
    )