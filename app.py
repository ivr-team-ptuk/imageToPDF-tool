import streamlit as st
import fitz
import io
import zipfile
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="تحويل ملفات PDF - IVR",
    page_icon="Black_Square-01.svg",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================

LOGO_URL = (
    "https://raw.githubusercontent.com/ivr-team-ptuk/home-page/refs/heads/main/Black_Square-01.svg"
)

IMAGE_ACCEPT = ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "webp", "gif", "heic", "heif"]

OUTPUT_FORMATS = ["PNG", "JPG", "JPEG", "BMP", "TIFF", "WEBP"]

# =========================
# CSS
# =========================

with open("styles/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# NAVBAR
# =========================

st.markdown(f"""
<nav class="ivr-navbar">
    <a href="https://ivr-home-page.streamlit.app" class="nav-logo">
        <img src="{LOGO_URL}" class="nav-logo-img" alt="IVR">
    </a>
    <div class="nav-links">
        <a href="https://ivr-watermark-tool.streamlit.app">تعليم الملفات</a>
        <a href="https://ivr-merge-tool.streamlit.app">دمج الملفات</a>
        <a href="https://ivr-imagetopdf-tool.streamlit.app">الصور إلى PDF</a>
    </div>
</nav>
""", unsafe_allow_html=True)

# =========================
# PAGE HEADER
# =========================

st.markdown(f"""
<div class="page-header">
    <img src="{LOGO_URL}" class="hero-logo" alt="IVR Logo">
    <h1>تحويل ملفات PDF</h1>
    <p>حوّل الصور إلى PDF أو حوّل صفحات PDF إلى صور بتنسيقات متعددة</p>
</div>
""", unsafe_allow_html=True)

# =========================
# DIRECTION TABS
# =========================

mode = st.radio(
    "اختر اتجاه التحويل",
    ["🖼️  صور  ←  PDF", "📄  PDF  ←  صور"],
    horizontal=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================

controls_col, preview_col = st.columns([1, 1.1])

# =========================================================
# MODE A — Images → PDF
# =========================================================

if mode.startswith("🖼️"):

    with controls_col:

        uploaded_images = st.file_uploader(
            "اسحب الصور هنا أو اضغط للاختيار",
            type=IMAGE_ACCEPT,
            accept_multiple_files=True,
            help="يمكنك رفع عدة صور دفعة واحدة"
        )

        if uploaded_images:

            st.caption(f"عدد الصور المرفوعة: **{len(uploaded_images)}**")
            st.divider()

            page_size = st.selectbox(
                "حجم الصفحة",
                ["A4 (210×297 مم)", "A3 (297×420 مم)", "Letter (216×279 مم)", "مطابق لحجم الصورة"],
                index=0
            )

            fit_mode = st.selectbox(
                "طريقة ملء الصفحة",
                ["ملء الصفحة مع الحفاظ على النسبة", "تمديد لملء الصفحة كاملاً"],
                index=0
            )

            output_name = st.text_input(
                "اسم الملف النهائي",
                value="converted_file"
            )

            if st.button("تحويل وتحميل"):

                # page size presets in points (1 pt = 1/72 inch)
                sizes = {
                    "A4 (210×297 مم)":      fitz.paper_rect("a4"),
                    "A3 (297×420 مم)":      fitz.paper_rect("a3"),
                    "Letter (216×279 مم)":  fitz.paper_rect("letter"),
                }

                merged_doc = fitz.open()
                progress   = st.progress(0)

                for i, img_file in enumerate(uploaded_images):

                    img = Image.open(img_file).convert("RGB")
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    if page_size.startswith("مطابق"):
                        w_pt = img.width  * 0.75   # px → pt (96dpi)
                        h_pt = img.height * 0.75
                        rect = fitz.Rect(0, 0, w_pt, h_pt)
                    else:
                        rect = sizes[page_size]

                    page = merged_doc.new_page(
                        width=rect.width,
                        height=rect.height
                    )

                    if fit_mode.startswith("ملء"):
                        img_w = img.width
                        img_h = img.height
                        scale = min(rect.width / img_w, rect.height / img_h)
                        new_w = img_w * scale
                        new_h = img_h * scale
                        x0 = (rect.width  - new_w) / 2
                        y0 = (rect.height - new_h) / 2
                        place = fitz.Rect(x0, y0, x0 + new_w, y0 + new_h)
                    else:
                        place = rect

                    page.insert_image(place, stream=img_bytes.read())
                    progress.progress((i + 1) / len(uploaded_images))

                buf = io.BytesIO()
                merged_doc.save(buf)
                merged_doc.close()
                buf.seek(0)

                st.download_button(
                    label="تحميل ملف PDF",
                    data=buf,
                    file_name=f"{output_name}.pdf",
                    mime="application/pdf"
                )

                st.success("تم التحويل بنجاح 🔥")

        else:
            st.info("قم برفع صور أولاً.")

    with preview_col:

        st.subheader("معاينة الصور")

        if uploaded_images:
            try:
                img = Image.open(uploaded_images[0])
                st.image(img, use_container_width=True, caption=uploaded_images[0].name)
            except Exception as e:
                st.error(f"خطأ في المعاينة: {e}")
        else:
            st.info("قم برفع صور لرؤية المعاينة.")

# =========================================================
# MODE B — PDF → Images
# =========================================================

else:

    with controls_col:

        uploaded_pdf = st.file_uploader(
            "اسحب ملف PDF هنا أو اضغط للاختيار",
            type=["pdf"],
            accept_multiple_files=False,
            help="ملف PDF واحد فقط"
        )

        if uploaded_pdf:

            _doc = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
            total_pages = len(_doc)
            _doc.close()

            st.caption(f"إجمالي الصفحات: **{total_pages}**")
            st.divider()

            out_fmt = st.selectbox(
                "تنسيق الصور الناتجة",
                OUTPUT_FORMATS,
                index=0
            )

            dpi = st.slider(
                "جودة الصورة (DPI)",
                min_value=72,
                max_value=300,
                value=150,
                step=1
            )

            c1, c2 = st.columns(2)
            with c1:
                from_p = st.number_input(
                    "من صفحة", min_value=1, max_value=total_pages, value=1
                )
            with c2:
                to_p = st.number_input(
                    "إلى صفحة", min_value=1, max_value=total_pages, value=total_pages
                )

            if st.button("تحويل وتحميل"):

                if int(from_p) > int(to_p):
                    st.error("صفحة البداية يجب أن تكون أصغر أو تساوي صفحة النهاية.")
                else:
                    scale  = dpi / 72
                    matrix = fitz.Matrix(scale, scale)

                    zip_buf  = io.BytesIO()
                    doc      = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
                    pages    = range(int(from_p) - 1, int(to_p))
                    progress = st.progress(0)

                    fmt_lower = out_fmt.lower()
                    pil_fmt   = "JPEG" if fmt_lower in ("jpg", "jpeg") else fmt_lower.upper()

                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for idx, p_idx in enumerate(pages):
                            page = doc[p_idx]
                            pix  = page.get_pixmap(matrix=matrix)
                            img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            ibuf = io.BytesIO()
                            img.save(ibuf, format=pil_fmt)
                            ibuf.seek(0)
                            zf.writestr(f"page_{p_idx + 1}.{fmt_lower}", ibuf.read())
                            progress.progress((idx + 1) / len(pages))

                    doc.close()
                    zip_buf.seek(0)

                    st.download_button(
                        label="تحميل الصور (ZIP)",
                        data=zip_buf,
                        file_name="pdf_pages.zip",
                        mime="application/zip"
                    )

                    st.success("تم التحويل بنجاح 🔥")

        else:
            st.info("قم برفع ملف PDF أولاً.")

    with preview_col:

        st.subheader("المعاينة")

        if uploaded_pdf:

            try:
                preview_doc = fitz.open(
                    stream=uploaded_pdf.getvalue(),
                    filetype="pdf"
                )
                total_pages = len(preview_doc)

                if total_pages > 1:
                    page_num = st.slider(
                        "الصفحة",
                        min_value=1,
                        max_value=total_pages,
                        value=1
                    )
                else:
                    page_num = 1
                    st.caption("الملف يحتوي على صفحة واحدة فقط")

                page = preview_doc[page_num - 1]
                pix  = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                st.image(pix.tobytes("png"), use_container_width=True)
                preview_doc.close()

            except Exception as e:
                st.error(f"خطأ في المعاينة: {e}")

        else:
            st.info("قم برفع ملف لرؤية المعاينة.")

# =========================
# FOOTER
# =========================

st.markdown(
    '<div class="footer">IVR Engineering Society © 2026</div>',
    unsafe_allow_html=True
)
