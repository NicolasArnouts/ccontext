import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageTemplate,
    Frame,
    BaseDocTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
import re


class ResearchPDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = self.create_research_styles()
        self.story = []
        self.toc = TableOfContents()
        self.register_fonts()
        
    def register_fonts(self):
        """Register custom fonts for better typography."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Register fonts
        try:
            pdfmetrics.registerFont(
                TTFont("Helvetica-Custom", os.path.join(script_dir, "Helvetica.ttf"))
            )
        except:
            # Fallback to system fonts if custom fonts not available
            pass
            
    def create_research_styles(self):
        """Create professional styles for research documents."""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='ResearchTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Metadata style
        styles.add(ParagraphStyle(
            name='Metadata',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        
        # Section headers
        styles.add(ParagraphStyle(
            name='ResearchHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=24,
            spaceAfter=12,
            borderWidth=0,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=0
        ))
        
        styles.add(ParagraphStyle(
            name='ResearchHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=18,
            spaceAfter=8
        ))
        
        styles.add(ParagraphStyle(
            name='ResearchHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='ResearchBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c2c2c'),
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            leading=14
        ))
        
        # Executive summary
        styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c2c2c'),
            leftIndent=20,
            rightIndent=20,
            spaceBefore=12,
            spaceAfter=12,
            leading=14,
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#e9ecef'),
            borderWidth=1,
            borderPadding=10
        ))
        
        # List items
        styles.add(ParagraphStyle(
            name='ListItem',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c2c2c'),
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        ))
        
        # Links
        styles.add(ParagraphStyle(
            name='Link',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#3498db'),
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        ))
        
        # Code/URL style
        styles.add(ParagraphStyle(
            name='ResearchCode',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=10,
            rightIndent=10
        ))
        
        return styles
    
    def markdown_to_pdf_elements(self, markdown_content):
        """Convert markdown content to PDF elements."""
        lines = markdown_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                self.story.append(Spacer(1, 0.1 * inch))
                i += 1
                continue
            
            # Headers
            if line.startswith('# '):
                # Main title
                title_text = line[2:].strip()
                # Remove "Research Document:" prefix if present
                if title_text.startswith("Research Document:"):
                    title_text = title_text.replace("Research Document:", "").strip()
                self.story.append(Paragraph(title_text, self.styles['ResearchTitle']))
                self.story.append(Spacer(1, 0.2 * inch))
                
            elif line.startswith('## '):
                # Section headers
                header_text = line[3:].strip()
                self.story.append(Paragraph(header_text, self.styles['ResearchHeading1']))
                
            elif line.startswith('### '):
                # Subsection headers
                header_text = line[4:].strip()
                self.story.append(Paragraph(header_text, self.styles['ResearchHeading2']))
                
            elif line.startswith('#### '):
                # Sub-subsection headers
                header_text = line[5:].strip()
                self.story.append(Paragraph(header_text, self.styles['ResearchHeading3']))
                
            elif line.startswith('**') and line.endswith('**'):
                # Bold metadata lines
                text = line[2:-2]
                self.story.append(Paragraph(text, self.styles['Metadata']))
                
            elif line.startswith('- '):
                # List items
                item_text = line[2:].strip()
                # Check if it's a link
                if '[' in item_text and '](' in item_text:
                    # Parse markdown link
                    link_match = re.match(r'\[(.*?)\]\((.*?)\)', item_text)
                    if link_match:
                        link_text = link_match.group(1)
                        link_url = link_match.group(2)
                        formatted_text = f'• <a href="{link_url}" color="blue">{link_text}</a>'
                        self.story.append(Paragraph(formatted_text, self.styles['Link']))
                else:
                    self.story.append(Paragraph(f"• {item_text}", self.styles['ListItem']))
                    
            elif line.startswith('  - '):
                # Indented list items (for table of contents)
                level = line.count('  ')
                item_text = line.strip('- ').strip()
                indent = level * 20
                style = ParagraphStyle(
                    'IndentedItem',
                    parent=self.styles['ListItem'],
                    leftIndent=indent + 20
                )
                self.story.append(Paragraph(f"• {item_text}", style))
                
            else:
                # Regular paragraphs
                # Check for metadata format (key: value)
                if ':' in line and line.count(':') == 1:
                    parts = line.split(':', 1)
                    if len(parts[0].split()) <= 3:  # Likely a metadata field
                        key = parts[0].strip()
                        value = parts[1].strip()
                        self.story.append(
                            Paragraph(f"<b>{key}:</b> {value}", self.styles['ResearchBody'])
                        )
                    else:
                        self.story.append(Paragraph(line, self.styles['ResearchBody']))
                else:
                    # Check if this is part of executive summary or special section
                    if i > 0 and '## Executive Summary' in lines[i-5:i]:
                        self.story.append(Paragraph(line, self.styles['ExecutiveSummary']))
                    else:
                        self.story.append(Paragraph(line, self.styles['ResearchBody']))
            
            i += 1
    
    def add_header_footer(self, canvas, doc):
        """Add professional header and footer to each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(inch, letter[1] - 0.5 * inch, "Research Document")
        canvas.drawRightString(letter[0] - inch, letter[1] - 0.5 * inch, 
                             datetime.now().strftime("%B %d, %Y"))
        
        # Header line
        canvas.setStrokeColor(colors.HexColor('#e0e0e0'))
        canvas.setLineWidth(0.5)
        canvas.line(inch, letter[1] - 0.6 * inch, letter[0] - inch, letter[1] - 0.6 * inch)
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawString(inch, 0.75 * inch, "Generated by CContext Research Crawler")
        canvas.drawRightString(letter[0] - inch, 0.75 * inch, f"Page {doc.page}")
        
        # Footer line
        canvas.line(inch, inch, letter[0] - inch, inch)
        
        canvas.restoreState()
    
    def generate_pdf(self, markdown_content):
        """Generate a professional PDF from markdown content."""
        # Create the document
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=1.5 * inch
        )
        
        # Add cover page info
        self.story.append(Spacer(1, 2 * inch))
        
        # Convert markdown to PDF elements
        self.markdown_to_pdf_elements(markdown_content)
        
        # Build the PDF
        doc.build(
            self.story,
            onFirstPage=self.add_header_footer,
            onLaterPages=self.add_header_footer
        )
        
        print(f"Research PDF generated at: {self.output_path}")


def convert_markdown_to_pdf(markdown_file_path, output_pdf_path=None):
    """Convert a markdown file to a professional PDF."""
    if output_pdf_path is None:
        base_name = os.path.splitext(markdown_file_path)[0]
        output_pdf_path = f"{base_name}.pdf"
    
    # Read the markdown content
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Generate the PDF
    generator = ResearchPDFGenerator(output_pdf_path)
    generator.generate_pdf(markdown_content)
    
    return output_pdf_path


def convert_json_to_pdf(json_file_path, output_pdf_path=None):
    """Convert a JSON crawler output to a professional PDF."""
    if output_pdf_path is None:
        base_name = os.path.splitext(json_file_path)[0]
        output_pdf_path = f"{base_name}.pdf"
    
    # Read the content (assuming it's markdown in a text file named .json)
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate the PDF
    generator = ResearchPDFGenerator(output_pdf_path)
    generator.generate_pdf(content)
    
    return output_pdf_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert research documents to PDF")
    parser.add_argument("input_file", help="Input markdown or JSON file")
    parser.add_argument("-o", "--output", help="Output PDF file path")
    
    args = parser.parse_args()
    
    if args.input_file.endswith('.json'):
        convert_json_to_pdf(args.input_file, args.output)
    else:
        convert_markdown_to_pdf(args.input_file, args.output)