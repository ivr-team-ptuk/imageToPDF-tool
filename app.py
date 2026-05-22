import streamlit as st
import fitz
import io

from PIL import Image
from streamlit_sortables import sort_items

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="تحويل الصور إلى PDF - IVR",
    layout="wide"
)

# =========================
# LOAD CSS
# =========================

with open("styles/style.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )
    
    
# =========================
# HEADER
# =========================

st.title("تحويل الصور إلى PDF")
st.caption("ارفع الصور ثم قم بترتيبها وتحويلها إلى PDF")

# =========================
# LAYOUT
# =========================

controls_col, preview_col = st.columns(
    [1, 1.2],
    gap="large"
)

# ROW 1 - NAVBAR
st.markdown("""
<div class="ivr-navbar">
    <a href="https://ivr-home.streamlit.app" target="_blank">Home</a>
    <a href="https://ivr-merge-tool.streamlit.app" target="_blank">Merge PDF</a>
    <a href="https://ivr-imagetopdf-tool.streamlit.app" target="_blank">Image to PDF</a>
</div>
""", unsafe_allow_html=True)

# =========================
# CONTROLS
# =========================

with controls_col:

    # =========================
    # UPLOAD IMAGES
    # =========================

    uploaded_images = st.file_uploader(
        "رفع الصور",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="يمكنك رفع عدة صور دفعة واحدة"
    )

    # =========================
    # MAIN
    # =========================

    if uploaded_images:

        st.markdown("### ترتيب الصور")

        image_names = [
            image.name
            for image in uploaded_images
        ]

        sorted_names = sort_items(
            image_names,
            direction="vertical"
        )

        st.divider()

        # =========================
        # PAGE SIZE
        # =========================

        page_size = st.selectbox(
            "حجم الصفحة",
            [
                "A4",
                "Letter",
                "Auto"
            ]
        )

        # =========================
        # ORIENTATION
        # =========================

        orientation = st.selectbox(
            "اتجاه الصفحة",
            [
                "Portrait",
                "Landscape",
                "Auto"
            ]
        )

        # =========================
        # BOOKMARKS
        # =========================

        add_bookmarks = st.checkbox(
            "إضافة علامات مرجعية",
            value=True
        )

        bookmark_titles = {}

        if add_bookmarks:

            st.markdown("### أسماء العلامات المرجعية")

            for image_name in sorted_names:

                clean_name = image_name.rsplit(".", 1)[0]

                bookmark_titles[image_name] = st.text_input(
                    f"علامة: {image_name}",
                    value=clean_name
                )

        # =========================
        # OUTPUT NAME
        # =========================

        output_name = st.text_input(
            "اسم الملف النهائي",
            value="images_pdf"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# PREVIEW
# =========================

with preview_col:

    st.subheader("المعاينة المباشرة")

    if uploaded_images:

        try:

            preview_names = sorted_names

            preview_index = st.slider(
                "التنقل بين الصور",
                min_value=1,
                max_value=len(preview_names),
                value=1
            )

            preview_index = st.number_input(
                "رقم الصورة",
                min_value=1,
                max_value=len(preview_names),
                value=preview_index,
                step=1
            )

            selected_name = preview_names[
                preview_index - 1
            ]

            selected_image = None

            for img in uploaded_images:

                if img.name == selected_name:

                    selected_image = img
                    break

            if selected_image:

                image = Image.open(
                    io.BytesIO(
                        selected_image.getvalue()
                    )
                )

                st.image(
                    image,
                    caption=selected_name,
                    use_container_width=True
                )

        except Exception as e:

            st.error(f"خطأ في المعاينة: {e}")

    else:

        st.info("قم برفع الصور لرؤية المعاينة.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# CREATE PDF
# =========================

with controls_col:

    st.markdown("<br>", unsafe_allow_html=True)

    if uploaded_images:

        if st.button("إنشاء وتحميل"):

            pdf_doc = fitz.open()

            toc = []

            current_page = 1

            progress = st.progress(0)

            total = len(sorted_names)

            for index, selected_name in enumerate(sorted_names):

                for uploaded_image in uploaded_images:

                    if uploaded_image.name == selected_name:

                        # =========================
                        # LOAD IMAGE
                        # =========================

                        original_bytes = uploaded_image.getvalue()

                        image = Image.open(
                            io.BytesIO(original_bytes)
                        )

                        # =========================
                        # CONVERT RGBA → RGB
                        # =========================

                        if image.mode in ("RGBA", "P"):

                            image = image.convert("RGB")

                        # =========================
                        # COMPRESS IMAGE
                        # =========================

                        compressed_buffer = io.BytesIO()

                        image.save(
                            compressed_buffer,
                            format="JPEG",
                            quality=92,
                            optimize=True
                        )

                        compressed_bytes = (
                            compressed_buffer.getvalue()
                        )

                        width, height = image.size

                        # =========================
                        # PAGE SIZE
                        # =========================

                        if page_size == "A4":

                            page_width = 595
                            page_height = 842

                        elif page_size == "Letter":

                            page_width = 612
                            page_height = 792

                        else:

                            page_width = width
                            page_height = height

                        # =========================
                        # ORIENTATION
                        # =========================

                        if orientation == "Landscape":

                            if page_height > page_width:

                                page_width, page_height = (
                                    page_height,
                                    page_width
                                )

                        elif orientation == "Portrait":

                            if page_width > page_height:

                                page_width, page_height = (
                                    page_height,
                                    page_width
                                )

                        # =========================
                        # CREATE PAGE
                        # =========================

                        page = pdf_doc.new_page(
                            width=page_width,
                            height=page_height
                        )

                        rect = fitz.Rect(
                            0,
                            0,
                            page_width,
                            page_height
                        )

                        page.insert_image(
                            rect,
                            stream=compressed_bytes,
                            keep_proportion=True
                        )

                        # =========================
                        # BOOKMARKS
                        # =========================

                        if add_bookmarks:

                            toc.append([
                                1,
                                bookmark_titles[selected_name],
                                current_page
                            ])

                        current_page += 1

                        break

                progress.progress(
                    (index + 1) / total
                )

            # =========================
            # APPLY TOC
            # =========================

            if add_bookmarks and toc:

                pdf_doc.set_toc(toc)

            # =========================
            # SAVE PDF
            # =========================

            output_buffer = io.BytesIO()

            pdf_doc.save(output_buffer)

            output_buffer.seek(0)

            pdf_doc.close()

            # =========================
            # DOWNLOAD
            # =========================

            st.download_button(
                label="تحميل ملف PDF",
                data=output_buffer,
                file_name=f"{output_name}.pdf",
                mime="application/pdf"
            )

            st.success("تم إنشاء ملف PDF بنجاح 🔥")