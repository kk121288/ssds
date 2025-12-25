from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List, Dict
import os
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Detector Pro API",
    description="نظام متقدم للكشف عن النصوص المولدة بالذكاء الاصطناعي",
    version="2.0.0",
    docs_url="/api-docs",
    redoc_url="/redoc"
)

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إنشاء المجلدات اللازمة
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# تقديم الملفات الثابتة
app.mount("/static", StaticFiles(directory="static"), name="static")

# تحميل القوالب
templates = Jinja2Templates(directory="templates")

# ========== دوال مساعدة ==========

def detect_language_advanced(text: str) -> str:
    """كشف اللغة بطرق متعددة"""
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    # كشف بسيط من الأحرف
    arabic_chars = sum(1 for char in text if "\u0600" <= char <= "\u06FF")
    english_chars = sum(1 for char in text if "a" <= char.lower() <= "z")
    
    if arabic_chars > english_chars * 2:
        return "العربية"
    elif english_chars > arabic_chars * 2:
        return "الإنجليزية"
    
    return "مختلطة"

def advanced_ai_detection(text: str) -> Dict:
    """خوارزمية متقدمة لكشف الذكاء الاصطناعي"""
    if not text or len(text.strip()) < 20:
        return {
            "ai_probability": 0.5,
            "note": "النص قصير جدًا لتحليل دقيق",
            "confidence": 50,
            "language": detect_language_advanced(text)
        }
    
    words = text.split()
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").replace("؟", ".").split(".") if s.strip()]
    avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    # حساب الاحتمالية (مثال مبسط)
    ai_probability = 0.5
    
    if avg_sentence_len > 25:
        ai_probability = 0.7
    elif avg_sentence_len < 10:
        ai_probability = 0.3
    
    # تحديد النتيجة
    if ai_probability > 0.7:
        note = "نص ذو احتمالية عالية للذكاء الاصطناعي"
    elif ai_probability < 0.3:
        note = "نص بشري واضح"
    else:
        note = "النتيجة غير حاسمة"
    
    return {
        "ai_probability": round(ai_probability, 3),
        "human_probability": round(1 - ai_probability, 3),
        "note": note,
        "confidence": 80,
        "language": detect_language_advanced(text),
        "analysis": {
            "word_count": len(words),
            "avg_sentence_length": round(avg_sentence_len, 1)
        }
    }

# ========== نقاط الوصول الرئيسية ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """الصفحة الرئيسية"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "AI Detector Pro", "version": "2.0.0"}
    )

@app.get("/api/health")
async def health_check():
    """فحص حالة الخادم"""
    return {
        "status": "healthy",
        "service": "AI Detector Pro",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": ["ai_detection", "plagiarism_check", "file_processing", "multi_language"]
    }

@app.post("/api/detect_ai")
async def detect_ai(payload: Dict):
    """كشف الذكاء الاصطناعي"""
    try:
        text = payload.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="النص مطلوب")
        
        result = advanced_ai_detection(text)
        result["method"] = "advanced_algorithm"
        return result
            
    except Exception as e:
        logger.exception("Error in /api/detect_ai")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check_plagiarism")
async def check_plagiarism(payload: Dict):
    """فحص الانتحال"""
    try:
        doc = payload.get("doc", "")
        references = payload.get("references", [])
        
        # محاكاة بسيطة للنتيجة
        results = []
        for i in range(len(references)):
            score = 0.1 + (i * 0.1)  # مثال بسيط
            status = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
            results.append({
                "ref_index": i,
                "score": round(score, 2),
                "percentage": round(score * 100, 2),
                "status": status
            })
        
        return {
            "scores": results,
            "summary": {
                "total_references": len(references),
                "highest_similarity": 0.3,
                "average_similarity": 0.2
            }
        }
    except Exception as e:
        logger.exception("Error in /api/check_plagiarism")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """الحصول على إحصائيات النظام"""
    return {
        "total_uploads": 0,
        "server_time": datetime.now().isoformat(),
        "server_uptime": "running",
        "features_enabled": {
            "ai_detection": True,
            "plagiarism_check": True,
            "multi_language": True
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """نقطة وصول للاختبار"""
    return {
        "message": "✅ الخادم يعمل بنجاح!",
        "endpoints": [
            "/api/health",
            "/api/detect_ai",
            "/api/check_plagiarism",
            "/api/stats"
        ],
        "server_time": datetime.now().isoformat()
    }

# ========== معالجة أخطاء ==========

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "الصفحة غير موجودة", "path": str(request.url)}
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"خطأ في الخادم: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "حدث خطأ داخلي في الخادم"}
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 AI Detector Pro - FastAPI Server")
    print("🌐 http://localhost:8000")
    print("📚 http://localhost:8000/api-docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
