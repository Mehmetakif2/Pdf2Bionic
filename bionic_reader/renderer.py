import multiprocessing
import tempfile
import os
import fitz  # PyMuPDF
from weasyprint import HTML
from .utils import get_logger

def render_chunk(html_content):
    """
    Worker function to render a single HTML chunk to a temporary PDF file.
    Returns the path to the temporary PDF.
    """
    try:
        # Create a temp file manually to ensure it's closed and accessible
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        HTML(string=html_content).write_pdf(temp_path)
        return temp_path
    except Exception as e:
        # We can't log easily to the main logger from here without setup, 
        # so we print or re-raise
        print(f"Error in worker: {e}")
        return None

def render_pdf(html_chunks, output_path):
    """
    Render a list of HTML strings to a single PDF file using parallel processing.
    """
    logger = get_logger()
    logger.info(f"Rendering {len(html_chunks)} chunks in parallel...")

    # If it's a single string, wrap it in a list (backward compatibility)
    if isinstance(html_chunks, str):
        html_chunks = [html_chunks]

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    
    try:
        # Render chunks in parallel
        temp_pdfs = pool.map(render_chunk, html_chunks)
        
        # Check for failures
        if any(p is None for p in temp_pdfs):
            raise Exception("One or more chunks failed to render.")

        logger.info("Merging chunks...")
        doc = fitz.open()
        
        for temp_pdf in temp_pdfs:
            with fitz.open(temp_pdf) as part:
                doc.insert_pdf(part)
            # Remove temp file
            try:
                os.remove(temp_pdf)
            except OSError:
                pass
                
        doc.save(output_path)
        doc.close()
        
        logger.info("PDF generation successful.")
        return True
        
    except Exception as e:
        logger.error(f"Failed to render PDF: {e}")
        raise
    finally:
        pool.close()
        pool.join()
