import argparse
import collections
import zipfile
import xml.etree.ElementTree as ET


DEFAULT_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def extract_namespace(tag: str) -> str:
    if tag.startswith("{"):
        return tag[1:].split("}", 1)[0]
    return ""


def build_ns(root) -> dict[str, str]:
    word_ns = extract_namespace(root.tag) or DEFAULT_NS["w"]
    return {"w": word_ns, "r": DEFAULT_NS["r"]}


def qn(ns_map: dict[str, str], tag: str) -> str:
    prefix, name = tag.split(":", 1)
    uri = ns_map[prefix]
    return f"{{{uri}}}{name}"


def twips_to_in(value: str | None) -> str:
    if not value:
        return "-"
    if value.endswith("pt"):
        return f"{float(value[:-2]) / 72:.2f} in"
    return f"{float(value) / 1440:.2f} in"


def half_points_to_pt(value: str | None) -> str:
    if not value:
        return "-"
    if value.endswith("pt"):
        return f"{float(value[:-2]):.1f} pt"
    return f"{float(value) / 2:.1f} pt"


def emu_to_in(value: str | None) -> str:
    if not value:
        return "-"
    if value.endswith("pt"):
        return f"{float(value[:-2]) / 72:.2f} in"
    return f"{float(value) / 914400:.2f} in"


def page_dim_to_in(value: str | None) -> str:
    if not value:
        return "-"
    if value.endswith("pt"):
        return f"{float(value[:-2]) / 72:.2f} in"
    return f"{float(value) / 1440:.2f} in"


def load_xml(docx_path: str, member: str):
    with zipfile.ZipFile(docx_path) as zf:
        return ET.fromstring(zf.read(member))


def load_style_maps(styles_root, ns_map):
    style_id_to_name = {}
    style_id_to_type = {}
    style_props = {}

    for style in styles_root.findall("w:style", ns_map):
        style_id = style.get(qn(ns_map, "w:styleId"), "")
        style_type = style.get(qn(ns_map, "w:type"), "")
        name_el = style.find("w:name", ns_map)
        style_name = name_el.get(qn(ns_map, "w:val")) if name_el is not None else style_id
        style_id_to_name[style_id] = style_name
        style_id_to_type[style_id] = style_type

        rpr = style.find("w:rPr", ns_map)
        ppr = style.find("w:pPr", ns_map)
        fonts = {}
        size = None
        bold = False
        italic = False
        if rpr is not None:
            rfonts = rpr.find("w:rFonts", ns_map)
            if rfonts is not None:
                for key in ("ascii", "hAnsi", "eastAsia", "cs"):
                    value = rfonts.get(qn(ns_map, f"w:{key}"))
                    if value:
                        fonts[key] = value
            sz = rpr.find("w:sz", ns_map)
            if sz is not None:
                size = sz.get(qn(ns_map, "w:val"))
            bold = rpr.find("w:b", ns_map) is not None
            italic = rpr.find("w:i", ns_map) is not None
        jc = None
        keep_next = False
        if ppr is not None:
            jc_el = ppr.find("w:jc", ns_map)
            if jc_el is not None:
                jc = jc_el.get(qn(ns_map, "w:val"))
            keep_next = ppr.find("w:keepNext", ns_map) is not None
        style_props[style_id] = {
            "fonts": fonts,
            "size": size,
            "bold": bold,
            "italic": italic,
            "jc": jc,
            "keep_next": keep_next,
        }

    return style_id_to_name, style_id_to_type, style_props


def get_doc_defaults(styles_root, ns_map):
    defaults = {"fonts": {}, "size": None}
    doc_defaults = styles_root.find("w:docDefaults", ns_map)
    if doc_defaults is None:
        return defaults
    rpr_default = doc_defaults.find("w:rPrDefault/w:rPr", ns_map)
    if rpr_default is None:
        return defaults
    rfonts = rpr_default.find("w:rFonts", ns_map)
    if rfonts is not None:
        for key in ("ascii", "hAnsi", "eastAsia", "cs"):
            value = rfonts.get(qn(ns_map, f"w:{key}"))
            if value:
                defaults["fonts"][key] = value
    sz = rpr_default.find("w:sz", ns_map)
    if sz is not None:
        defaults["size"] = sz.get(qn(ns_map, "w:val"))
    return defaults


def paragraph_text(paragraph, ns_map):
    parts = []
    for node in paragraph.iter():
        if node.tag == qn(ns_map, "w:t"):
            parts.append(node.text or "")
        elif node.tag == qn(ns_map, "w:tab"):
            parts.append("\t")
        elif node.tag == qn(ns_map, "w:br"):
            parts.append("\n")
    return "".join(parts).strip()


def get_paragraph_style_id(paragraph, ns_map):
    ppr = paragraph.find("w:pPr", ns_map)
    if ppr is None:
        return None
    pstyle = ppr.find("w:pStyle", ns_map)
    if pstyle is None:
        return None
    return pstyle.get(qn(ns_map, "w:val"))


def get_run_props(run, ns_map):
    rpr = run.find("w:rPr", ns_map)
    fonts = {}
    size = None
    bold = False
    italic = False
    if rpr is not None:
        rfonts = rpr.find("w:rFonts", ns_map)
        if rfonts is not None:
            for key in ("ascii", "hAnsi", "eastAsia", "cs"):
                value = rfonts.get(qn(ns_map, f"w:{key}"))
                if value:
                    fonts[key] = value
        sz = rpr.find("w:sz", ns_map)
        if sz is not None:
            size = sz.get(qn(ns_map, "w:val"))
        bold = rpr.find("w:b", ns_map) is not None
        italic = rpr.find("w:i", ns_map) is not None
    return fonts, size, bold, italic


def analyze(docx_path: str, preview_count: int):
    document_root = load_xml(docx_path, "word/document.xml")
    styles_root = load_xml(docx_path, "word/styles.xml")
    ns_map = build_ns(document_root)
    numbering_root = None
    try:
        numbering_root = load_xml(docx_path, "word/numbering.xml")
    except KeyError:
        numbering_root = None

    style_id_to_name, style_id_to_type, style_props = load_style_maps(styles_root, ns_map)
    doc_defaults = get_doc_defaults(styles_root, ns_map)

    body = document_root.find("w:body", ns_map)
    paragraphs = body.findall("w:p", ns_map) if body is not None else []
    tables = body.findall("w:tbl", ns_map) if body is not None else []

    style_counter = collections.Counter()
    font_counter = collections.Counter()
    size_counter = collections.Counter()
    combo_counter = collections.Counter()
    nonempty = []

    for p in paragraphs:
        text = paragraph_text(p, ns_map)
        style_id = get_paragraph_style_id(p, ns_map)
        style_name = style_id_to_name.get(style_id, style_id or "Normal")
        if text:
            style_counter[style_name] += 1
            if len(nonempty) < preview_count:
                nonempty.append((style_name, text))

        for run in p.findall("w:r", ns_map):
            run_text = "".join(t.text or "" for t in run.findall("w:t", ns_map)).strip()
            if not run_text:
                continue
            fonts, size, bold, italic = get_run_props(run, ns_map)
            font_name = fonts.get("ascii") or fonts.get("hAnsi") or "(inherit)"
            font_counter[font_name] += 1
            size_counter[half_points_to_pt(size)] += 1
            combo_counter[(font_name, half_points_to_pt(size), bold, italic)] += 1

    sect_pr = body.find("w:sectPr", ns_map) if body is not None else None
    if sect_pr is None and paragraphs:
        last_ppr = paragraphs[-1].find("w:pPr", ns_map)
        if last_ppr is not None:
            sect_pr = last_ppr.find("w:sectPr", ns_map)
    pg_sz = sect_pr.find("w:pgSz", ns_map) if sect_pr is not None else None
    pg_mar = sect_pr.find("w:pgMar", ns_map) if sect_pr is not None else None
    cols = sect_pr.find("w:cols", ns_map) if sect_pr is not None else None

    print(f"FILE: {docx_path}")
    print("=" * 80)
    print(f"Paragraphs: {len(paragraphs)}")
    print(f"Tables: {len(tables)}")
    print("DOC DEFAULTS")
    print(f"  Fonts: {doc_defaults['fonts'] or '-'}")
    print(f"  Size: {half_points_to_pt(doc_defaults['size'])}")
    print("SECTION")
    if pg_sz is not None:
        print(
            "  Page size: "
            f"{page_dim_to_in(pg_sz.get(qn(ns_map, 'w:w')))} x {page_dim_to_in(pg_sz.get(qn(ns_map, 'w:h')))}"
        )
    if pg_mar is not None:
        print(
            "  Margins: "
            f"top={twips_to_in(pg_mar.get(qn(ns_map, 'w:top')))}, "
            f"bottom={twips_to_in(pg_mar.get(qn(ns_map, 'w:bottom')))}, "
            f"left={twips_to_in(pg_mar.get(qn(ns_map, 'w:left')))}, "
            f"right={twips_to_in(pg_mar.get(qn(ns_map, 'w:right')))}"
        )
    if cols is not None:
        print(
            "  Columns: "
            f"num={cols.get(qn(ns_map, 'w:num'), '1')}, space={twips_to_in(cols.get(qn(ns_map, 'w:space')))}"
        )

    print("TOP PARAGRAPH STYLES")
    for name, count in style_counter.most_common(15):
        print(f"  {name}: {count}")

    print("TOP RUN FONTS")
    for name, count in font_counter.most_common(10):
        print(f"  {name}: {count}")

    print("TOP RUN SIZES")
    for name, count in size_counter.most_common(10):
        print(f"  {name}: {count}")

    print("TOP RUN STYLE COMBINATIONS")
    for (font_name, size, bold, italic), count in combo_counter.most_common(12):
        flags = []
        if bold:
            flags.append("bold")
        if italic:
            flags.append("italic")
        flag_text = ", ".join(flags) if flags else "plain"
        print(f"  {font_name} | {size} | {flag_text}: {count}")

    print("KEY STYLE DEFINITIONS")
    key_names = {
        "Title",
        "Subtitle",
        "Author",
        "Abstract",
        "Keywords",
        "Heading 1",
        "Heading 2",
        "Heading 3",
        "Normal",
    }
    for style_id, name in style_id_to_name.items():
        if name in key_names:
            props = style_props.get(style_id, {})
            print(
                f"  {name}: fonts={props.get('fonts') or '-'}, "
                f"size={half_points_to_pt(props.get('size'))}, "
                f"bold={props.get('bold')}, italic={props.get('italic')}, "
                f"align={props.get('jc') or '-'}"
            )

    print("PARAGRAPH PREVIEW")
    for idx, (style_name, text) in enumerate(nonempty, start=1):
        preview = text.replace("\n", " ")
        if len(preview) > 180:
            preview = preview[:177] + "..."
        print(f"  {idx:02d}. [{style_name}] {preview}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("docx_path")
    parser.add_argument("--preview", type=int, default=40)
    args = parser.parse_args()
    analyze(args.docx_path, args.preview)


if __name__ == "__main__":
    main()
