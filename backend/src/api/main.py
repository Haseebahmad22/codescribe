"""
FastAPI-based REST API for CodeScribe.
"""
import os
import asyncio
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import aiofiles

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import CodeScribeEngine
from generators.base import DocumentationConfig


# Pydantic models for API
class DocumentationRequest(BaseModel):
    code: str
    language: str
    verbosity: str = "medium"
    style: str = "google"
    provider: str = "openai"
    model: Optional[str] = None


class DocumentationResponse(BaseModel):
    success: bool
    message: str
    documentation: Optional[str] = None
    elements: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None


class ProcessingStatus(BaseModel):
    job_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress: float
    message: str
    result: Optional[Dict[str, Any]] = None


class ConfigResponse(BaseModel):
    supported_languages: List[str]
    output_formats: List[str]
    ai_providers: Dict[str, Dict[str, Any]]
    styles: Dict[str, List[str]]


# Initialize FastAPI app
app = FastAPI(
    title="CodeScribe API",
    description="AI-Powered Code Documentation Assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
    ],  # React dev origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for background tasks
processing_jobs: Dict[str, ProcessingStatus] = {}


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "name": "CodeScribe API",
        "version": "1.0.0",
        "description": "AI-Powered Code Documentation Assistant",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "codescribe-api"}


@app.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get API configuration and supported options"""
    from parsers import ParserFactory
    from generators import GeneratorFactory
    
    return ConfigResponse(
        supported_languages=ParserFactory.get_supported_languages(),
        output_formats=["markdown", "html", "inline"],
        ai_providers=GeneratorFactory.get_available_providers(),
        styles={
            "python": ["google", "numpy", "sphinx"],
            "javascript": ["jsdoc"],
            "typescript": ["jsdoc"]
        }
    )


@app.post("/document/code", response_model=DocumentationResponse)
async def document_code(request: DocumentationRequest):
    """Generate documentation for code snippet"""
    try:
        # Create temporary engine with request configuration
        engine = _create_engine_from_request(request)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f".{_get_file_extension(request.language)}", 
            delete=False
        ) as temp_file:
            temp_file.write(request.code)
            temp_file_path = temp_file.name
        
        try:
            # Process the code
            documentation_list = await engine.process_file(temp_file_path, request.language)
            
            if not documentation_list:
                return DocumentationResponse(
                    success=False,
                    message="No code elements found to document"
                )
            
            # Extract documentation
            docstrings = []
            elements = []
            
            for doc in documentation_list:
                elements.append({
                    "name": doc.element.name,
                    "type": doc.element.type,
                    "signature": doc.element.signature,
                    "line": doc.element.start_line,
                    "docstring": doc.docstring,
                    "summary": doc.summary
                })
                docstrings.append(doc.docstring)
            
            # Generate summary
            summary = await engine.doc_generator.generate_summary([doc.element for doc in documentation_list])
            
            return DocumentationResponse(
                success=True,
                message="Documentation generated successfully",
                documentation="\n\n".join(docstrings),
                elements=elements,
                summary=summary
            )
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return DocumentationResponse(
            success=False,
            message=f"Error generating documentation: {str(e)}"
        )


@app.post("/document/file")
async def document_file(
    file: UploadFile = File(...),
    verbosity: str = Form("medium"),
    style: str = Form("google"),
    provider: str = Form("openai"),
    model: Optional[str] = Form(None),
    output_format: str = Form("markdown")
):
    """Generate documentation for uploaded file"""
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix
        from parsers import ParserFactory
        language = ParserFactory.detect_language_from_extension(file_extension)
        
        if not language:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}"
            )
        
        # Read file content
        content = await file.read()
        
        # Create documentation request
        request = DocumentationRequest(
            code=content.decode('utf-8'),
            language=language,
            verbosity=verbosity,
            style=style,
            provider=provider,
            model=model
        )
        
        # Generate documentation
        doc_response = await document_code(request)
        
        if not doc_response.success:
            raise HTTPException(status_code=500, detail=doc_response.message)
        
        # Format response based on output format
        if output_format == "markdown":
            # Create temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                temp_file.write(f"# Documentation for {file.filename}\n\n")
                temp_file.write(doc_response.documentation)
                temp_file_path = temp_file.name
            
            return FileResponse(
                temp_file_path,
                filename=f"{Path(file.filename).stem}_docs.md",
                media_type="text/markdown"
            )
        
        elif output_format == "html":
            # Generate HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Documentation for {file.filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        .element {{ margin-bottom: 20px; border-left: 3px solid #007acc; padding-left: 15px; }}
    </style>
</head>
<body>
    <h1>Documentation for {file.filename}</h1>
    <div class="documentation">
        {"<br>".join(doc_response.documentation.split("\\n"))}
    </div>
</body>
</html>
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name
            
            return FileResponse(
                temp_file_path,
                filename=f"{Path(file.filename).stem}_docs.html",
                media_type="text/html"
            )
        
        else:
            return doc_response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/document/batch")
async def start_batch_processing(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    verbosity: str = Form("medium"),
    style: str = Form("google"),
    provider: str = Form("openai"),
    model: Optional[str] = Form(None),
    recursive: bool = Form(False)
):
    """Start batch processing of multiple files"""
    import uuid
    
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    processing_jobs[job_id] = ProcessingStatus(
        job_id=job_id,
        status="queued",
        progress=0.0,
        message="Job queued for processing"
    )
    
    # Start background processing
    background_tasks.add_task(
        _process_batch_files,
        job_id,
        files,
        verbosity,
        style,
        provider,
        model
    )
    
    return {"job_id": job_id, "status": "queued", "message": "Batch processing started"}


@app.get("/document/batch/{job_id}", response_model=ProcessingStatus)
async def get_batch_status(job_id: str):
    """Get status of batch processing job"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_jobs[job_id]


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    from parsers import ParserFactory
    return {"languages": ParserFactory.get_supported_languages()}


@app.get("/providers")
async def get_ai_providers():
    """Get list of available AI providers"""
    from generators import GeneratorFactory
    return {"providers": GeneratorFactory.get_available_providers()}


# Helper functions
def _create_engine_from_request(request: DocumentationRequest) -> CodeScribeEngine:
    """Create CodeScribe engine from API request"""
    # Create basic configuration
    config = {
        'ai': {
            'provider': request.provider,
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'model': request.model or 'gpt-3.5-turbo',
                'max_tokens': 1000,
                'temperature': 0.3
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
                'model': request.model or 'deepseek-r1',
                'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                'max_tokens': 1000,
                'temperature': 0.3
            }
        },
        'documentation': {
            'verbosity': request.verbosity,
            'style': request.style,
            'include_examples': True,
            'include_parameters': True,
            'include_return_values': True,
            'include_exceptions': True
        },
        'processing': {
            'batch_size': 10,
            'max_file_size_mb': 5,
            'skip_files': [],
            'supported_extensions': ['.py', '.js', '.ts', '.jsx', '.tsx']
        }
    }
    
    # Create engine
    engine = CodeScribeEngine()
    engine.config = config
    engine._initialize_generator()
    
    return engine


def _get_file_extension(language: str) -> str:
    """Get file extension for language"""
    extensions = {
        'python': 'py',
        'javascript': 'js',
        'typescript': 'ts'
    }
    return extensions.get(language, 'txt')


async def _process_batch_files(
    job_id: str,
    files: List[UploadFile],
    verbosity: str,
    style: str,
    provider: str,
    model: Optional[str]
):
    """Background task for batch processing files"""
    try:
        processing_jobs[job_id].status = "processing"
        processing_jobs[job_id].message = "Processing files..."
        
        total_files = len(files)
        results = {}
        
        for i, file in enumerate(files):
            try:
                # Update progress
                progress = (i / total_files) * 100
                processing_jobs[job_id].progress = progress
                processing_jobs[job_id].message = f"Processing {file.filename}..."
                
                # Process file
                content = await file.read()
                
                # Detect language
                file_extension = Path(file.filename).suffix
                from parsers import ParserFactory
                language = ParserFactory.detect_language_from_extension(file_extension)
                
                if language:
                    request = DocumentationRequest(
                        code=content.decode('utf-8'),
                        language=language,
                        verbosity=verbosity,
                        style=style,
                        provider=provider,
                        model=model
                    )
                    
                    doc_response = await document_code(request)
                    results[file.filename] = doc_response.dict()
                else:
                    results[file.filename] = {
                        "success": False,
                        "message": f"Unsupported file type: {file_extension}"
                    }
            
            except Exception as e:
                results[file.filename] = {
                    "success": False,
                    "message": f"Error processing file: {str(e)}"
                }
        
        # Mark as completed
        processing_jobs[job_id].status = "completed"
        processing_jobs[job_id].progress = 100.0
        processing_jobs[job_id].message = "Batch processing completed"
        processing_jobs[job_id].result = results
    
    except Exception as e:
        processing_jobs[job_id].status = "failed"
        processing_jobs[job_id].message = f"Batch processing failed: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)