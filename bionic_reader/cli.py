import argparse
import sys
import os
from .utils import setup_logging, get_logger

def parse_args():
    parser = argparse.ArgumentParser(description="Convert PDF to Bionic Reading formatted PDF")
    parser.add_argument("--input", "-i", required=True, help="Input PDF file")
    parser.add_argument("--output", "-o", help="Output PDF file (default: input_bionic.pdf)")
    parser.add_argument("--bold-ratio", "-b", type=float, default=0.5, help="Ratio of word to bold (0.0-1.0)")
    parser.add_argument("--font", "-f", default="Arial", help="Font family to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    args = parse_args()
    logger = setup_logging(args.verbose)
    
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    if not args.output:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_bionic.pdf"
    else:
        output_path = os.path.abspath(args.output)
        
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")

    try:
        from .converter import pdf_to_html
        from .processor import apply_bionic_reading
        from .renderer import render_pdf
        
        # 1. Convert PDF to HTML chunks
        logger.info("Step 1: Converting PDF to HTML chunks and applying Bionic Reading...")
        html_chunks = pdf_to_html(input_path, font_family=args.font, bold_ratio=args.bold_ratio)
        
        # 3. Render to PDF
        logger.info("Step 3: Rendering final PDF (Parallel)...")
        render_pdf(html_chunks, output_path)
        
        logger.info(f"Success! Output saved to: {output_path}")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
