"""
CSS constants and HTML templates for Bionic Reader.
"""

DEFAULT_FONT_FAMILY = "Arial"

HTML_HEAD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Bionic PDF</title>
  <style>
    @page {{
      size: Letter;
      margin: 1in;
      margin-right: 1.5in;
    }}
    body {{ font-family: {font_family}, sans-serif; font-size: {font_size}; margin: 0; padding: 0; background: white; }}
    .page {{ width: 100%; box-sizing: border-box; }}
    .bionic-prefix {{ font-weight: 700; }}
    .bionic-rest {{ font-weight: 400; }}
    img {{ max-width: 100%; height: auto; display: block; }}
    .paragraph {{ margin-bottom: 0.5em; }}
    .image-container {{ position: relative; margin: 1em 0; text-align: center; clear: both; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 1em; }}
    td {{ vertical-align: top; padding: 4px; }}
  </style>
</head>
<body>
<div class="page">
"""

HTML_TAIL = """
</div>
</body>
</html>
"""
