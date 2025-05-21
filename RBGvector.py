from PIL import Image
import os

def get_and_save_all_pixel_rgb(image_path, output_txt_path):
    try:
        img = Image.open(image_path)

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        width, height = img.size

        with open(output_txt_path, 'w') as f:
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    f.write(f"{r},{g},{b}\n")

        print(f"성공: '{image_path}'의 모든 픽셀 RGB 값이 '{output_txt_path}'에 저장됨.")
        print(f"총 {width * height}개의 픽셀이 저장됨.")

    except FileNotFoundError:
        print(f"오류: '{image_path}' 파일을 찾을 수 없음. 경로를 확인 필요.")
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    image_file = 'encrypted.png'
    output_text_file = 'original_rgb_values.txt'

    get_and_save_all_pixel_rgb(image_file, output_text_file)

    print(f"\n'{output_text_file}' 파일의 처음 10줄 내용:")
    try:
        with open(output_text_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(line.strip())
                else:
                    break
    except FileNotFoundError:
        print("생성된 텍스트 파일을 찾을 수 없음.")
    except Exception as e:
        print(f"파일 읽기 중 오류 발생: {e}")