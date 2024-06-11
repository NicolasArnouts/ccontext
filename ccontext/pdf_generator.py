from fpdf import FPDF
import os
import re


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Directory and File Contents", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_tree_section(self, tree_content):
        self.add_page()
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "File Tree", 0, 1, "L")
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, tree_content)

    def add_file_section(self, file_path, file_content):
        self.add_page()
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, file_path, 0, 1, "L")
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, file_content)

    def add_toc(self, toc):
        self.add_page()
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Table of Contents", 0, 1, "L")
        self.set_font("Arial", "", 12)
        for item in toc:
            self.cell(0, 10, item, 0, 1, "L")


def generate_pdf(root_path, tree_content, file_contents_list):
    pdf = PDF()
    pdf.add_font(
        "Arial", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True
    )
    pdf.add_font(
        "Arial", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True
    )
    pdf.add_font(
        "Arial",
        "I",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        uni=True,
    )
    pdf.set_auto_page_break(auto=True, margin=15)

    toc = ["File Tree"]

    # Add file tree section
    pdf.add_tree_section(tree_content)

    # Add file content sections
    for file_content in file_contents_list:
        match = re.match(
            r"#### 📄 (.+)\n\*\*Contents:\*\*\n(.+)", file_content, re.DOTALL
        )
        if match:
            file_path = match.group(1)
            content = match.group(2)
            toc.append(file_path)
            pdf.add_file_section(file_path, content)
        else:
            toc.append("Unknown file format")

    # Add table of contents
    pdf.add_toc(toc)

    output_path = os.path.join(root_path, "output.pdf")
    pdf.output(output_path)

    print(f"PDF generated at {output_path}")


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
    