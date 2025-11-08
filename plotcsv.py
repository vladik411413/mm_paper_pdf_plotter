from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import pandas as pd
import math

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
    
    # Read points from CSV using pandas
    points = read_points_from_csv(csv_filename)
    
    if points:
        # Calculate data range and scaling parameters
        all_x = [point[0] for point in points]
        all_y = [point[1] for point in points]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        data_width = max_x - min_x
        data_height = max_y - min_y
        
        # Calculate scale factors to fit data within grid
        scale_x = grid_width / (data_width / units_per_mm)
        scale_y = grid_height / (data_height / units_per_mm)
        scale = min(scale_x, scale_y)
        
        # Draw the grid background with unit labels
        draw_grid_with_unit_labels(c, x_offset, y_offset, grid_width, grid_height, 
                                 min_x, max_x, min_y, max_y, units_per_mm, scale)
        
        # Plot points as circles with unit conversion
        plot_points_with_units(c, points, x_offset, y_offset, grid_width, grid_height, 
                             units_per_mm, scale, min_x, min_y, circle_radius)
    else:
        # Draw empty grid with default labels if no points
        draw_grid(c, x_offset, y_offset, grid_width, grid_height)
        add_mm_dimension_labels(c, x_offset, y_offset, grid_width, grid_height)
        print("No points to plot")
    
    # Add border
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(x_offset, y_offset, grid_width, grid_height)
    
    # Add point count and scale information
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(x_offset, y_offset - 20, f"Points plotted: {len(points)}")
    c.drawString(x_offset, y_offset - 35, f"Scale: {units_per_mm} units/mm")
    
    c.save()
    print(f"PDF created with points: {pdf_filename}")

def draw_grid_with_unit_labels(c, x_offset, y_offset, grid_width, grid_height, 
                             min_x, max_x, min_y, max_y, units_per_mm, scale):
    """Draw the millimeter grid with unit labels covering entire axes"""
    # Set light grey color for thin lines
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.2)
    
    # Calculate margins for centering
    data_width_mm = (max_x - min_x) / units_per_mm * scale
    data_height_mm = (max_y - min_y) / units_per_mm * scale
    margin_x = (grid_width - data_width_mm) / 2
    margin_y = (grid_height - data_height_mm) / 2
    
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
    
    # Add unit labels for entire x-axis (bottom)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    
    # Calculate the unit step that corresponds to 10mm grid lines
    unit_step_x = (10 * units_per_mm) / scale
    
    # Find the starting unit value for the left edge
    start_unit_x = min_x - (margin_x / scale) * units_per_mm
    # Round to the nearest multiple of unit_step_x for clean labels
    start_unit_x = math.floor(start_unit_x / unit_step_x) * unit_step_x
    
    # Label every 10mm position along the entire x-axis
    for mm_pos in range(0, int(grid_width / mm) + 1, 10):
        # Calculate the unit value at this millimeter position
        unit_value = start_unit_x + (mm_pos / scale) * units_per_mm
        x_pos = x_offset + mm_pos * mm
        
        # Format the label (use integers if step is integer, otherwise decimals)
        if unit_step_x.is_integer():
            label = f"{int(unit_value)}"
        else:
            label = f"{unit_value:.1f}"
        
        c.drawString(x_pos - 8, y_offset - 12, label)
    
    # Add unit labels for entire y-axis (left)
    # Calculate the unit step that corresponds to 10mm grid lines
    unit_step_y = (10 * units_per_mm) / scale
    
    # Find the starting unit value for the bottom edge
    start_unit_y = min_y - (margin_y / scale) * units_per_mm
    # Round to the nearest multiple of unit_step_y for clean labels
    start_unit_y = math.floor(start_unit_y / unit_step_y) * unit_step_y
    
    # Label every 10mm position along the entire y-axis
    for mm_pos in range(0, int(grid_height / mm) + 1, 10):
        # Calculate the unit value at this millimeter position
        unit_value = start_unit_y + (mm_pos / scale) * units_per_mm
        y_pos = y_offset + mm_pos * mm
        
        # Format the label (use integers if step is integer, otherwise decimals)
        if unit_step_y.is_integer():
            label = f"{int(unit_value)}"
        else:
            label = f"{unit_value:.1f}"
        
        c.drawString(x_offset - 25, y_pos - 3, label)

def draw_grid(c, x_offset, y_offset, grid_width, grid_height):
    """Draw the millimeter grid without unit labels (fallback)"""
    # Set light grey color for thin lines
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.2)
    
    # Draw vertical lines
    for x in range(int(grid_width / mm) + 1):
        x_pos = x_offset + x * mm
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
        if y % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
        c.line(x_offset, y_pos, x_offset + grid_width, y_pos)

def add_mm_dimension_labels(c, x_offset, y_offset, grid_width, grid_height):
    """Add millimeter labels (fallback when no points)"""
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

def plot_points_with_units(c, points, x_offset, y_offset, grid_width, grid_height, 
                         units_per_mm, scale, min_x, min_y, circle_radius):
    """Plot points as circles on the grid with unit conversion"""
    # Calculate margins for centering
    data_width = max([point[0] for point in points]) - min_x
    data_height = max([point[1] for point in points]) - min_y
    margin_x = (grid_width - (data_width / units_per_mm) * scale) / 2
    margin_y = (grid_height - (data_height / units_per_mm) * scale) / 2
    
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
        x_pdf = x_offset + margin_x + (x_mm * scale)
        y_pdf = y_offset + margin_y + (y_mm * scale)
        
        # Draw circle
        c.circle(x_pdf, y_pdf, circle_radius, fill=1, stroke=1)

def create_sample_csv_with_large_range(filename="points_large_range.csv"):
    """Create a sample CSV file with large range like -50 to -4"""
    # Create sample data with large negative range
    sample_data = [
        [-50, -40],
        [-45, -35],
        [-40, -30],
        [-35, -25],
        [-30, -20],
        [-25, -15],
        [-20, -10],
        [-15, -5],
        [-10, -4],
        [-5, -8]
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(filename, index=False, header=False)
    print(f"Sample CSV with large range created: {filename}")
    
    # Display the CSV content for verification
    print("CSV content:")
    print(df.to_string(header=False, index=False))
    print(f"X range: {df[0].min()} to {df[0].max()}")
    print(f"Y range: {df[1].min()} to {df[1].max()}")

if __name__ == "__main__":
    # Install required packages: 
    # pip install reportlab pandas
    
    # Create a sample CSV file with large range for testing
    # create_sample_csv_with_large_range("sample_points_large_range.csv")
    
    # Create PDF with points from CSV using unit conversion
    # Example: 10 units per millimeter
    create_grid_with_points(
        csv_filename="sample_points_negative.csv",
        units_per_mm=10.0,  # Adjust this scale factor as needed
        pdf_filename="grid_with_unit_labels.pdf",
        circle_radius=2
    )