"""
FastAPI приложение для мониторинга конкурентов
"""
import base64
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings, logger
from backend.models.schemas import (
    TextAnalysisRequest,
    ParseDemoRequest,
    TextAnalysisResponse,
    ImageAnalysisResponse,
    ParseDemoResponse,
    ParsedContent,
    HistoryResponse,
)
from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service

app = FastAPI(
    title="Competitor Monitor",
    description="AI ассистент для анализа конкурентов через текст, изображения и парсинг сайтов.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

service_logger = logging.getLogger("competitor_monitor.main")


@app.on_event("startup")
async def startup_event():
    service_logger.info("Запуск приложения Competitor Monitor")
    if not settings.proxy_api_key:
        service_logger.warning("PROXY_API_KEY не задан. Запросы к OpenAI API не будут работать.")


@app.get("/", summary="Статус API")
async def root():
    return {
        "service": "Competitor Monitor",
        "version": "0.1.0",
        "status": "ok",
        "openai_configured": bool(settings.proxy_api_key)
    }


@app.get("/health", summary="Проверка состояния")
async def health_check():
    return {"status": "healthy"}


@app.post("/analyze_text", response_model=TextAnalysisResponse, summary="Анализ текста конкурента")
async def analyze_text(request: TextAnalysisRequest):
    try:
        analysis = await openai_service.analyze_text(request.text)
        history_service.add_entry(
            request_type="text_analysis",
            request_summary=request.text[:200],
            response_summary=analysis.summary[:300]
        )
        return TextAnalysisResponse(success=True, analysis=analysis)
    except Exception as error:
        service_logger.exception("Ошибка при анализе текста")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/analyze_image", response_model=ImageAnalysisResponse, summary="Анализ изображения")
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Файл изображения пустой")

        image_base64 = base64.b64encode(content).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"

        analysis = await openai_service.analyze_image(image_base64, mime_type=mime_type)
        history_service.add_entry(
            request_type="image_analysis",
            request_summary=f"image:{file.filename} ({mime_type})",
            response_summary=analysis.description[:300]
        )
        return ImageAnalysisResponse(success=True, analysis=analysis)
    except HTTPException:
        raise
    except Exception as error:
        service_logger.exception("Ошибка при анализе изображения")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/parse_demo", response_model=ParseDemoResponse, summary="Парсинг сайта конкурента и анализ")
async def parse_demo(request: ParseDemoRequest):
    try:
        title, h1, first_paragraph, screenshot_bytes, error = await parser_service.parse_url(request.url)
        if error:
            service_logger.warning(f"Ошибка парсинга URL: {error}")
            return ParseDemoResponse(success=False, error=error)

        screenshot_base64 = parser_service.screenshot_to_base64(screenshot_bytes) if screenshot_bytes else None
        analysis = await openai_service.analyze_parsed_content(title, h1, first_paragraph)

        parsed_content = ParsedContent(
            url=request.url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
            analysis=analysis
        )

        history_service.add_entry(
            request_type="parse_demo",
            request_summary=request.url,
            response_summary=analysis.summary[:300] if analysis else "Парсинг выполнен"
        )

        return ParseDemoResponse(success=True, data=parsed_content)
    except Exception as error:
        service_logger.exception("Ошибка при парсинге сайта")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/parse_all", summary="Парсинг всех сайтов из конфигурации и сохранение в историю")
async def parse_all():
    try:
        results = await parser_service.parse_configured_sites()
        return JSONResponse({"success": True, "results": results})
    except Exception as error:
        service_logger.exception("Ошибка при парсинге всех сайтов")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/history", response_model=HistoryResponse, summary="Получить историю запросов")
async def get_history():
    items = history_service.get_history()
    return HistoryResponse(items=items, total=len(items))


@app.delete("/history", summary="Очистить историю запросов")
async def clear_history():
    history_service.clear_history()
    return JSONResponse({"success": True, "message": "История очищена"})
