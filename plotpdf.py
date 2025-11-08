from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def create_grid_pdf(filename="grid.pdf"):
    # Grid dimensions
    grid_width = 275 * mm
    grid_height = 190 * mm
    
    # Create PDF with landscape A4 (swap width and height)
    c = canvas.Canvas(filename, pagesize=(A4[1], A4[0]))  # Landscape A4
    
    # Calculate position to center the grid on landscape A4 page
    page_width, page_height = A4[1], A4[0]  # Swapped for landscape
    x_offset = (page_width - grid_width) / 2
    y_offset = (page_height - grid_height) / 2
    
    # Set light grey color for thin lines
    c.setStrokeColorRGB(0.8, 0.8, 0.8)  # Light grey
    c.setLineWidth(0.2)
    
    # Draw vertical lines
    for x in range(int(grid_width / mm) + 1):
        x_pos = x_offset + x * mm
        # Every 10th line is thicker
        if x % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)  # Darker grey
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)  # Light grey
            c.setLineWidth(0.2)
        
        c.line(x_pos, y_offset, x_pos, y_offset + grid_height)
    
    # Draw horizontal lines
    for y in range(int(grid_height / mm) + 1):
        y_pos = y_offset + y * mm
        # Every 10th line is thicker
        if y % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)  # Darker grey
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)  # Light grey
            c.setLineWidth(0.2)
        
        c.line(x_offset, y_pos, x_offset + grid_width, y_pos)
    
    # Add border around the grid
    c.setStrokeColorRGB(0, 0, 0)  # Black border
    c.setLineWidth(1)
    c.rect(x_offset, y_offset, grid_width, grid_height)
    
    # Add dimension labels
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    '''
    # Label vertical lines (every 10mm)
    for x in range(0, int(grid_width / mm) + 1, 10):
        x_pos = x_offset + x * mm
        c.drawString(x_pos - 5, y_offset - 10, str(x))
    
    # Label horizontal lines (every 10mm)
    for y in range(0, int(grid_height / mm) + 1, 10):
        y_pos = y_offset + y * mm
        c.drawString(x_offset - 15, y_pos - 3, str(y))
    '''
    c.save()
    print(f"PDF created with horizontal A4: {filename}")

# Alternative version with custom page size matching grid dimensions
def create_grid_pdf_exact_size(filename="grid_exact.pdf"):
    # Grid dimensions as page size
    page_width = 275 * mm
    page_height = 190 * mm
    
    # Create PDF with exact grid size (already landscape orientation)
    c = canvas.Canvas(filename, pagesize=(page_width, page_height))
    
    # Set light grey color for thin lines
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(0.2)
    
    # Draw vertical lines
    for x in range(int(page_width / mm) + 1):
        x_pos = x * mm
        if x % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
        c.line(x_pos, 0, x_pos, page_height)
    
    # Draw horizontal lines
    for y in range(int(page_height / mm) + 1):
        y_pos = y * mm
        if y % 10 == 0:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.8)
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.2)
        c.line(0, y_pos, page_width, y_pos)
    
    # Add border
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1.5)
    c.rect(0, 0, page_width, page_height)
    
    c.save()
    print(f"PDF created with exact size: {filename}")

if __name__ == "__main__":
    # Install reportlab first: pip install reportlab
    create_grid_pdf("mm_grid_landscape.pdf")
    create_grid_pdf_exact_size("mm_grid_exact.pdf")