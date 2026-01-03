from typing import List, Dict, Optional, Tuple
from fastapi import UploadFile
from datetime import datetime
import pandas as pd
import io
from app.core.database import get_database
from app.models.file import FileUploadResponse, FileInfoResponse, CSVDataResponse, RelatedColumnsResponse, ColumnsResponse
from app.services.file.file_repository import FileRepository
from app.services.file.file_analysis_config_repository import FileAnalysisConfigRepository
from app.services.solution.llm_service import LLMService
from app.services.user.user_service import UserService
from app.services.feature.lag_feature_generator import LagFeatureGenerator

class FileService:
    """파일 서비스"""
    
    def __init__(self):
        self.repository = FileRepository()
        self.config_repository = FileAnalysisConfigRepository()
        self.user_service = UserService()
        self.llm_service = LLMService()
    
    def _detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """컬럼 타입 감지"""
        column_types = {}
        for col in df.columns:
            if pd.api.types.is_integer_dtype(df[col]):
                column_types[col] = 'integer'
            elif pd.api.types.is_float_dtype(df[col]):
                column_types[col] = 'float'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                column_types[col] = 'datetime'
            elif pd.api.types.is_bool_dtype(df[col]):
                column_types[col] = 'boolean'
            else:
                column_types[col] = 'string'
        return column_types
    
    async def upload_file(self, file: UploadFile, user_id: str, target_column: Optional[str] = None) -> FileUploadResponse:
        """CSV 파일 업로드 및 파싱"""
        file_id = None
        try:
            # 파일 읽기
            contents = await file.read()
            
            # 인코딩 자동 감지 및 CSV 읽기
            df = None
            encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin-1', 'iso-8859-1']
            
            # chardet 라이브러리가 있으면 사용 (더 정확한 인코딩 감지)
            try:
                import chardet
                detected = chardet.detect(contents)
                if detected and detected.get('encoding'):
                    detected_encoding = detected['encoding'].lower()
                    # 감지된 인코딩을 우선 시도
                    if detected_encoding not in encodings:
                        encodings.insert(0, detected_encoding)
            except ImportError:
                pass  # chardet이 없으면 기본 인코딩 리스트 사용
            
            for encoding in encodings:
                try:
                    # BytesIO를 사용하여 인코딩 시도
                    df = pd.read_csv(io.BytesIO(contents), encoding=encoding)
                    break
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    continue
            
            if df is None:
                raise ValueError("CSV 파일을 읽을 수 없습니다. 지원되는 인코딩 형식이 아닙니다. (시도한 인코딩: " + ", ".join(encodings) + ")")
            
            # 파일 정보 저장 (Sales Collection)
            file_id = f"file_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            upload_time = datetime.now()
            
            # 업로드 상태: processing
            await self.repository.update_upload_status(file_id, "processing")
            
            # 컬럼 타입 감지
            columns_type = self._detect_column_types(df)
            
            # 수량/금액 컬럼 자동 매칭
            matched_columns = await self.llm_service.match_quantity_and_price_columns(df.columns.tolist())
            
            sales_data = {
                'file_id': file_id,
                'user_id': user_id,
                'file_name': file.filename,  # 가게이름_날짜.csv 형식
                'file_size': len(contents),
                'columns_list': df.columns.tolist(),
                'columns_type': columns_type,  # JSON 형식
                'columns_count': len(df.columns),
                'matched_quantity_column': matched_columns.get('quantity_column'),  # 자동 매칭된 수량 컬럼
                'matched_price_column': matched_columns.get('price_column'),  # 자동 매칭된 금액 컬럼
                'target_column': target_column,  # 사용자가 지정한 예측 대상 컬럼명
                'upload_time': upload_time,
                'upload_status': 'processing'
            }
            
            sales_info = await self.repository.save_sales_info(sales_data)
            
            # CSV 데이터 저장 (CSV Collection)
            await self.repository.save_csv_data(file_id, user_id, df)
            
            # 업로드 상태: completed
            await self.repository.update_upload_status(file_id, 'completed')
            
            # 유저의 file_upload_count 증가
            await self.user_service.increment_file_upload_count(user_id)
            
            # 날짜 컬럼 자동 감지 (빠른 감지)
            lag_generator = LagFeatureGenerator()
            data_sample = df.head(20).to_dict('records')
            detected_date_column = lag_generator.find_date_column(df.columns.tolist(), data_sample)
            
            # 컬럼 추천 결과 초기화
            grouping_columns = None
            directly_related_columns = None
            valid_columns = None
            related_columns = None
            final_columns = None
            lag_feature_columns = None
            
            # 자동으로 컬럼 추천 및 예측 피처 생성 (동기적으로 실행하여 결과를 응답에 포함)
            # 사용자가 지정한 target_column이 있으면 그것을 사용, 없으면 matched_quantity_column 사용
            final_target_column = target_column or matched_columns.get('quantity_column')
            if final_target_column:
                try:
                    # 컬럼 추천 수행
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"컬럼 추천 시작: file_id={file_id}, target_column={final_target_column}")
                    
                    suggestion_result = await self.suggest_related_columns(file_id, final_target_column, user_id)
                    grouping_columns = suggestion_result.grouping_columns
                    directly_related_columns = suggestion_result.excluded_columns  # excluded_columns가 올바른 필드명
                    valid_columns = suggestion_result.valid_columns
                    related_columns = suggestion_result.related_columns
                    final_columns = suggestion_result.final_columns
                    
                    logger.info(f"컬럼 추천 완료: grouping={len(grouping_columns)}, valid={len(valid_columns)}")
                    
                    # config에서 date_column 가져오기 (LLM이 추출한 날짜 컬럼)
                    config = await self.config_repository.get_config(file_id, final_target_column)
                    if config and config.get('date_column'):
                        detected_date_column = config.get('date_column')
                        logger.info(f"날짜 컬럼 감지: {detected_date_column}")
                    
                    # 예측 피처 생성 및 저장 (date_column이 있을 때만)
                    if detected_date_column:
                        logger.info(f"Lag 피처 생성 시작: date_column={detected_date_column}")
                        try:
                            preprocess_result = await self.generate_preprocessed_features(file_id, final_target_column, user_id)
                            lag_feature_columns = preprocess_result.get('lag_feature_columns', [])
                            logger.info(f"Lag 피처 생성 완료: {len(lag_feature_columns)}개 생성")
                        except Exception as preprocess_error:
                            # Lag 피처 생성 실패는 경고로 처리 (파일 업로드는 성공)
                            logger.warning(f"Lag 피처 생성 실패 (파일 업로드는 성공): {str(preprocess_error)}")
                            lag_feature_columns = []
                    else:
                        logger.warning("날짜 컬럼이 감지되지 않아 Lag 피처를 생성할 수 없습니다")
                        lag_feature_columns = []
                        
                except Exception as e:
                    # 자동 생성 실패해도 파일 업로드는 성공으로 처리
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"컬럼 추천 또는 피처 생성 중 오류 발생: {str(e)}")
                    logger.error(f"상세 오류:\n{traceback.format_exc()}")
                    # 콘솔에도 출력
                    print(f"❌ 컬럼 추천/피처 생성 오류: {str(e)}")
                    traceback.print_exc()
                    pass
            
            return FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                file_size=len(contents),
                columns=df.columns.tolist(),
                row_count=len(df),
                uploaded_at=upload_time,
                matched_quantity_column=matched_columns.get('quantity_column'),
                matched_price_column=matched_columns.get('price_column'),
                date_column=detected_date_column,
                target_column=final_target_column,
                grouping_columns=grouping_columns,
                directly_related_columns=directly_related_columns,
                valid_columns=valid_columns,
                related_columns=related_columns,
                final_columns=final_columns,
                lag_feature_columns=lag_feature_columns
            )
        except Exception as e:
            # 업로드 실패 시 상태 업데이트
            if 'file_id' in locals():
                await self.repository.update_upload_status(file_id, 'failed')
            raise e
    
    async def list_files(self, user_id: str) -> List[FileInfoResponse]:
        """파일 목록 조회"""
        files = await self.repository.get_sales_by_user(user_id)
        result = []
        for file in files:
            # CSV 컬렉션에서 실제 행 수 조회
            row_count = await self.repository.get_csv_row_count(file['file_id'])
            result.append(
                FileInfoResponse(
                    file_id=file['file_id'],
                    filename=file['file_name'],
                    file_size=file['file_size'],
                    columns=file['columns_list'],
                    row_count=row_count,
                    uploaded_at=file['upload_time'],
                    user_id=file['user_id'],
                    matched_quantity_column=file.get('matched_quantity_column'),
                    matched_price_column=file.get('matched_price_column'),
                    target_column=file.get('target_column')
                )
            )
        return result
    
    async def get_file_info(self, file_id: str, user_id: str) -> FileInfoResponse:
        """파일 정보 조회"""
        file_info = await self.repository.get_sales_info(file_id, user_id)
        if file_info:
            # CSV 컬렉션에서 실제 행 수 조회
            row_count = await self.repository.get_csv_row_count(file_id)
            return FileInfoResponse(
                file_id=file_info['file_id'],
                filename=file_info['file_name'],
                file_size=file_info['file_size'],
                columns=file_info['columns_list'],
                row_count=row_count,
                uploaded_at=file_info['upload_time'],
                user_id=file_info['user_id'],
                matched_quantity_column=file_info.get('matched_quantity_column'),
                matched_price_column=file_info.get('matched_price_column'),
                target_column=file_info.get('target_column')
            )
        return None
    
    async def get_csv_data(
        self, 
        file_id: str, 
        page: int, 
        page_size: int,
        user_id: str
    ) -> CSVDataResponse:
        """CSV 데이터 조회 (페이지네이션)"""
        # 파일 소유권 확인
        file_info = await self.repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        # 데이터 조회
        skip = (page - 1) * page_size
        data = await self.repository.get_csv_data(file_id, skip, page_size)
        
        # 총 행 수 계산 (CSV Collection에서)
        db = await get_database()
        csv_collection = db['csv']
        total_rows = await csv_collection.count_documents({'file_id': file_id})
        
        return CSVDataResponse(
            file_id=file_id,
            data=data,
            total_rows=total_rows,
            page=page,
            page_size=page_size
        )
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """파일 삭제 (분석 설정도 함께 삭제)"""
        # 분석 설정 삭제
        await self.config_repository.delete_config(file_id)
        # 파일 삭제
        return await self.repository.delete_file(file_id, user_id)
    
    async def get_columns(self, file_id: str, user_id: str) -> ColumnsResponse:
        """컬럼 목록 조회"""
        file_info = await self.repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        columns = file_info.get('columns_list', [])
        if not columns:
            raise ValueError("컬럼 정보를 찾을 수 없습니다")
        
        return ColumnsResponse(
            file_id=file_id,
            columns=columns
        )
    
    async def suggest_related_columns(
        self,
        file_id: str,
        target_column: str,
        user_id: str
    ) -> RelatedColumnsResponse:
        """특정 컬럼과 직접적으로 연관된 컬럼만 제외하고 나머지 컬럼 추천 (결과 저장)"""
        # 파일 정보 조회
        file_info = await self.repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        columns = file_info.get('columns_list', [])
        columns_type = file_info.get('columns_type', {})
        if not columns:
            raise ValueError("컬럼 정보를 찾을 수 없습니다")
        
        # 대상 컬럼이 존재하는지 확인
        if target_column not in columns:
            raise ValueError(f"컬럼 '{target_column}'을 찾을 수 없습니다")
        
        # 데이터 샘플 가져오기 (최대 20행) - LLM에 제공
        data_sample = await self.repository.get_csv_data(file_id, 0, 20)
        
        # LLM으로 컬럼 분류 (그룹화 컬럼, 직접 연관 컬럼, 유효 컬럼)
        suggestion = await self.llm_service.suggest_related_columns_simple(
            target_column=target_column,
            all_columns=columns,
            data_sample=data_sample
        )
        
        grouping_columns = suggestion.get("grouping_columns", [])
        directly_related_columns = suggestion.get("directly_related_columns", [])
        valid_columns_base = suggestion.get("valid_columns", [])  # Lag 피처 생성 전 기본 유효 컬럼
        date_column = suggestion.get("date_column")
        
        # 날짜 컬럼이 없으면 자동 감지
        lag_generator = LagFeatureGenerator()
        if not date_column:
            date_column = lag_generator.find_date_column(columns, data_sample)
        
        # Lag 피처 생성 (유효 컬럼에 대해)
        lag_feature_columns = []
        valid_columns_with_lag = valid_columns_base.copy()
        
        if date_column and valid_columns_base:
            try:
                # 전체 데이터 로드 (Lag 피처 생성용)
                all_data = await self.repository.get_csv_data(file_id, 0, 10000)
                if all_data and len(all_data) > 0:
                    # Lag 피처 생성
                    processed_df, new_lag_columns = await lag_generator.generate_lag_features(
                        data=all_data,
                        date_column=date_column,
                        target_column=target_column,
                        numeric_columns=valid_columns_base,  # 유효 컬럼에 대해서만 Lag 생성
                        group_by_columns=grouping_columns,  # 그룹화 컬럼으로 그룹별 Lag 생성
                        lag_periods=[7, 30]  # 1주, 1개월
                    )
                    
                    lag_feature_columns = new_lag_columns
                    valid_columns_with_lag.extend(new_lag_columns)  # Lag 피처를 유효 컬럼에 추가
                    
                    # 생성된 Lag 피처가 포함된 전처리 데이터 저장
                    await self.repository.save_preprocessed_data(
                        file_id=file_id,
                        user_id=user_id,
                        df=processed_df,
                        target_column=target_column
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Lag 피처 생성 또는 저장 중 오류: {str(e)}")
                pass
        
        # 각 컬럼의 통계 정보 계산
        column_stats = {}
        if data_sample:
            df_sample = pd.DataFrame(data_sample)
            for col in columns:
                if col in df_sample.columns:
                    unique_count = df_sample[col].nunique()
                    total_count = len(df_sample)
                    data_type = columns_type.get(col, 'unknown')
                    
                    column_stats[col] = {
                        'unique_count': unique_count,
                        'total_count': total_count,
                        'unique_ratio': unique_count / total_count if total_count > 0 else 0,
                        'data_type': data_type
                    }
        
        # 그룹화 컬럼 추천 (LLM이 이미 grouping_columns를 제공했으므로, 필요시 추가 검증)
        group_by_columns = grouping_columns.copy()  # LLM이 추천한 그룹화 컬럼 사용
        
        # 최종 컬럼 목록: target_column + 유효 컬럼 (Lag 피처 포함)
        final_columns = [target_column] + valid_columns_with_lag
        
        # 제품별 개수 및 컬럼 타입별 개수 계산
        # 주요 그룹화 컬럼 (시각화용) - 첫 번째 그룹화 컬럼 사용
        primary_group_by_column, product_counts, column_type_counts = await self._analyze_file_stats(
            file_id, target_column, final_columns, columns_type, group_by_columns if group_by_columns else None
        )
        
        # 분석 설정 저장 (모든 정보 포함)
        await self.config_repository.save_config(
            file_id=file_id,
            user_id=user_id,
            target_column=target_column,
            related_columns=suggestion.get("related_columns", []),  # 하위 호환성
            excluded_columns=directly_related_columns,
            final_columns=final_columns,
            group_by_column=primary_group_by_column,  # 시각화용 주요 그룹화 컬럼
            group_by_columns=group_by_columns,  # 상관계수 분석용 모든 그룹화 컬럼 목록
            grouping_columns=grouping_columns,  # 그룹화 전용 컬럼 (브랜드, 카테고리 등)
            valid_columns=valid_columns_with_lag,  # 유효 컬럼 (Lag 피처 포함)
            date_column=date_column,  # 날짜 컬럼명
            lag_feature_columns=lag_feature_columns,  # 생성된 Lag 피처 컬럼 목록
            product_counts=product_counts,
            column_type_counts=column_type_counts
        )
        
        # 하위 호환성을 위해 related_columns는 valid_columns + grouping_columns로 구성
        related_columns_for_response = valid_columns_with_lag + grouping_columns
        
        return RelatedColumnsResponse(
            file_id=file_id,
            target_column=target_column,
            grouping_columns=grouping_columns,  # 그룹화 전용 컬럼 (별도 표시)
            valid_columns=valid_columns_with_lag,  # 유효 컬럼 (Lag 피처 포함, 별도 표시)
            related_columns=related_columns_for_response,  # 유효 컬럼 + 그룹화 컬럼 (하위 호환성)
            excluded_columns=directly_related_columns,
            final_columns=final_columns,
            reason=suggestion.get("reason", "컬럼 분류 완료")
        )
    
    async def _analyze_file_stats(
        self,
        file_id: str,
        target_column: str,
        final_columns: list,
        columns_type: dict,
        group_by_columns: Optional[List[str]] = None
    ) -> Tuple[Optional[str], Dict[str, int], Dict[str, int]]:
        """파일 통계 분석: 제품별 개수, 컬럼 타입별 개수"""
        # 데이터 로드 (일부만)
        data = await self.repository.get_csv_data(file_id, 0, 10000)
        
        if not data:
            return None, {}, {}
        
        df = pd.DataFrame(data)
        
        # 제품별 그룹화 컬럼 자동 감지
        group_by_column = None
        product_counts = {}
        
        group_keywords = ['상품', '제품', 'product', 'item', 'id', 'ID', '명']
        exclude_columns = {target_column} | set(final_columns)
        candidate_columns = set(df.columns) - exclude_columns
        
        for col in candidate_columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in group_keywords):
                unique_count = df[col].nunique()
                total_count = len(df)
                if 1 < unique_count < total_count * 0.5:
                    group_by_column = col
                    # 제품별 개수 계산
                    product_counts = df[col].value_counts().to_dict()
                    # 문자열 키를 문자열로 변환 (JSON 직렬화를 위해)
                    product_counts = {str(k): int(v) for k, v in product_counts.items()}
                    break
        
        # 컬럼 타입별 개수 계산 (final_columns 기준)
        column_type_counts = {
            'int': 0,
            'varchar': 0,
            'date': 0,
            'object': 0
        }
        
        for col in final_columns:
            if col not in df.columns:
                continue
            
            # columns_type에서 타입 확인
            col_type = columns_type.get(col, 'string')
            
            # pandas 타입으로 재확인
            if pd.api.types.is_integer_dtype(df[col]):
                mapped_type = 'int'
            elif pd.api.types.is_float_dtype(df[col]):
                mapped_type = 'int'  # float도 int로 카운트
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                mapped_type = 'date'
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                # 컬럼 타입 매핑
                if 'date' in str(col_type).lower() or 'datetime' in str(col_type).lower():
                    mapped_type = 'date'
                elif 'string' in str(col_type).lower() or 'varchar' in str(col_type).lower():
                    mapped_type = 'varchar'
                else:
                    mapped_type = 'object'
            else:
                mapped_type = 'object'
            
            column_type_counts[mapped_type] = column_type_counts.get(mapped_type, 0) + 1
        
        return group_by_column, product_counts, column_type_counts
    
    async def generate_preprocessed_features(
        self,
        file_id: str,
        target_column: str,
        user_id: str
    ) -> Dict:
        """전처리 피처 생성 (Lag 피처 포함) 및 저장"""
        # 파일 정보 조회
        file_info = await self.repository.get_sales_info(file_id, user_id)
        if not file_info:
            raise ValueError("파일을 찾을 수 없습니다")
        
        # 설정 조회 (컬럼 추천 결과)
        config = await self.config_repository.get_config(file_id, target_column)
        if not config:
            raise ValueError("컬럼 추천 설정을 먼저 생성해야 합니다. /features/{file_id}/suggest 엔드포인트를 먼저 호출하세요.")
        
        # 설정에서 필요한 정보 추출
        date_column = config.get('date_column')
        valid_columns = config.get('valid_columns', [])
        grouping_columns = config.get('grouping_columns', [])
        lag_feature_columns = config.get('lag_feature_columns', [])
        
        if not date_column:
            raise ValueError("날짜 컬럼이 설정되지 않았습니다.")
        
        # 이미 Lag 피처가 생성되어 있으면 다시 생성하지 않음 (suggest_related_columns에서 이미 생성됨)
        if lag_feature_columns and len(lag_feature_columns) > 0:
            # 이미 생성된 Lag 피처가 있으면 전처리 데이터만 저장 (Lag 피처 재생성 없이)
            all_data = await self.repository.get_csv_data(file_id, 0, 10000)
            if not all_data or len(all_data) == 0:
                raise ValueError("데이터를 찾을 수 없습니다")
            
            # DataFrame으로 변환 (이미 Lag 피처가 포함된 valid_columns 사용)
            df = pd.DataFrame(all_data)
            
            # 전처리 데이터 저장 (Lag 피처는 이미 포함되어 있음)
            save_result = await self.repository.save_preprocessed_data(
                file_id=file_id,
                user_id=user_id,
                df=df,
                target_column=target_column
            )
            
            return {
                'file_id': file_id,
                'target_column': target_column,
                'row_count': save_result['row_count'],
                'original_columns': list(df.columns),
                'preprocessed_columns': save_result['columns'],
                'lag_feature_columns': lag_feature_columns,  # 이미 생성된 Lag 피처 반환
                'total_columns': len(save_result['columns']),
                'preprocessed_time': save_result['preprocessed_time']
            }
        
        # Lag 피처가 없으면 생성 (하위 호환성)
        # 원본 데이터 로드
        all_data = await self.repository.get_csv_data(file_id, 0, 10000)
        if not all_data or len(all_data) == 0:
            raise ValueError("데이터를 찾을 수 없습니다")
        
        # Lag 피처 생성
        lag_generator = LagFeatureGenerator()
        
        # Lag 피처를 생성할 기본 컬럼 (Lag 피처가 아닌 원본 컬럼만)
        # 이미 생성된 rolling_4weeks 피처도 제외
        valid_base_columns = [col for col in valid_columns if not any(lag_col in col for lag_col in ['_lag_7d', '_lag_14d', '_lag_30d', '_rolling_4weeks'])]
        
        try:
            processed_df, new_lag_columns = await lag_generator.generate_lag_features(
                data=all_data,
                date_column=date_column,
                target_column=target_column,
                numeric_columns=valid_base_columns,
                group_by_columns=grouping_columns,
                lag_periods=[7, 30]  # 1주, 1개월
            )
            
            # 전처리 데이터 저장
            save_result = await self.repository.save_preprocessed_data(
                file_id=file_id,
                user_id=user_id,
                df=processed_df,
                target_column=target_column
            )
            
            return {
                'file_id': file_id,
                'target_column': target_column,
                'row_count': save_result['row_count'],
                'original_columns': list(pd.DataFrame(all_data).columns),
                'preprocessed_columns': save_result['columns'],
                'lag_feature_columns': new_lag_columns,
                'total_columns': len(save_result['columns']),
                'preprocessed_time': save_result['preprocessed_time']
            }
        except Exception as e:
            import traceback
            traceback.format_exc()
            raise ValueError(f"전처리 피처 생성 실패: {str(e)}")

