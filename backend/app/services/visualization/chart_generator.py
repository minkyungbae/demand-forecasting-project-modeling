from typing import Optional, List, Dict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64
import io

class ChartGenerator:
    """차트 생성기"""
    
    async def generate_chart(
        self,
        data: List[Dict],
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        columns: Optional[List[str]] = None
    ) -> str:
        """차트 생성 및 Base64 인코딩"""
        df = pd.DataFrame(data)
        
        if chart_type == "line":
            chart = self._create_line_chart(df, x_column, y_column)
        elif chart_type == "bar":
            chart = self._create_bar_chart(df, x_column, y_column)
        elif chart_type == "scatter":
            chart = self._create_scatter_chart(df, x_column, y_column)
        elif chart_type == "heatmap":
            chart = self._create_heatmap(df, columns)
        elif chart_type == "pie":
            chart = self._create_pie_chart(df, x_column, y_column, columns)
        elif chart_type == "area":
            chart = self._create_area_chart(df, x_column, y_column)
        else:
            chart = self._create_line_chart(df, x_column, y_column)
        
        # Base64 인코딩
        img_bytes = chart.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    
    def _create_line_chart(self, df: pd.DataFrame, x: Optional[str], y: Optional[str]):
        """라인 차트 생성"""
        if x and y:
            fig = px.line(df, x=x, y=y)
        else:
            fig = px.line(df)
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, x: Optional[str], y: Optional[str]):
        """바 차트 생성"""
        if x and y:
            fig = px.bar(df, x=x, y=y)
        else:
            fig = px.bar(df)
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, x: Optional[str], y: Optional[str]):
        """스캐터 차트 생성"""
        if x and y:
            fig = px.scatter(df, x=x, y=y)
        else:
            fig = px.scatter(df)
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, columns: Optional[List[str]]):
        """히트맵 생성"""
        if columns:
            df_subset = df[columns]
        else:
            df_subset = df.select_dtypes(include=['number'])
        
        corr = df_subset.corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto")
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, x: Optional[str], y: Optional[str], columns: Optional[List[str]]):
        """파이 차트 생성"""
        # 파이 차트는 보통 카테고리 컬럼과 값 컬럼이 필요함
        if columns and len(columns) >= 2:
            # columns[0] = 카테고리, columns[1] = 값
            category_col = columns[0]
            value_col = columns[1]
            fig = px.pie(df, names=category_col, values=value_col)
        elif x and y:
            # x = 카테고리, y = 값
            fig = px.pie(df, names=x, values=y)
        elif y:
            # y만 있으면 y를 값으로, 인덱스를 카테고리로
            fig = px.pie(df, names=df.index, values=y)
        else:
            # 기본값: 첫 번째 숫자형 컬럼 사용
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                fig = px.pie(df, names=df.index, values=numeric_cols[0])
            else:
                # 숫자형 컬럼이 없으면 첫 번째 컬럼 사용
                first_col = df.columns[0] if len(df.columns) > 0 else None
                if first_col:
                    fig = px.pie(df, names=df.index, values=first_col)
                else:
                    raise ValueError("파이 차트를 생성하기 위한 데이터가 부족합니다")
        return fig
    
    def _create_area_chart(self, df: pd.DataFrame, x: Optional[str], y: Optional[str]):
        """영역 차트 생성"""
        if x and y:
            fig = px.area(df, x=x, y=y)
        elif y:
            # y만 있으면 인덱스를 x로 사용
            fig = px.area(df, x=df.index, y=y)
        else:
            # 기본값: 첫 번째 숫자형 컬럼을 y로 사용
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                fig = px.area(df, x=df.index, y=numeric_cols[0])
            else:
                fig = px.area(df)
        return fig

