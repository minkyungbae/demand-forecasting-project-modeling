from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from app.core.database import get_database

class FileRepository:
    """파일 데이터 접근 레이어 (Sales Collection & CSV Collection)"""
    
    async def save_sales_info(self, sales_data: dict) -> dict:
        """Sales Collection에 파일 정보 저장"""
        db = await get_database()
        collection = db['sales']  # Sales Collection
        
        # sales_id 자동 생성 (순차적 증가)
        last_sale = await collection.find_one(
            sort=[('sales_id', -1)]
        )
        sales_id = 1 if not last_sale else last_sale.get('sales_id', 0) + 1
        
        sales_data['sales_id'] = sales_id
        await collection.insert_one(sales_data)
        return sales_data
    
    async def save_csv_data(self, file_id: str, user_id: str, df: pd.DataFrame):
        """CSV Collection에 데이터 저장"""
        db = await get_database()
        collection = db['csv']  # CSV Collection
        
        # csv_id 자동 생성
        last_csv = await collection.find_one(
            {'file_id': file_id},
            sort=[('csv_id', -1)]
        )
        csv_id = 1 if not last_csv else last_csv.get('csv_id', 0) + 1
        
        csv_upload_time = datetime.now()
        
        # 데이터프레임을 행 단위로 저장
        documents = []
        for idx, row in df.iterrows():
            documents.append({
                'csv_id': csv_id + idx,  # 각 행마다 고유 csv_id
                'file_id': file_id,
                'user_id': user_id,
                'row_index': int(idx),
                'data': row.to_dict(),
                'csv_upload_time': csv_upload_time
            })
        
        if documents:
            await collection.insert_many(documents)
    
    async def get_sales_by_user(self, user_id: str) -> List[Dict]:
        """유저의 Sales 목록 조회"""
        db = await get_database()
        collection = db['sales']
        cursor = collection.find({'user_id': user_id}).sort('upload_time', -1)
        files = await cursor.to_list(length=None)
        for file in files:
            file.pop('_id', None)
        return files
    
    async def get_sales_info(self, file_id: str, user_id: str) -> Optional[Dict]:
        """Sales 정보 조회"""
        db = await get_database()
        collection = db['sales']
        file_info = await collection.find_one({
            'file_id': file_id,
            'user_id': user_id
        })
        if file_info:
            file_info.pop('_id', None)
        return file_info
    
    async def get_csv_data(self, file_id: str, skip: int, limit: int) -> List[Dict]:
        """CSV 데이터 조회"""
        db = await get_database()
        collection = db['csv']  # CSV Collection
        cursor = collection.find({'file_id': file_id}).sort('row_index', 1).skip(skip).limit(limit)
        rows = await cursor.to_list(length=limit)
        return [row['data'] for row in rows]
    
    async def get_csv_row_count(self, file_id: str) -> int:
        """CSV 컬렉션에서 특정 file_id의 행 수 조회"""
        db = await get_database()
        collection = db['csv']
        count = await collection.count_documents({'file_id': file_id})
        return count
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """파일 삭제 (Sales + CSV)"""
        db = await get_database()
        
        # Sales 정보 삭제
        sales_collection = db['sales']
        result = await sales_collection.delete_one({
            'file_id': file_id,
            'user_id': user_id
        })
        
        if result.deleted_count > 0:
            # CSV 데이터 삭제
            csv_collection = db['csv']
            await csv_collection.delete_many({'file_id': file_id})
            return True
        
        return False
    
    async def update_upload_status(self, file_id: str, status: str):
        """업로드 상태 업데이트"""
        db = await get_database()
        collection = db['sales']
        await collection.update_one(
            {'file_id': file_id},
            {'$set': {'upload_status': status}}
        )
    
    async def get_file_info(self, file_id: str, user_id: str) -> Optional[Dict]:
        """파일 정보 조회 (호환성)"""
        return await self.get_sales_info(file_id, user_id)
    
    async def save_preprocessed_data(self, file_id: str, user_id: str, df: pd.DataFrame, target_column: str):
        """전처리 데이터 저장 (Preprocessed Data Collection)"""
        db = await get_database()
        collection = db['preprocessed_data']  # 전처리 데이터 컬렉션
        
        # 기존 전처리 데이터 삭제 (같은 file_id, target_column 조합)
        await collection.delete_many({
            'file_id': file_id,
            'target_column': target_column
        })
        
        preprocessed_time = datetime.now()
        
        # NaT (Not a Time) 및 NaN 값을 None으로 변환 (MongoDB 호환성을 위해)
        df_cleaned = df.copy()
        for col in df_cleaned.columns:
            if pd.api.types.is_datetime64_any_dtype(df_cleaned[col]):
                # datetime 컬럼의 NaT 값을 None으로 변환
                df_cleaned[col] = df_cleaned[col].where(pd.notna(df_cleaned[col]), None)
        
        # 데이터프레임을 행 단위로 저장
        documents = []
        for idx, row in df_cleaned.iterrows():
            row_dict = row.to_dict()
            
            # 모든 값을 MongoDB 호환 형식으로 변환
            cleaned_data = {}
            for key, value in row_dict.items():
                # NaT/NaN 체크 (여러 방법으로 확인)
                if value is None:
                    cleaned_data[key] = None
                elif pd.isna(value):
                    cleaned_data[key] = None
                elif isinstance(value, float) and (pd.isna(value) or str(value) == 'nan'):
                    cleaned_data[key] = None
                elif isinstance(value, pd.Timestamp):
                    # NaT인지 확인 (NaT는 pd.isna()로 체크 가능)
                    if pd.isna(value):
                        cleaned_data[key] = None
                    else:
                        # 정상적인 Timestamp는 Python datetime으로 변환
                        try:
                            cleaned_data[key] = value.to_pydatetime()
                        except (ValueError, AttributeError):
                            cleaned_data[key] = None
                elif hasattr(pd, 'NaTType') and isinstance(value, pd.NaTType):
                    # NaTType 체크 (간접적으로)
                    cleaned_data[key] = None
                elif str(type(value)) == "<class 'pandas._libs.tslibs.nattype.NaTType'>":
                    # NaTType 문자열로 체크 (안전한 방법)
                    cleaned_data[key] = None
                else:
                    # 그 외 값은 그대로 사용 (numpy 타입도 Python 기본 타입으로 변환)
                    import numpy as np
                    if isinstance(value, (np.integer, np.floating)):
                        cleaned_data[key] = value.item() if hasattr(value, 'item') else float(value)
                    elif isinstance(value, np.ndarray):
                        cleaned_data[key] = value.tolist()
                    else:
                        cleaned_data[key] = value
            
            documents.append({
                'preprocessed_id': f"preprocessed_{file_id}_{target_column}_{idx}",
                'file_id': file_id,
                'user_id': user_id,
                'target_column': target_column,
                'row_index': int(idx),
                'data': cleaned_data,
                'preprocessed_time': preprocessed_time
            })
        
        if documents:
            await collection.insert_many(documents)
        
        return {
            'file_id': file_id,
            'target_column': target_column,
            'row_count': len(documents),
            'columns': list(df.columns),
            'preprocessed_time': preprocessed_time
        }
    
    async def get_preprocessed_data(self, file_id: str, target_column: str, skip: int = 0, limit: int = 10000) -> List[Dict]:
        """전처리 데이터 조회"""
        db = await get_database()
        collection = db['preprocessed_data']
        cursor = collection.find({
            'file_id': file_id,
            'target_column': target_column
        }).sort('row_index', 1).skip(skip).limit(limit)
        rows = await cursor.to_list(length=limit)
        return [row['data'] for row in rows]
    
    async def get_preprocessed_info(self, file_id: str, target_column: str) -> Optional[Dict]:
        """전처리 데이터 정보 조회 (컬럼 목록 등)"""
        db = await get_database()
        collection = db['preprocessed_data']
        sample = await collection.find_one({
            'file_id': file_id,
            'target_column': target_column
        })
        if sample and 'data' in sample:
            # 컬럼 목록 추출
            columns = list(sample['data'].keys())
            # 전체 행 수 계산
            count = await collection.count_documents({
                'file_id': file_id,
                'target_column': target_column
            })
            return {
                'file_id': file_id,
                'target_column': target_column,
                'columns': columns,
                'row_count': count,
                'preprocessed_time': sample.get('preprocessed_time')
            }
        return None

