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
# LAYOUT
# =========================

# ROW 1 - NAVBAR
st.markdown("""
<div class="ivr-navbar">
    <a href="https://ivr-home.streamlit.app" target="_blank">Home</a>
    <a href="https://ivr-merge-tool.streamlit.app" target="_blank">Merge PDF</a>
    <a href="https://ivr-watermark-tool.streamlit.app" target="_blank">Watermark PDF</a>
    <a href="https://ivr-imagetopdf-tool.streamlit.app" target="_blank">Image to PDF</a>
    <svg xmlns="http://www.w3.org/2000/svg" id="svg1" viewBox="0 0 50 30"><defs><style>.cls-1 {stroke-width: 0px;}.cls-1, .cls-2 {fill: #000;}.cls-3, .cls-2 {isolation: isolate;}.cls-2 {font-family: Arial-BoldMT, Arial;font-size: 5.36px;font-weight: 700;}</style></defs><g id="g1"><g id="g15"><path id="path14" class="cls-1" d="M107.91,7.49c-.47.79-.97,1.62-1.52,2.49-.51.87-.97,1.7-1.41,2.49-.51.83-.98,1.68-1.41,2.54-.43.83-.9,1.68-1.41,2.54l-1.95,3.63c-.61,1.15-1.3,2.4-2.06,3.73-.72,1.3-1.39,2.47-2,3.52l-11.64-20.89h-9.31c1.05,1.84,2.07,3.68,3.09,5.52,1.01,1.84,2.04,3.66,3.09,5.47.72,1.23,1.42,2.47,2.11,3.73.72,1.26,1.44,2.51,2.17,3.73l10.39,18.46,15.91-29.01h17.66c.9,0,1.68.32,2.33.97.69.65,1.03,1.48,1.03,2.49v2.06c0,.94-.34,1.77-1.03,2.49-.65.72-1.43,1.08-2.33,1.08h-18.35v20.57h7.79v-12.83h4.87l7.96,12.83h9.2l-8.12-13.26c1.19-.43,2.27-1.03,3.25-1.79.97-.76,1.8-1.62,2.49-2.6s1.21-2,1.57-3.09c.4-1.12.6-2.26.6-3.41v-2.06c0-1.59-.31-3.07-.92-4.44-.58-1.37-1.37-2.56-2.38-3.57-1.01-1.05-2.2-1.86-3.57-2.44-1.37-.61-2.83-.92-4.38-.92h-14.39c-.28-.03-.55-.05-.83-.05h-6.49Z"/><path id="path15" class="cls-1" d="M64.17,7.54v37.56h7.96V7.54h-7.96Z"/><g id="text15-6" class="cls-3"><text class="cls-2" transform="translate(137.75 8.92)"><tspan x="0" y="0">©</tspan></text></g></g><g id="g23"><path id="path20" class="cls-1" d="M.81,32.39c-.43.06-.77.38-.81.77v8.99c.15,3.96,2.33,7.56,5.77,9.53,1.09.59,2.27,1.01,3.49,1.22h12.8c.89-.12,1.21-.98,1.31-1.34v-.11s.73-9.39.73-9.39l.24-3.11c-.05-.15.14-.57.28-.85.93.02,1.84.23,2.69.61,1.13.49,3.6,2.47,4.12,5.52.04.28.06.57.06.86h0c.19,2.07.27,4.05.41,6.12,0,.93.62,1.68,1.39,1.69h12.49c.5,0,.91-.42.91-.92,0-.27-.13-.53-.34-.71l-.05-.05-12.7-11.52-2.29-2.08-.32-.29-2.27-2.06-.29-.26c-.57-.46-1.26-.77-1.99-.89l-.72-.05-.97-.07-1.8-.12-3.24-.22-1.56-.11-13.63-.93-3.21-.22-.48-.03Z"/><path id="path4" class="cls-1" d="M11.61,0C6.1.09,1.42,4.07.46,9.51c-.04.24-.07.48-.1.73v19.54c.01.47.4.85.87.86l.52-.16,13.66-4.33,2.52-.8,6.17-1.96,1.22-.39c.98-.45,1.43-1.39,2.02-2.25l2.63-3.85.81-1.19.55-.81L40.7,1.16l.29-.43s.02-.09.02-.13c0-.15-.07-.3-.17-.41-.09-.09-.21-.16-.34-.19H11.61Z"/><path id="path5" class="cls-1" d="M43.08,0c-.36.13-.66.38-.87.71l-.21.96-3.75,16.95-.72,3.26-.74,3.33-.25,1.11c-.09.59-.08,1.2.04,1.81l1.35,2.76.25.51,1.79,3.65c2.88,5.22,4.92,10.95,7.89,16.11.17.17.4.26.64.27.15-.02.29-.08.41-.17.11-.08.21-.17.31-.26,2.49-2.14,3.94-5.25,3.99-8.53V9.86c-.6-4.62-3.92-8.42-8.41-9.64-.57-.12-1.15-.2-1.73-.23h0Z"/></g></g></svg>
</div>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.title("")
st.title("تحويل الصور إلى PDF")
st.caption("ارفع الصور ثم قم بترتيبها وتحويلها إلى PDF")

controls_col, preview_col = st.columns(
    [1, 1.2],
    gap="large"
)


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