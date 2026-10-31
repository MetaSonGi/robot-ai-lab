"""site/index.fragment.html → docs/index.html (GitHub Pages 용 완성 HTML)"""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
body = (root / "site" / "index.fragment.html").read_text(encoding="utf-8")
html = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        + body + '\n</html>\n')
(root / "docs" / "index.html").write_text(html, encoding="utf-8")
print("docs/index.html 생성")
