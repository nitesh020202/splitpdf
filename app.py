import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import base64
from datetime import datetime
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="PDF Splitter - Split PDF Pages Online",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- iLovePDF STYLE CSS ----------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .stApp {
        background: #f5f7fa;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .ilovepdf-header {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .logo {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #ff6b6b, #ff8e53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tool card styling */
    .tool-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: #fafbfc;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #ff6b6b;
        background: #fff5f5;
    }
    
    /* Button styling */
    .stButton > button {
        background: #ff6b6b;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #ff5252;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255,107,107,0.3);
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: #4a5568;
    }
    
    .secondary-btn > button:hover {
        background: #2d3748;
    }
    
    /* Mode selector */
    .mode-selector {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 0.5rem;
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .mode-option {
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .mode-option.active {
        background: white;
        color: #ff6b6b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Page preview */
    .page-preview {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .page-preview:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Range input styling */
    .range-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* File info bar */
    .file-info {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #ff6b6b;
    }
    
    /* Number input */
    .stNumberInput input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
    }
    
    /* Text input */
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
    }
    
    /* Info box */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success box */
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Feature grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-item {
        text-align: center;
        padding: 1rem;
    }
    
    .feature-icon {
        font-size: 32px;
        margin-bottom: 0.5rem;
    }
    
    hr {
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------
def get_pdf_info(reader):
    """Get PDF information"""
    return {
        "pages": len(reader.pages),
        "metadata": reader.metadata if reader.metadata else {}
    }

def split_by_range(reader, start, end):
    """Split PDF by page range"""
    writer = PdfWriter()
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def split_by_pages(reader, pages_list):
    """Split PDF by specific pages"""
    writer = PdfWriter()
    for page_num in pages_list:
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

def split_all_pages(reader):
    """Split each page into separate PDF"""
    outputs = []
    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        outputs.append(output)
    return outputs

def split_by_ranges(reader, ranges):
    """Split by multiple ranges"""
    outputs = []
    for start, end in ranges:
        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        outputs.append(output)
    return outputs

def parse_range_string(range_str, total_pages):
    """Parse range string like '1-5,8,10-12'"""
    ranges = []
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid range: {part}")
            ranges.append((start, end))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Invalid page: {page}")
            ranges.append((page, page))
    
    return ranges

def get_download_link(file_bytes, filename):
    """Generate download link"""
    b64 = base64.b64encode(file_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="download-link">Download {filename}</a>'
    return href

# ---------------- MAIN UI ----------------
def main():
    # Header
    st.markdown("""
        <div class="ilovepdf-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="logo" style="font-size: 28px;">✂️ PDF Splitter</span>
                    <p style="color: #64748b; margin-top: 0.5rem;">Split PDF pages quickly and easily</p>
                </div>
                <div style="display: flex; gap: 1rem;">
                    <span style="color: #64748b;">🔒 Secure</span>
                    <span style="color: #64748b;">⚡ Fast</span>
                    <span style="color: #64748b;">🎯 Accurate</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Upload section
        uploaded_file = st.file_uploader(
            "",
            type=['pdf'],
            label_visibility="collapsed",
            help="Upload PDF file to split"
        )
        
        if uploaded_file:
            # Read PDF
            reader = PdfReader(uploaded_file)
            pdf_info = get_pdf_info(reader)
            total_pages = pdf_info['pages']
            
            # File info bar
            st.markdown(f"""
                <div class="file-info">
                    <div>
                        <strong>📄 {uploaded_file.name}</strong><br>
                        <span style="color: #64748b; font-size: 14px;">{total_pages} pages • {(uploaded_file.size / 1024):.0f} KB</span>
                    </div>
                    <div>
                        <span style="background: #e2e8f0; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 12px;">Ready to split</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Split mode selection
            st.markdown("### Choose split method")
            
            mode = st.radio(
                "",
                ["Extract pages", "Split by ranges", "Split all pages"],
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Mode 1: Extract pages
            if mode == "Extract pages":
                st.markdown("#### 📄 Extract specific pages")
                
                extract_mode = st.radio(
                    "",
                    ["Page range", "Individual pages"],
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                if extract_mode == "Page range":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        start_page = st.number_input("From page", min_value=1, max_value=total_pages, value=1)
                    with col_b:
                        end_page = st.number_input("To page", min_value=start_page, max_value=total_pages, value=total_pages)
                    
                    if st.button("Extract Pages", use_container_width=True):
                        with st.spinner("Processing..."):
                            pdf_output = split_by_range(reader, start_page, end_page)
                            st.success(f"✅ Extracted pages {start_page} to {end_page}")
                            
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_output,
                                file_name=f"extracted_pages_{start_page}_{end_page}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                
                else:  # Individual pages
                    pages_input = st.text_input(
                        "Page numbers (comma-separated)",
                        placeholder="Example: 1,3,5,7",
                        help="Enter page numbers separated by commas"
                    )
                    
                    if pages_input:
                        try:
                            pages = [int(p.strip()) for p in pages_input.split(',')]
                            valid_pages = [p for p in pages if 1 <= p <= total_pages]
                            
                            if valid_pages:
                                st.info(f"Selected {len(valid_pages)} pages: {valid_pages}")
                                
                                if st.button("Extract Pages", use_container_width=True):
                                    pdf_output = split_by_pages(reader, valid_pages)
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=pdf_output,
                                        file_name="selected_pages.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            else:
                                st.error("No valid pages selected")
                        except:
                            st.error("Please enter valid page numbers")
            
            # Mode 2: Split by ranges
            elif mode == "Split by ranges":
                st.markdown("#### 🎯 Split into multiple files")
                st.markdown("""
                    <div class="info-box">
                        💡 Enter ranges like: <strong>1-5,6-10,11-15</strong> or <strong>1-3,5,7-9</strong>
                    </div>
                """, unsafe_allow_html=True)
                
                ranges_input = st.text_input(
                    "Page ranges",
                    placeholder="Example: 1-5,6-10,11-15",
                    help="Each range will become a separate PDF file"
                )
                
                if ranges_input:
                    try:
                        ranges = parse_range_string(ranges_input, total_pages)
                        
                        # Preview ranges
                        st.markdown("##### Preview:")
                        for i, (start, end) in enumerate(ranges, 1):
                            st.markdown(f"📄 **File {i}:** Pages {start} to {end} ({end-start+1} pages)")
                        
                        if st.button("Split PDF", use_container_width=True):
                            with st.spinner("Splitting PDF..."):
                                if len(ranges) == 1:
                                    # Single file
                                    pdf_output = split_by_range(reader, ranges[0][0], ranges[0][1])
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=pdf_output,
                                        file_name=f"split_{ranges[0][0]}_{ranges[0][1]}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    # Multiple files - create ZIP
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                        for i, (start, end) in enumerate(ranges, 1):
                                            pdf_output = split_by_range(reader, start, end)
                                            zip_file.writestr(f"split_{i}_pages_{start}_{end}.pdf", pdf_output.getvalue())
                                    
                                    zip_buffer.seek(0)
                                    st.success(f"✅ Created {len(ranges)} PDF files")
                                    st.download_button(
                                        label="📦 Download All (ZIP)",
                                        data=zip_buffer,
                                        file_name=f"pdf_splits_{datetime.now().strftime('%Y%m%d')}.zip",
                                        mime="application/zip",
                                        use_container_width=True
                                    )
                    except Exception as e:
                        st.error(f"Invalid format: {str(e)}")
            
            # Mode 3: Split all pages
            else:
                st.markdown("#### 🔪 Split each page into separate PDF")
                st.markdown(f"""
                    <div class="info-box">
                        📄 This will create {total_pages} individual PDF files - one for each page.
                    </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Split All Pages", use_container_width=True):
                        with st.spinner(f"Splitting {total_pages} pages..."):
                            progress_bar = st.progress(0)
                            zip_buffer = io.BytesIO()
                            
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for i in range(total_pages):
                                    writer = PdfWriter()
                                    writer.add_page(reader.pages[i])
                                    output = io.BytesIO()
                                    writer.write(output)
                                    output.seek(0)
                                    zip_file.writestr(f"page_{i+1}.pdf", output.getvalue())
                                    progress_bar.progress((i + 1) / total_pages)
                            
                            zip_buffer.seek(0)
                            st.success(f"✅ Created {total_pages} individual PDF files")
                            st.download_button(
                                label="📦 Download All Pages (ZIP)",
                                data=zip_buffer,
                                file_name=f"all_pages_{datetime.now().strftime('%Y%m%d')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                
                with col_b:
                    # Quick preview of pages
                    st.markdown("##### Page preview:")
                    preview_pages = min(6, total_pages)
                    preview_cols = st.columns(preview_pages)
                    for i in range(preview_pages):
                        with preview_cols[i]:
                            st.markdown(f"""
                                <div class="page-preview" style="text-align: center;">
                                    <div style="background: #f1f5f9; border-radius: 4px; padding: 1rem; margin-bottom: 0.5rem;">
                                        📄
                                    </div>
                                    <span style="font-size: 12px;">Page {i+1}</span>
                                </div>
                            """, unsafe_allow_html=True)
            
            # Tips section
            st.markdown("---")
            st.markdown("""
                <div style="background: #f8fafc; border-radius: 12px; padding: 1rem; margin-top: 1rem;">
                    <h4 style="margin: 0 0 0.5rem 0;">💡 Tips</h4>
                    <ul style="margin: 0; color: #64748b;">
                        <li>Use comma (,) to separate multiple page numbers</li>
                        <li>Use hyphen (-) to specify a range of pages</li>
                        <li>You can combine ranges and single pages (e.g., 1-5,8,10-15)</li>
                        <li>All files are processed securely in your browser</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        else:
            # Empty state - show features
            st.markdown("""
                <div class="tool-card">
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 64px; margin-bottom: 1rem;">✂️</div>
                        <h2>Split PDF pages easily</h2>
                        <p style="color: #64748b; margin-bottom: 2rem;">Upload a PDF file to extract specific pages or split into multiple files</p>
                        
                        <div class="feature-grid">
                            <div class="feature-item">
                                <div class="feature-icon">📄</div>
                                <h4>Extract pages</h4>
                                <p style="font-size: 14px; color: #64748b;">Extract specific page ranges</p>
                            </div>
                            <div class="feature-item">
                                <div class="feature-icon">🎯</div>
                                <h4>Multiple ranges</h4>
                                <p style="font-size: 14px; color: #64748b;">Split into several PDF files</p>
                            </div>
                            <div class="feature-item">
                                <div class="feature-icon">⚡</div>
                                <h4>Fast processing</h4>
                                <p style="font-size: 14px; color: #64748b;">Process locally in your browser</p>
                            </div>
                            <div class="feature-item">
                                <div class="feature-icon">🔒</div>
                                <h4>100% secure</h4>
                                <p style="font-size: 14px; color: #64748b;">Files never leave your device</p>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <hr>
        <div style="text-align: center; color: #64748b; padding: 1rem; font-size: 14px;">
            <p>PDF Splitter • Free online tool • No registration required</p>
            <p style="margin-top: 0.5rem;">🔒 Your files are processed locally and never uploaded to any server</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
