from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import re


class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self.story = []
        self.toc = []
        self.custom_styles = self.create_custom_styles()

    def create_custom_styles(self):
        custom_styles = getSampleStyleSheet()
        custom_styles.add(
            ParagraphStyle(
                name="TOC", fontSize=12, textColor=colors.blue, underline=True
            )
        )
        custom_styles.add(
            ParagraphStyle(name="FileTree", fontSize=10, leading=12, spaceAfter=6)
        )
        custom_styles.add(
            ParagraphStyle(name="FileContent", fontSize=10, leading=12, spaceAfter=6)
        )
        return custom_styles

    def create_pdf(self, tree_content, file_contents_list):
        self.doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        self.story.append(
            Paragraph("Directory and File Contents", self.styles["Title"])
        )
        self.story.append(Spacer(1, 0.2 * inch))
        self.add_table_of_contents()
        self.add_tree_section(tree_content)
        self.add_file_sections(file_contents_list)
        self.doc.build(
            self.story,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        print(f"PDF generated at {self.output_path}")

    def add_tree_section(self, tree_content):
        self.story.append(Paragraph("File Tree", self.styles["Heading2"]))
        for line in tree_content.splitlines():
            line = (
                line.replace("[DIR]", "📁")
                .replace("[FILE]", "📄")
                .replace("[EXCLUDED]", "🚫")
            )
            self.story.append(Paragraph(line, self.custom_styles["FileTree"]))
        self.story.append(PageBreak())

    def add_file_sections(self, file_contents_list):
        for file_content in file_contents_list:
            match = re.match(
                r"#### 📄 (.+)\n\*\*Contents:\*\*\n(.+)", file_content, re.DOTALL
            )
            if match:
                file_path = match.group(1)
                content = match.group(2)
                section_anchor = f"section_{len(self.toc)}"
                self.toc.append((file_path, section_anchor))
                self.story.append(
                    Paragraph(
                        f'<a name="{section_anchor}">{file_path}</a>',
                        self.styles["Heading2"],
                    )
                )
                self.story.append(Spacer(1, 0.1 * inch))
                self.story.append(
                    Paragraph(
                        content.replace("\n", "<br />"),
                        self.custom_styles["FileContent"],
                    )
                )
                self.story.append(PageBreak())

    def add_table_of_contents(self):
        self.story.append(Paragraph("Table of Contents", self.styles["Heading2"]))
        toc_entries = []
        for file_path, section_anchor in self.toc:
            toc_entries.append(
                [
                    Paragraph(
                        f'<a href="#{section_anchor}">{file_path}</a>',
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


def generate_pdf(root_path, tree_content, file_contents_list):
    output_path = os.path.join(root_path, "output.pdf")
    pdf_gen = PDFGenerator(output_path)
    pdf_gen.create_pdf(tree_content, file_contents_list)


if __name__ == "__main__":
    import argparse
    from ccontext.main import load_config, print_file_tree, gather_file_contents

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

    tree_content = print_file_tree(args.root_path, excludes, includes, max_tokens)
    file_contents_list, _ = gather_file_contents(args.root_path, excludes, includes)

    generate_pdf(args.root_path, tree_content, file_contents_list)
    