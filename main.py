import pandas as pd

def load_excel_data(file_path):
    try:
        data = pd.read_excel(file_path)
        print("데이터가 성공적으로 로드되었습니다.")
        print(data.head())  # 첫 5행 출력
        return data
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        return None
    
file_path = r"C:\Users\kimse\Downloads\air_pollution_data.xlsx"
df = load_excel_data(file_path)

print(df.tail())