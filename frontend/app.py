"""
Streamlit web interface for CodeScribe.
"""
import streamlit as st
import requests
import os
import tempfile
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


# Configure Streamlit page
st.set_page_config(
    page_title="CodeScribe - AI Code Documentation",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("CODESCRIBE_API_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #007acc;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007acc;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .code-element {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    # Header
    st.markdown('<h1 class="main-header">📚 CodeScribe</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2em; color: #666;">AI-Powered Code Documentation Assistant</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("Configuration")
        
        # API Provider Selection
        provider = st.selectbox(
            "AI Provider",
            ["openai", "deepseek", "huggingface"],
            index=1,  # Default to deepseek
            help="Choose the AI provider for documentation generation"
        )
        
        # Model Selection
        if provider == "openai":
            model = st.selectbox(
                "Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
                help="Select the OpenAI model to use"
            )
            
            # API Key Input
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="Your OpenAI API key"
            )
            
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        
        elif provider == "deepseek":
            model = st.selectbox(
                "Model",
                ["deepseek-r1", "deepseek-chat"],
                help="Select the DeepSeek model to use"
            )
            
            # API Key Input
            api_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=os.getenv("DEEPSEEK_API_KEY", ""),
                help="Your DeepSeek API key"
            )
            
            if api_key:
                os.environ["DEEPSEEK_API_KEY"] = api_key
        
        else:
            model = st.selectbox(
                "Model",
                ["microsoft/DialoGPT-medium", "microsoft/CodeBERT-base"],
                help="Select the Hugging Face model to use"
            )
        
        # Documentation Settings
        st.subheader("Documentation Settings")
        
        verbosity = st.selectbox(
            "Verbosity",
            ["low", "medium", "high"],
            index=1,
            help="Level of detail in generated documentation"
        )
        
        style = st.selectbox(
            "Documentation Style",
            ["google", "numpy", "sphinx", "jsdoc"],
            help="Documentation style to follow"
        )
        
        output_format = st.selectbox(
            "Output Format",
            ["markdown", "html", "inline"],
            help="Format for generated documentation"
        )
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            include_examples = st.checkbox("Include Examples", value=True)
            include_parameters = st.checkbox("Include Parameters", value=True)
            include_return_values = st.checkbox("Include Return Values", value=True)
            include_exceptions = st.checkbox("Include Exceptions", value=True)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Code Input", "📁 File Upload", "📦 Batch Processing", "ℹ️ About"])
    
    with tab1:
        code_input_interface(provider, model, verbosity, style)
    
    with tab2:
        file_upload_interface(provider, model, verbosity, style, output_format)
    
    with tab3:
        batch_processing_interface(provider, model, verbosity, style, output_format)
    
    with tab4:
        about_interface()


def code_input_interface(provider: str, model: str, verbosity: str, style: str):
    """Interface for direct code input"""
    st.header("Code Input")
    st.write("Paste your code below to generate documentation:")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Language selection
        language = st.selectbox(
            "Programming Language",
            ["python", "javascript", "typescript"],
            help="Select the programming language of your code"
        )
        
        # Code input
        code_input = st.text_area(
            "Code",
            height=400,
            placeholder="Paste your code here...",
            help="Enter the code you want to document"
        )
        
        # Generate button
        if st.button("Generate Documentation", type="primary"):
            if code_input.strip():
                with st.spinner("Generating documentation..."):
                    result = generate_documentation_for_code(
                        code_input, language, provider, model, verbosity, style
                    )
                    
                    if result:
                        display_documentation_result(result)
                    else:
                        st.error("Failed to generate documentation. Please check your settings and try again.")
            else:
                st.warning("Please enter some code to document.")
    
    with col2:
        st.subheader("Tips")
        st.markdown("""
        <div class="feature-box">
        <strong>Best Practices:</strong>
        <ul>
        <li>Include complete functions/classes</li>
        <li>Ensure proper syntax</li>
        <li>Add type hints for better results</li>
        <li>Use meaningful variable names</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


def file_upload_interface(provider: str, model: str, verbosity: str, style: str, output_format: str):
    """Interface for file upload"""
    st.header("File Upload")
    st.write("Upload a code file to generate documentation:")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a code file",
        type=['py', 'js', 'ts', 'jsx', 'tsx'],
        help="Upload a supported code file"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("File Information")
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
            
            # Preview file content
            if st.checkbox("Preview file content"):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    st.code(content[:1000] + "..." if len(content) > 1000 else content)
                    uploaded_file.seek(0)  # Reset file pointer
                except UnicodeDecodeError:
                    st.error("Cannot preview file: contains non-text data")
        
        with col2:
            st.subheader("Actions")
            
            if st.button("Generate Documentation", type="primary"):
                with st.spinner("Processing file..."):
                    result = process_uploaded_file(
                        uploaded_file, provider, model, verbosity, style, output_format
                    )
                    
                    if result:
                        display_file_result(result, output_format)
                    else:
                        st.error("Failed to process file. Please check your settings and try again.")


def batch_processing_interface(provider: str, model: str, verbosity: str, style: str, output_format: str):
    """Interface for batch processing"""
    st.header("Batch Processing")
    st.write("Upload multiple files or a ZIP archive for batch documentation generation:")
    
    # Multiple file uploader
    uploaded_files = st.file_uploader(
        "Choose multiple files",
        type=['py', 'js', 'ts', 'jsx', 'tsx', 'zip'],
        accept_multiple_files=True,
        help="Upload multiple code files or a ZIP archive"
    )
    
    if uploaded_files:
        st.subheader(f"Selected {len(uploaded_files)} file(s)")
        
        # Display file list
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size / 1024:.2f} KB)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            recursive = st.checkbox("Process ZIP files recursively", value=True)
        
        with col2:
            if st.button("Start Batch Processing", type="primary"):
                with st.spinner("Processing files..."):
                    results = process_batch_files(
                        uploaded_files, provider, model, verbosity, style, output_format, recursive
                    )
                    
                    if results:
                        display_batch_results(results)
                    else:
                        st.error("Failed to process files. Please check your settings and try again.")


def about_interface():
    """About and help interface"""
    st.header("About CodeScribe")
    
    st.markdown("""
    <div class="feature-box">
    <h3>🚀 Features</h3>
    <ul>
    <li><strong>AI-Powered:</strong> Uses advanced AI models to generate high-quality documentation</li>
    <li><strong>Multi-Language:</strong> Supports Python, JavaScript, TypeScript, and more</li>
    <li><strong>Flexible Output:</strong> Generate Markdown, HTML, or inline documentation</li>
    <li><strong>Batch Processing:</strong> Process multiple files at once</li>
    <li><strong>Customizable:</strong> Configure style, verbosity, and AI provider</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Supported Languages")
        st.write("- Python (.py)")
        st.write("- JavaScript (.js)")
        st.write("- TypeScript (.ts)")
        st.write("- React JSX (.jsx)")
        st.write("- React TSX (.tsx)")
    
    with col2:
        st.subheader("AI Providers")
        st.write("- **OpenAI:** GPT-3.5, GPT-4 (requires API key)")
        st.write("- **Hugging Face:** Free local models")
    
    st.subheader("Getting Started")
    st.write("""
    1. **Configure** your AI provider and settings in the sidebar
    2. **Choose** how you want to input your code:
       - Direct code input
       - Single file upload
       - Batch processing
    3. **Generate** documentation with a single click
    4. **Download** or copy the generated documentation
    """)
    
    st.subheader("API Information")
    if check_api_health():
        st.success("✅ API is healthy and ready")
    else:
        st.error("❌ API is not responding. Please check the backend service.")
    
    # Display API configuration
    config = get_api_config()
    if config:
        st.subheader("API Configuration")
        st.json(config)


def generate_documentation_for_code(code: str, language: str, provider: str, model: str, verbosity: str, style: str) -> Optional[Dict[str, Any]]:
    """Generate documentation for code snippet"""
    try:
        payload = {
            "code": code,
            "language": language,
            "verbosity": verbosity,
            "style": style,
            "provider": provider,
            "model": model
        }
        
        response = requests.post(f"{API_BASE_URL}/document/code", json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def process_uploaded_file(uploaded_file, provider: str, model: str, verbosity: str, style: str, output_format: str) -> Optional[Any]:
    """Process uploaded file"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {
            "verbosity": verbosity,
            "style": style,
            "provider": provider,
            "model": model,
            "output_format": output_format
        }
        
        response = requests.post(f"{API_BASE_URL}/document/file", files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            if output_format in ["markdown", "html"]:
                return response.content
            else:
                return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def process_batch_files(uploaded_files: List, provider: str, model: str, verbosity: str, style: str, output_format: str, recursive: bool) -> Optional[Dict[str, Any]]:
    """Process multiple files"""
    try:
        files = []
        for uploaded_file in uploaded_files:
            files.append(("files", (uploaded_file.name, uploaded_file, uploaded_file.type)))
        
        data = {
            "verbosity": verbosity,
            "style": style,
            "provider": provider,
            "model": model,
            "recursive": recursive
        }
        
        response = requests.post(f"{API_BASE_URL}/document/batch", files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def display_documentation_result(result: Dict[str, Any]):
    """Display documentation generation result"""
    if result.get("success"):
        st.success("Documentation generated successfully!")
        
        # Display elements
        if result.get("elements"):
            st.subheader("Documented Elements")
            for element in result["elements"]:
                with st.expander(f"{element['type'].title()}: {element['name']}"):
                    st.code(element['signature'])
                    st.markdown("**Documentation:**")
                    st.markdown(element['docstring'])
                    if element.get('summary'):
                        st.markdown("**Summary:**")
                        st.markdown(element['summary'])
        
        # Display full documentation
        if result.get("documentation"):
            st.subheader("Complete Documentation")
            st.markdown(result["documentation"])
            
            # Download button
            st.download_button(
                label="Download Documentation",
                data=result["documentation"],
                file_name="documentation.md",
                mime="text/markdown"
            )
        
        # Display summary
        if result.get("summary"):
            st.subheader("Summary")
            st.info(result["summary"])
    
    else:
        st.error(f"Failed to generate documentation: {result.get('message', 'Unknown error')}")


def display_file_result(result: Any, output_format: str):
    """Display file processing result"""
    if output_format in ["markdown", "html"]:
        # File download
        st.success("Documentation generated successfully!")
        
        file_extension = "md" if output_format == "markdown" else "html"
        mime_type = "text/markdown" if output_format == "markdown" else "text/html"
        
        st.download_button(
            label=f"Download {output_format.title()} Documentation",
            data=result,
            file_name=f"documentation.{file_extension}",
            mime=mime_type
        )
        
        # Preview
        if output_format == "markdown":
            st.subheader("Preview")
            st.markdown(result.decode('utf-8'))
    
    else:
        display_documentation_result(result)


def display_batch_results(results: Dict[str, Any]):
    """Display batch processing results"""
    if results.get("job_id"):
        st.success(f"Batch processing started! Job ID: {results['job_id']}")
        
        # You could implement job status polling here
        st.info("Check the API for job status updates.")
    
    else:
        st.error("Failed to start batch processing.")


def check_api_health() -> bool:
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_api_config() -> Optional[Dict[str, Any]]:
    """Get API configuration"""
    try:
        response = requests.get(f"{API_BASE_URL}/config", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


if __name__ == "__main__":
    main()