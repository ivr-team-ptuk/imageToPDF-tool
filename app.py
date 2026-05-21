import streamlit as st
import fitz
import io
from streamlit_pdf_viewer import pdf_viewer
from PIL import Image
from streamlit_sortables import sort_items

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="تحويل الصور إلى PDF - IVR",
    layout="centered"
)

st.title("تحويل الصور إلى PDF")
st.caption("ارفع الصور ثم قم بترتيبها وتحويلها إلى PDF")

# =========================
# FILE UPLOADER STYLE
# =========================

st.markdown("""
<style>

[data-testid="stFileUploader"] {
    border: 2px dashed #999;
    border-radius: 18px;
    padding: 35px;
}

[data-testid="stFileUploaderDropzone"] {
    padding: 40px;
}

[data-testid="stFileUploaderDropzone"] div div div span {
    display: none;
}

[data-testid="stFileUploaderDropzone"]::before {

    content: "🖼️ اسحب الصور هنا أو اضغط للاختيار";

    display: flex;
    align-items: center;
    justify-content: center;

    width: 100%;
    height: 120px;

    font-size: 22px;
    font-weight: 600;

    color: #888;
}

</style>
""", unsafe_allow_html=True)

# =========================
# UPLOAD IMAGES
# =========================

uploaded_images = st.file_uploader(
    "",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# =========================
# MAIN
# =========================

if uploaded_images:

    st.subheader("ترتيب الصور")

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

        st.subheader("أسماء العلامات المرجعية")

        for image_name in sorted_names:

            clean_name = image_name.rsplit(".", 1)[0]

            bookmark_titles[image_name] = st.text_input(
                f"علامة: {image_name}",
                value=clean_name
            )

    # =========================
    # OUTPUT FILE NAME
    # =========================

    output_name = st.text_input(
        "اسم الملف النهائي",
        value="images_pdf"
    )

    # =========================
    # CREATE PDF
    # =========================

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

                    compressed_bytes = compressed_buffer.getvalue()

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
                    # BOOKMARK
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

else:

    st.info("قم برفع الصور أولاً.")