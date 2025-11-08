from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import pandas as pd

def read_points_from_csv(csv_filename):
    """Read points from CSV file with x,y coordinates in mm using pandas"""
    try:
        # Read CSV with pandas - more flexible approach
        # Let pandas auto-detect the number of columns
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
        print(f"First few points: {points[:5]}")  # Show first 5 points for verification
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

def create_grid_with_points(csv_filename, pdf_filename="grid_with_points.pdf", circle_radius=2):
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
    
    # Plot points as circles
    if points:
        plot_points(c, points, x_offset, y_offset, circle_radius)
    else:
        print("No points to plot")
    
    # Add border and labels
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(x_offset, y_offset, grid_width, grid_height)
    
    add_dimension_labels(c, x_offset, y_offset, grid_width, grid_height)
    
    # Add point count information
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(x_offset, y_offset - 20, f"Points plotted: {len(points)}")
    
    c.save()
    print(f"PDF created with points: {pdf_filename}")

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

def plot_points(c, points, x_offset, y_offset, circle_radius):
    """Plot points as circles on the grid"""
    # Set point color (red circles with black border)
    c.setFillColorRGB(1, 0, 0)  # Red fill
    c.setStrokeColorRGB(0, 0, 0)  # Black border
    c.setLineWidth(0.5)
    
    for i, (x_mm, y_mm) in enumerate(points):
        # Convert mm coordinates to PDF coordinates
        x_pdf = x_offset + x_mm * mm
        y_pdf = y_offset + y_mm * mm
        
        # Draw circle
        c.circle(x_pdf, y_pdf, circle_radius, fill=1, stroke=1)
        
        # Optional: Add point numbers (comment out if not needed)
        # c.setFillColorRGB(0, 0, 0)
        # c.setFont("Helvetica", 6)
        # c.drawString(x_pdf + 5, y_pdf + 5, str(i+1))

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

# Simplified function to create a sample CSV file
def create_sample_csv(filename="points.csv"):
    """Create a sample CSV file with test points using pandas"""
    # Create sample data with only 2 columns
    sample_data = [
        [10, 10],
        [50, 30],
        [100, 80],
        [150, 120],
        [200, 50],
        [250, 150],
        [75, 25],
        [125, 75],
        [175, 100],
        [225, 180]
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(filename, index=False, header=False)
    print(f"Sample CSV created: {filename}")
    
    # Display the CSV content for verification
    print("CSV content:")
    print(df.to_string(header=False, index=False))

if __name__ == "__main__":
    # Install required packages: 
    # pip install reportlab pandas
    
    # Create a sample CSV file for testing (optional)
    create_sample_csv("sample_points.csv")
    
    # Create PDF with points from CSV using pandas
    create_grid_with_points(
        csv_filename="sample_points.csv",
        pdf_filename="grid_with_points_pandas.pdf",
        circle_radius=2
    )