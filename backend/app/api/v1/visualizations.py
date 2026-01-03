from fastapi import APIRouter, Depends, HTTPException, Response, Query
from app.models.visualization import VisualizationRequest, VisualizationResponse, ProductListResponse, VisualizationDetailResponse
from app.services.visualization.visualization_service import VisualizationService
from app.dependencies import get_current_user
from app.core.database import get_database
from app.utils.constants import CHART_TYPES
from typing import List
from datetime import datetime
import base64

router = APIRouter()

def get_visualization_service() -> VisualizationService:
    """시각화 서비스 의존성"""
    return VisualizationService()

@router.get("/chart-types", summary="지원하는 차트 타입 목록 조회")
async def get_chart_types():
    """
    지원하는 차트 타입 목록 조회
    
    시각화 생성 시 사용할 수 있는 모든 차트 타입을 반환합니다.
    
    반환되는 차트 타입:
    - **line**: 선 그래프 (시계열 데이터 추세 확인)
    - **bar**: 막대 그래프 (카테고리별 비교)
    - **scatter**: 산점도 (두 변수 간 관계 확인)
    - **heatmap**: 히트맵 (다중 변수 간 상관관계)
    - **pie**: 파이 차트 (비율 표현)
    - **area**: 영역 그래프 (누적 데이터 표현)
    """
    return {
        "chart_types": CHART_TYPES,
        "descriptions": {
            "line": "선 그래프 - 시계열 데이터의 추세를 확인할 때 사용",
            "bar": "막대 그래프 - 카테고리별 값을 비교할 때 사용",
            "scatter": "산점도 - 두 변수 간의 관계를 확인할 때 사용",
            "heatmap": "히트맵 - 다중 변수 간의 상관관계를 시각화할 때 사용",
            "pie": "파이 차트 - 전체 대비 비율을 표현할 때 사용",
            "area": "영역 그래프 - 누적 데이터나 여러 시계열을 표현할 때 사용"
        }
    }

@router.post("/create", response_model=VisualizationResponse, status_code=201, summary="데이터 시각화 생성")
async def create_visualization(
    request: VisualizationRequest,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    데이터 시각화 생성
    
    업로드된 CSV 파일의 데이터를 기반으로 다양한 유형의 차트를 생성합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID (파일 업로드 시 지정한 target_column이 자동으로 사용됩니다)
    - **chart_type**: 차트 유형 (line, bar, scatter, heatmap 등)
    - **target_column**: (선택사항) 시각화하고 싶은 주요 컬럼명. None이면 파일 업로드 시 지정한 target_column 사용
    - **x_column**: (선택사항) X축에 사용할 컬럼명. target_column이 지정되면 LLM이 자동 추천
    - **y_column**: (선택사항) Y축에 사용할 컬럼명. target_column이 지정되면 LLM이 자동 추천
    - **columns**: (선택사항) 다중 컬럼 차트에 사용할 컬럼 목록. target_column이 지정되면 LLM이 자동 추천
    
    **자동 모드**:
    - target_column이 None이면 파일 업로드 시 지정한 target_column이 자동으로 사용됩니다.
    - target_column이 지정되면 LLM이 자동으로 적절한 x_column, y_column, columns를 추천합니다.
    
    생성된 차트는 Base64 인코딩된 이미지로 반환되며, 웹 페이지나 리포트에 바로 사용할 수 있습니다.
    시각화 결과는 데이터베이스에 저장되어 나중에 다시 조회할 수 있습니다.
    """
    try:
        # target_column이 None이면 파일 정보에서 가져오기
        target_column = request.target_column
        if not target_column:
            from app.services.file.file_repository import FileRepository
            file_repository = FileRepository()
            file_info = await file_repository.get_sales_info(request.file_id, current_user['user_id'])
            if file_info:
                target_column = file_info.get('target_column')
        
        result = await visualization_service.create_visualization(
            file_id=request.file_id,
            chart_type=request.chart_type,
            target_column=target_column,
            x_column=request.x_column,
            y_column=request.y_column,
            columns=request.columns,
            user_id=current_user['user_id']
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{visualization_id}", response_model=VisualizationResponse, summary="시각화 결과 조회")
async def get_visualization(
    visualization_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    시각화 결과 조회
    
    이전에 생성한 시각화 결과를 조회합니다.
    
    - **visualization_id**: 조회할 시각화의 고유 ID
    
    저장된 차트 이미지와 시각화 메타데이터(차트 타입, 사용된 컬럼 등)를 반환합니다.
    존재하지 않는 시각화 ID인 경우 404 에러가 반환됩니다.
    """
    try:
        result = await visualization_service.get_visualization(visualization_id)
        if not result:
            raise HTTPException(status_code=404, detail="시각화를 찾을 수 없습니다")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{visualization_id}/image", summary="시각화 이미지 직접 조회 (Swagger UI에서 확인용)")
async def get_visualization_image(
    visualization_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    시각화 이미지를 직접 반환 (PNG 형식)
    
    Swagger UI나 브라우저에서 이미지를 직접 볼 수 있도록 이미지를 반환합니다.
    
    - **visualization_id**: 조회할 시각화의 고유 ID
    
    브라우저에서 이 URL을 직접 열면 차트 이미지를 볼 수 있습니다.
    """
    try:
        db = await get_database()
        collection = db['visualizations']
        viz = await collection.find_one({'visualization_id': visualization_id})
        
        if not viz:
            raise HTTPException(status_code=404, detail="시각화를 찾을 수 없습니다")
        
        # 사용자 권한 확인
        if viz.get('user_id') != current_user['user_id']:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        # Base64 디코딩
        chart_data = viz.get('chart_data', '')
        if not chart_data:
            raise HTTPException(status_code=404, detail="이미지 데이터가 없습니다")
        
        image_bytes = base64.b64decode(chart_data)
        
        # 이미지를 직접 반환
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=visualization_{visualization_id}.png"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/products/count-bar", response_model=VisualizationDetailResponse, summary="전체 상품별 count 막대그래프 생성")
async def get_product_count_bar_chart(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    전체 상품별 데이터 개수 막대그래프 생성
    
    그룹화 컬럼(보통 상품명)별로 데이터 개수를 집계하여 막대그래프로 시각화합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID
    
    반환: Base64 인코딩된 PNG 이미지
    """
    try:
        result = await visualization_service.get_product_count_bar_chart(
            file_id=file_id,
            user_id=current_user['user_id'],
            top_n=None
        )
        return {
            "visualization_id": result["visualization_id"],
            "file_id": file_id,
            "chart_type": "bar",
            "chart_data": result["chart_data"],
            "description": "전체 상품별 데이터 개수 막대그래프",
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/products/sum-bar", response_model=VisualizationDetailResponse, summary="전체 상품별 합계 막대그래프 생성")
async def get_product_sum_bar_chart(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    전체 상품별 합계 막대그래프 생성
    
    그룹화 컬럼(보통 상품명)별로 target_column(수량)의 합계를 계산하여 막대그래프로 시각화합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID
    
    반환: Base64 인코딩된 PNG 이미지
    """
    try:
        result = await visualization_service.get_product_count_bar_chart(
            file_id=file_id,
            user_id=current_user['user_id'],
            top_n=None,
            use_sum=True
        )
        return {
            "visualization_id": result["visualization_id"],
            "file_id": file_id,
            "chart_type": "bar",
            "chart_data": result["chart_data"],
            "description": "전체 상품별 합계 막대그래프",
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/products/count-bar/top10", response_model=VisualizationDetailResponse, summary="상위 10개 상품별 합계 막대그래프 생성")
async def get_top10_product_sum_bar_chart(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    상위 10개 상품별 합계 막대그래프 생성
    
    그룹화 컬럼(보통 상품명)별로 target_column(수량)의 합계를 계산하여 상위 10개만 막대그래프로 시각화합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID
    
    반환: Base64 인코딩된 PNG 이미지
    """
    try:
        result = await visualization_service.get_product_count_bar_chart(
            file_id=file_id,
            user_id=current_user['user_id'],
            top_n=10,
            use_sum=True
        )
        return {
            "visualization_id": result["visualization_id"],
            "file_id": file_id,
            "chart_type": "bar",
            "chart_data": result["chart_data"],
            "description": "상위 10개 상품별 합계 막대그래프",
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/products", response_model=ProductListResponse, summary="상품명 목록 조회")
async def get_product_list(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    상품명 목록 조회
    
    파일의 그룹화 컬럼(보통 상품명)에 있는 모든 고유한 상품명 목록을 반환합니다.
    
    - **file_id**: 조회할 파일의 고유 ID
    
    반환: 상품명 목록 (정렬된 배열)
    """
    try:
        product_list = await visualization_service.get_product_list(
            file_id=file_id,
            user_id=current_user['user_id']
        )
        return {
            "file_id": file_id,
            "products": product_list,
            "count": len(product_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/products/{product_name}/trend", response_model=VisualizationDetailResponse, summary="특정 상품의 수량 추세 선그래프 생성")
async def get_product_quantity_trend(
    file_id: str,
    product_name: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    특정 상품명의 수량 추세 선그래프 생성
    
    지정한 상품명의 수량(target_column) 추세를 날짜별로 선그래프로 시각화합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID
    - **product_name**: 조회할 상품명 (URL 인코딩 필요)
    
    반환: Base64 인코딩된 PNG 이미지
    
    **참고**: 상품명에 특수문자가 포함된 경우 URL 인코딩이 필요합니다.
    예: "상품 A" → "상품%20A"
    """
    try:
        # URL 디코딩
        from urllib.parse import unquote
        decoded_product_name = unquote(product_name)
        
        result = await visualization_service.get_product_quantity_trend(
            file_id=file_id,
            product_name=decoded_product_name,
            user_id=current_user['user_id']
        )
        return {
            "visualization_id": result["visualization_id"],
            "file_id": file_id,
            "product_name": decoded_product_name,
            "chart_type": "line",
            "chart_data": result["chart_data"],
            "description": f"{decoded_product_name}의 수량 추세",
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/correlation/heatmap", response_model=VisualizationDetailResponse, summary="상관관계 분석 결과 히트맵 생성")
async def get_correlation_heatmap(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service)
):
    """
    상관관계 분석 결과 기반 히트맵 생성
    
    상관관계 분석 결과를 기반으로 모든 피처들 간의 상관관계를 히트맵으로 시각화합니다.
    
    - **file_id**: 시각화할 파일의 고유 ID
    - 상관관계 분석이 먼저 수행되어야 합니다 (`/correlations/analyze` 엔드포인트)
    
    반환: Base64 인코딩된 PNG 이미지 및 visualization_id
    
    **참고**: 상관관계 분석을 먼저 수행하지 않으면 오류가 발생합니다.
    """
    try:
        result = await visualization_service.get_correlation_heatmap(
            file_id=file_id,
            user_id=current_user['user_id']
        )
        return {
            "visualization_id": result["visualization_id"],
            "file_id": file_id,
            "chart_type": "heatmap",
            "chart_data": result["chart_data"],
            "description": "상관관계 분석 결과 히트맵",
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

