import streamlit as st
import fitz
import io
from PIL import Image
from pillow_heif import register_heif_opener
from streamlit_sortables import sort_items

register_heif_opener()

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="تحويل الصور إلى PDF - IVR",
    page_icon="Black_Square-01.svg",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================

LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "ivr-team-ptuk/home-page/main/Black_Square-01.svg"
)

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
    <h1>تحويل الصور إلى PDF</h1>
    <p>ارفع الصور ثم قم بترتيبها وتحويلها إلى PDF</p>
</div>
""", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================

controls_col, preview_col = st.columns([1, 1.2], gap="large")

# =========================
# LEFT COLUMN — CONTROLS
# =========================

with controls_col:

    uploaded_images = st.file_uploader(
        "اسحب الصور هنا أو اضغط للاختيار",
        type=["png", "jpg", "jpeg", "webp", "heic", "heif", "bmp", "tiff", "gif"],
        accept_multiple_files=True,
        help="يمكنك رفع عدة صور دفعة واحدة"
    )

    if uploaded_images:

        st.subheader("ترتيب الصور")

        sorted_names = sort_items(
            [img.name for img in uploaded_images],
            direction="vertical"
        )

        st.divider()

        page_size = st.selectbox(
            "حجم الصفحة",
            ["A4", "Letter", "Auto"]
        )

        orientation = st.selectbox(
            "اتجاه الصفحة",
            ["Portrait", "Landscape", "Auto"]
        )

        add_bookmarks = st.checkbox(
            "إضافة علامات مرجعية",
            value=True
        )

        bookmark_titles = {}

        if add_bookmarks:

            st.subheader("أسماء العلامات المرجعية")

            for name in sorted_names:
                bookmark_titles[name] = st.text_input(
                    f"علامة: {name}",
                    value=name.rsplit(".", 1)[0]
                )

        output_name = st.text_input(
            "اسم الملف النهائي",
            value="images_pdf"
        )

    else:
        st.info("قم برفع الصور أولاً.")

# =========================
# RIGHT COLUMN — PREVIEW
# =========================

with preview_col:

    st.subheader("المعاينة المباشرة")

    if uploaded_images:

        try:

            image_map = {img.name: img for img in uploaded_images}

            preview_index = st.slider(
                "التنقل بين الصور",
                min_value=1,
                max_value=len(sorted_names),
                value=1
            )

            selected = image_map.get(sorted_names[preview_index - 1])

            if selected:
                image = Image.open(io.BytesIO(selected.getvalue()))
                st.image(image, caption=selected.name, use_container_width=True)

        except Exception as e:
            st.error(f"خطأ في المعاينة: {e}")

    else:
        st.info("قم برفع الصور لرؤية المعاينة.")

# =========================
# CREATE PDF — back in left column
# =========================

with controls_col:

    if uploaded_images:

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("إنشاء وتحميل"):

            image_map = {img.name: img for img in uploaded_images}
            pdf_doc   = fitz.open()
            toc          = []
            current_page = 1
            progress     = st.progress(0)

            for i, name in enumerate(sorted_names):

                if name not in image_map:
                    continue

                image = Image.open(io.BytesIO(image_map[name].getvalue()))

                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")

                buf = io.BytesIO()
                image.save(buf, format="JPEG", quality=92, optimize=True)
                compressed = buf.getvalue()

                img_w, img_h = image.size

                # Page dimensions
                if page_size == "A4":
                    page_w, page_h = 595, 842
                elif page_size == "Letter":
                    page_w, page_h = 612, 792
                else:
                    page_w, page_h = img_w, img_h

                # Orientation
                if orientation == "Landscape" and page_h > page_w:
                    page_w, page_h = page_h, page_w
                elif orientation == "Portrait" and page_w > page_h:
                    page_w, page_h = page_h, page_w

                page = pdf_doc.new_page(width=page_w, height=page_h)
                page.insert_image(
                    fitz.Rect(0, 0, page_w, page_h),
                    stream=compressed,
                    keep_proportion=True
                )

                if add_bookmarks:
                    toc.append([1, bookmark_titles.get(name, name), current_page])

                current_page += 1
                progress.progress((i + 1) / len(sorted_names))

            if add_bookmarks and toc:
                pdf_doc.set_toc(toc)

            output_buf = io.BytesIO()
            pdf_doc.save(output_buf)
            pdf_doc.close()
            output_buf.seek(0)

            st.download_button(
                label="تحميل ملف PDF",
                data=output_buf,
                file_name=f"{output_name}.pdf",
                mime="application/pdf"
            )

            st.success("تم إنشاء ملف PDF بنجاح 🔥")

# =========================
# FOOTER
# =========================

st.markdown(
    '<div class="footer">IVR Engineering Society © 2026</div>',
    unsafe_allow_html=True
)
