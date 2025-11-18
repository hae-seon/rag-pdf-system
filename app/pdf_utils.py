"""
PDF 유틸리티: PDF 페이지를 이미지로 변환
"""
import os
import logging
from typing import Optional
from pdf2image import convert_from_path
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pdf_page_to_image(pdf_path: str, page_number: int, dpi: int = 150) -> Optional[Image.Image]:
    """
    PDF의 특정 페이지를 이미지로 변환

    Args:
        pdf_path: PDF 파일 경로
        page_number: 페이지 번호 (0부터 시작)
        dpi: 이미지 해상도 (기본값: 150)

    Returns:
        PIL Image 객체 또는 None (에러 시)
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
            return None

        # 특정 페이지만 변환 (first_page와 last_page는 1부터 시작)
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=page_number + 1,  # pdf2image는 1부터 시작
            last_page=page_number + 1
        )

        if images:
            logger.info(f"페이지 {page_number} 이미지 변환 성공: {pdf_path}")
            return images[0]
        else:
            logger.warning(f"페이지 {page_number}를 변환할 수 없습니다.")
            return None

    except Exception as e:
        logger.error(f"PDF 페이지 이미지 변환 중 오류: {e}")
        return None


def pdf_page_to_image_bytes(pdf_path: str, page_number: int, dpi: int = 150, format: str = "PNG") -> Optional[bytes]:
    """
    PDF 페이지를 이미지 바이트로 변환 (Streamlit에서 사용)

    Args:
        pdf_path: PDF 파일 경로
        page_number: 페이지 번호 (0부터 시작)
        dpi: 이미지 해상도
        format: 이미지 포맷 (PNG, JPEG 등)

    Returns:
        이미지 바이트 또는 None
    """
    import io

    try:
        image = pdf_page_to_image(pdf_path, page_number, dpi)
        if image:
            buffer = io.BytesIO()
            image.save(buffer, format=format)
            return buffer.getvalue()
        return None
    except Exception as e:
        logger.error(f"PDF 페이지 바이트 변환 중 오류: {e}")
        return None
