import os

def compare_rgb_files(original_file_path, modified_file_path):
    changed_pixels = 0
    total_pixels = 0
    
    if not os.path.exists(original_file_path):
        print(f"오류: 원본 파일 '{original_file_path}'을 찾을 수 없음.")
        return 0, 0
    if not os.path.exists(modified_file_path):
        print(f"오류: 수정된 파일 '{modified_file_path}'을 찾을 수 없음.")
        return 0, 0

    try:
        with open(original_file_path, 'r') as original_f, \
             open(modified_file_path, 'r') as modified_f:

            for original_line, modified_line in zip(original_f, modified_f):
                total_pixels += 1
                original_rgb_str = original_line.strip()
                modified_rgb_str = modified_line.strip()

                original_rgb = tuple(map(int, original_rgb_str.split(',')))
                modified_rgb = tuple(map(int, modified_rgb_str.split(',')))

                if original_rgb != modified_rgb:
                    changed_pixels += 1
            if len(original_f.readlines()) != 0 or len(modified_f.readlines()) != 0:
                print("경고: 두 파일의 픽셀 수가 다름. 정확한 비교가 어려울 수 있음.")

    except ValueError as e:
        print(f"오류: 파일 내용 중 RGB 형식이 올바르지 않음. {e}")
        return 0, 0
    except Exception as e:
        print(f"파일 비교 중 오류 발생: {e}")
        return 0, 0

    return changed_pixels, total_pixels

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    original_rgb_file = 'original_rgb_values.txt' 
    modified_rgb_file = 'encrypted_rgb_values.txt'

    print(f"'{original_rgb_file}'와 '{modified_rgb_file}' 파일 비교 시작...")

    num_changed, num_total = compare_rgb_files(original_rgb_file, modified_rgb_file)

    if num_total > 0:
        percentage_changed = (num_changed / num_total) * 100
        print(f"\n--- 비교 결과 ---")
        print(f"총 픽셀 수: {num_total}")
        print(f"변경되지 않은 픽셀 수: {num_total - num_changed}")
        print(f"변경된 픽셀 수: {num_changed}")
        print(f"전체 픽셀 중 변경된 픽셀 비율: {percentage_changed:.10f}%")
        
        if percentage_changed == 0:
            print("모든 픽셀이 일치함. 스테가노그래피가 적용되지 않았거나, 변경 사항을 감지할 수 없음.")
        elif percentage_changed > 0 and percentage_changed < 100:
            print("일부 픽셀이 변경되었음. 스테가노그래피 적용 결과일 수 있음.")
        else:
            print("모든 픽셀이 변경되었음. 예상치 못한 결과일 수 있음.")
    else:
        print("파일 비교를 완료할 수 없음.")