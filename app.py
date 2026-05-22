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
    <div class="logo">
                <svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" id="svg1" x="0px" y="0px" viewBox="0 0 1000 373.3" style="enable-background:new 0 0 1000 373.3;" xml:space="preserve"> <style type="text/css"> .st0{fill:#FFFFFF;} .st1{font-family:'Arial-BoldMT';} .st2{font-size:37.8074px;} </style> <g id="g1" transform="translate(223.64936,-370.2004)"> <g id="g15" transform="matrix(2.3855057,0,0,2.3855057,-454.13116,-683.06164)"> <path id="path14" class="st0" d="M415.7,463.7c-1.3,2.4-2.9,4.9-4.4,7.3c-1.6,2.7-2.9,5.1-4.2,7.3c-1.6,2.4-2.9,4.9-4.2,7.6    c-1.3,2.4-2.7,4.9-4.2,7.6l-5.8,10.7c-1.8,3.3-3.8,7.1-6,11.1c-2.2,3.8-4,7.3-6,10.4l-34.4-61.8h-27.6c3.1,5.3,6.2,10.9,9.1,16.2    s6,10.9,9.1,16.2c2.2,3.6,4.2,7.3,6.2,11.1c2.2,3.8,4.2,7.3,6.4,11.1l30.7,54.7l47.1-85.8h52.2c2.7,0,4.9,0.9,6.9,2.9    s3.1,4.4,3.1,7.3v6c0,2.7-1.1,5.3-3.1,7.3c-2,2.2-4.2,3.1-6.9,3.1h-54.2V575h23.1v-38H463l23.6,38h27.1l-24-39.1    c3.6-1.3,6.7-3.1,9.6-5.3s5.3-4.9,7.3-7.8c2-2.9,3.6-6,4.7-9.1c1.1-3.3,1.8-6.7,1.8-10v-6c0-4.7-0.9-9.1-2.7-13.1    c-1.8-4-4-7.6-7.1-10.7c-2.9-3.1-6.4-5.6-10.7-7.1c-4-1.8-8.4-2.7-12.9-2.7h-42.2c-0.9,0-1.6-0.2-2.4-0.2L415.7,463.7z"/> <path id="path15" class="st0" d="M286.4,463.9V575h23.6V463.9H286.4z"/> <text transform="matrix(0.4192 0 0 0.4192 504.0249 467.9003)" class="st0 st1 st2">©</text> </g> <g id="g23" transform="translate(0,-928)"> <path id="path20" class="st0" d="M-217.9,1526.6c-3.1,0.4-5.3,2.7-5.8,5.6v0.9v56v6.4c1.1,28,16.4,53.3,40.7,67.3    c7.8,4.2,16,7.1,24.7,8.7h30.9h58.2h1.3c6.2-0.9,8.4-6.9,9.3-9.3v-0.7l5.1-66.2l1.8-22c-0.4-1.1,0.9-4,2-6    c6.4,0.2,12.9,1.6,18.9,4.2c8,3.6,25.3,17.3,29.1,38.9c0.2,2,0.4,4,0.4,6l0,0c1.3,14.4,2,28.4,2.9,43.1c0,6.7,4.4,11.8,9.8,12l0,0    h30h30.4h27.3h0.2c3.6,0,6.4-2.9,6.4-6.4c0-2-0.9-3.8-2.4-4.9l-0.4-0.4l-89.5-81.3l-16.2-14.7l-2.2-2l-16-14.4l-2-1.8    c-4-3.3-8.9-5.3-14-6.2l-5.1-0.4l-6.9-0.4l-12.7-0.9l-22.9-1.6l-10.9-0.7l-96.2-6.4l-22.7-1.6L-217.9,1526.6z"/> <path id="path4" class="st0" d="M-141.7,1298.2c-38.9,0.7-72,28.7-78.7,67.1c-0.2,1.8-0.4,3.3-0.7,5.1v5.6v12.2V1508v0.4    c0,3.3,2.9,6,6.2,6l3.6-1.1l96.4-30.7l17.8-5.6l43.6-13.8l8.7-2.7c6.9-3.1,10.2-9.8,14.2-16l18.4-27.1l5.8-8.4l3.8-5.8l66-96.9    l2-3.1c0-0.2,0.2-0.7,0.2-0.9c0-1.1-0.4-2.2-1.1-2.9c-0.7-0.7-1.6-1.1-2.4-1.3h-2.2h-79.8h-8h-32.7h-79.5H-141.7z"/> <path id="path5" class="st0" d="M80.3,1298.2c-2.4,0.9-4.7,2.7-6.2,5.1l-1.6,6.9l-26.4,119.5l-5.1,22.9l-5.1,23.6l-1.8,7.8    c-0.7,4.2-0.4,8.4,0.2,12.7l9.6,19.6l1.8,3.6l12.7,25.8c20.4,36.9,34.7,77.3,55.8,113.5c1.1,1.1,2.9,1.8,4.4,1.8    c1.1-0.2,2-0.7,2.9-1.1c0.7-0.7,1.6-1.1,2.2-1.8c17.6-15.1,27.8-37.1,28.2-60.2v-2.4v-227.5c-4.2-32.7-27.6-59.3-59.3-68    C88.5,1298.9,84.5,1298.4,80.3,1298.2L80.3,1298.2z"/> </g> </g> </svg>
            </div>
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