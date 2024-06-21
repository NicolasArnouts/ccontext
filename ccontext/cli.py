from ccontext.argument_parser import parse_arguments
from ccontext.main import main as actual_main


def main():
    args = parse_arguments()
    actual_main(
        root_path=args.root_path,
        excludes=args.excludes,
        includes=args.includes,
        max_tokens=args.max_tokens,
        config_path=args.config,
        verbose=args.verbose,
        ignore_gitignore=args.ignore_gitignore,
        generate_pdf_flag=args.generate_pdf,
        generate_md_flag=args.generate_md,
        crawl_flag=args.crawl_flag,
    )
