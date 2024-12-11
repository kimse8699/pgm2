import pandas as pd

def load_excel_data(file_path):
    try:
        data = pd.read_excel(file_path)
        print("데이터가 성공적으로 로드함.")
        print(data.info)  # 첫 5행 출력
        return data
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"데이터 로드중 오류 발생!: {e}")
        return None
    
file_path = r"C:\Users\kimse\Downloads\air_pollution_data.xlsx"
df = load_excel_data(file_path)

print(df.tail())
print(df.info())
# 어떻게 데이터 전처리를 할까요
print(df.describe()) 

# 사용 예시
if __name__ == "__main__":
    file_path = "C:/pgm2/air_pollution_data.xlsx"  # 엑셀 파일 경로를 입력하세요
    data = load_excel_data(file_path)

    if data is not None:
        print("데이터 로드 및 처리가 완료되었습니다.")

print('진짜 모르것다')