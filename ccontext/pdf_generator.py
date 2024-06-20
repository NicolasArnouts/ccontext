import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Preformatted,
)
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from ccontext.file_node import FileNode


class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self.story = []
        self.toc = []
        self.custom_styles = self.create_custom_styles()

    def create_custom_styles(self):
        custom_styles = getSampleStyleSheet()
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Register and use the Noto Emoji font for emojis
        pdfmetrics.registerFont(
            TTFont("Helvetica", os.path.join(script_dir, "Helvetica.ttf"))
        )
        pdfmetrics.registerFont(
            TTFont("NotoEmoji", os.path.join(script_dir, "NotoEmoji.ttf"))
        )

        custom_styles.add(
            ParagraphStyle(
                name="TOC",
                fontSize=12,
                textColor=colors.blue,
                underline=True,
                fontName="Helvetica",
            )
        )
        custom_styles.add(
            ParagraphStyle(
                name="FileTree",
                fontSize=10,
                leading=12,
                spaceAfter=6,
                fontName="Helvetica",
            )
        )
        custom_styles.add(
            ParagraphStyle(
                name="FileContent",
                fontSize=10,
                leading=12,
                spaceAfter=6,
                fontName="Courier",
            )
        )
        custom_styles.add(
            ParagraphStyle(name="Emoji", fontSize=10, leading=12, fontName="NotoEmoji")
        )
        return custom_styles

    def create_pdf(self, root_node: FileNode, root_path: str):
        self.doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        self.story.append(
            Paragraph("Directory and File Contents", self.styles["Title"])
        )
        self.story.append(Spacer(1, 0.2 * inch))
        self.add_table_of_contents()
        self.story.append(Paragraph(f"Root Path: {root_path}", self.styles["Heading2"]))
        self.add_tree_section(root_node)
        self.add_file_sections(root_node)
        self.doc.build(
            self.story,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )

        print(f"Total context size: ", root_node.calculate_size())
        print(f"PDF generated at {self.output_path}")

    def add_tree_section(self, node: FileNode, indent: str = ""):
        self.story.append(Paragraph("## FILE TREE ##", self.styles["Heading2"]))
        self.format_file_tree(node, indent)
        self.story.append(Paragraph("## END FILE TREE ##", self.styles["Heading2"]))
        self.story.append(PageBreak())

    def format_file_tree(self, node: FileNode, indent: str):
        if node.node_type == "directory":
            icon = "📁" if not node.excluded else "🚫📁"
            self.story.append(
                Paragraph(
                    f"{indent}<font name='NotoEmoji'>{icon}</font> {node.name}",
                    self.custom_styles["FileTree"],
                )
            )
            for child in node.children:
                self.format_file_tree(child, indent + "&nbsp;&nbsp;&nbsp;&nbsp;")
        else:
            section_anchor = f"section_{len(self.toc)}"
            self.toc.append((node.path, section_anchor))

            icon = "📄" if not node.excluded else "🚫📄"
            self.story.append(
                Paragraph(
                    f"{indent}<font name='NotoEmoji'>📄</font> {node.tokens} <a href=\"#{section_anchor}\">{node.name}</a>",
                    self.custom_styles["FileTree"],
                )
            )

    def add_file_sections(self, node: FileNode):
        if node.node_type == "file":
            section_anchor = None
            for i, (path, anchor) in enumerate(self.toc):
                if path == node.path:
                    section_anchor = anchor
                    break
            if section_anchor:
                self.story.append(
                    Paragraph(
                        f'<a name="{section_anchor}"></a>{node.path} - {node.tokens} tokens',
                        self.styles["Heading2"],
                    )
                )
                self.story.append(Spacer(1, 0.1 * inch))
                try:
                    self.story.append(
                        Preformatted(node.content, self.custom_styles["FileContent"])
                    )
                except Exception as e:
                    print(f"Error adding file content for {node.path}: {e}")
                    self.story.append(
                        Paragraph(
                            "<Error reading file content>",
                            self.custom_styles["FileContent"],
                        )
                    )
                self.story.append(PageBreak())
        elif node.node_type == "directory":
            for child in node.children:
                self.add_file_sections(child)

    def add_table_of_contents(self):
        toc_entries = []
        for file_path, section_anchor in self.toc:
            relative_path = os.path.relpath(file_path)  # Get relative path
            toc_entries.append(
                [
                    Paragraph(
                        f'<a href="#{section_anchor}">{relative_path}</a>',
                        self.custom_styles["TOC"],
                    )
                ]
            )
        if toc_entries:
            table = Table(toc_entries, colWidths=[7 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.blue),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            self.story.append(table)
            self.story.append(PageBreak())

    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.drawString(inch, 0.75 * inch, f"Page {doc.page}")
        canvas.restoreState()

    def escape_html(self, text):
        """Escape HTML tags in text to avoid parsing errors."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_pdf(root_path: str, root_node: FileNode):
    output_path = os.path.join(root_path, "ccontext-output.pdf")
    pdf_gen = PDFGenerator(output_path)
    pdf_gen.create_pdf(root_node, root_path)


if __name__ == "__main__":
    import argparse
    from ccontext.main import load_config, build_file_tree

    parser = argparse.ArgumentParser(
        description="Generate PDF of directory tree and file contents."
    )
    parser.add_argument(
        "root_path", type=str, help="The root path of the directory to process."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to a custom configuration file.",
        default=None,
    )
    args = parser.parse_args()

    config = load_config(args.root_path, args.config)
    excludes, includes = config.get("excluded_folders_files", []), []
    max_tokens = config.get("max_tokens", 32000)

    root_node = build_file_tree(args.root_path, excludes, includes)

    generate_pdf(args.root_path, root_node)
