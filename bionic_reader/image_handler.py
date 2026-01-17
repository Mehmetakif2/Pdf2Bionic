import io
import base64
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from .utils import get_logger

MAX_IMAGE_WIDTH = 1200
IMAGE_JPEG_QUALITY = 75

def process_single_image(image_data: bytes, rel_id: str) -> tuple:
    """
    Process a single image: resize and compress.
    Returns (rel_id, base64_string).
    """
    logger = get_logger()
    try:
        # Decode
        image = Image.open(io.BytesIO(image_data))
        
        # Check for transparency / mode
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
             # Keep PNG for transparency, but still resize if huge
             format_type = "PNG"
        else:
             image = image.convert("RGB")
             format_type = "JPEG"

        width, height = image.size
        # Resize if too large
        if width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / float(width)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        
        buf = io.BytesIO()
        if format_type == "JPEG":
            image.save(buf, format="JPEG", quality=IMAGE_JPEG_QUALITY, optimize=True)
            mime_type = "image/jpeg"
        else:
            image.save(buf, format="PNG", optimize=True)
            mime_type = "image/png"
            
        final_data = buf.getvalue()
        encoded = base64.b64encode(final_data).decode('utf-8')
        return rel_id, f"data:{mime_type};base64,{encoded}"
        
    except Exception as e:
        logger.warning(f"Failed to process image {rel_id}: {e}")
        return rel_id, None

def extract_images_from_doc(doc) -> dict:
    """
    Extract images from a docx Document object.
    
    Returns:
        dict: rId -> data_url
    """
    logger = get_logger()
    logger.debug("Extracting images from DOCX...")
    
    # Collect all image parts
    tasks = []
    
    # We iterate over relationships to find images
    # Note: doc.part.rels is a dictionary
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
             tasks.append((rel.target_part.blob, rel.rId))

    if not tasks:
        return {}
        
    results = {}
    
    # Parallelize compression for speed
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_single_image, blob, rid) for blob, rid in tasks]
        for f in futures:
            rid, data_url = f.result()
            if data_url:
                results[rid] = data_url
                
    logger.info(f"Extracted and processed {len(results)} images.")
    return results

def get_image_position(element):
    """
    Extract image position from XML element if available (floating images).
    """
    try:
        ns_wp = {'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
        anchor = element.find('.//wp:anchor', ns_wp)
        if anchor is not None:
            pos_h = anchor.find('.//wp:positionH', ns_wp)
            pos_v = anchor.find('.//wp:positionV', ns_wp)
            if pos_h is not None and pos_v is not None:
                x_node = pos_h.find('.//wp:posOffset', ns_wp)
                y_node = pos_v.find('.//wp:posOffset', ns_wp)
                if x_node is not None and y_node is not None:
                    # EMUs to Inches (1 inch = 914400 EMUs)
                    return {'x': int(x_node.text) / 914400, 'y': int(y_node.text) / 914400}
    except Exception:
        pass
    return None
