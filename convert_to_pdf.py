import markdown
from fpdf import FPDF

# Read the markdown file
with open("DMBI_Viva_Notes.md", "r", encoding="utf-8") as f:
    md_text = f.read()

# Convert to basic HTML
html_text = markdown.markdown(md_text)

# Create PDF using fpdf2's write_html
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=11)
try:
    pdf.write_html(html_text)
except Exception as e:
    print("Error during write_html:", e)

# Save the PDF
pdf.output("DMBI_Viva_Notes.pdf")
print("PDF generation complete.")
