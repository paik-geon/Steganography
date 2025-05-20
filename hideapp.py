# stego_hide.py

from PIL import Image
import sys

def text_to_binary(text):
    """
    텍스트를 8비트 이진 문자열로 변환합니다.
    예: 'A' -> '01000001'
    """
    return ''.join(format(ord(char), '08b') for char in text)

def hide_message(image_path, message, output_path="stego_image.png"):
    """
    이미지에 메시지를 숨깁니다 (인코딩).
    PNG 파일 사용 권장.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
        return False
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}")
        return False

    # 이미지 모드 확인 및 RGB로 변환 (RGBA의 경우 알파 채널은 건드리지 않음)
    original_mode = img.mode
    if img.mode not in ['RGB', 'RGBA']:
        print(f"경고: 이미지 모드가 {img.mode}입니다. RGB로 변환하여 처리합니다.")
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        # RGBA 이미지는 RGB만 조작하고 알파 채널은 유지하기 위해 분리했다 다시 합칠 수도 있지만,
        # 여기서는 단순하게 RGB로 변환하여 처리합니다 (알파 채널 정보는 손실됨).
        # 더 고급 처리 시에는 img.split() 후 RGB 채널만 조작하고 merge해야 함.
        img = img.convert('RGB')


    width, height = img.size
    pixels = img.load() # 픽셀 데이터에 직접 접근

    # 메시지 끝을 표시하기 위한 마커 추가 (매우 중요!)
    message_to_hide = message + "###END###"
    binary_message = text_to_binary(message_to_hide)
    
    # 숨길 수 있는 최대 비트 수 계산 (RGB 3채널 기준)
    max_bits_to_hide = width * height * 3
    if len(binary_message) > max_bits_to_hide:
        print(f"오류: 메시지가 너무 깁니다.")
        print(f"이미지에 숨길 수 있는 최대 비트 수: {max_bits_to_hide} bits")
        print(f"숨길 메시지 비트 수: {len(binary_message)} bits")
        print("메시지 길이를 줄이거나 더 큰 이미지를 사용하세요.")
        return False

    data_index = 0
    message_length = len(binary_message)

    for y in range(height):
        for x in range(width):
            if data_index < message_length:
                r, g, b = pixels[x, y] # 현재 픽셀의 RGB 값 가져오기

                # 각 채널의 LSB를 조작하여 비트 숨기기
                new_r = (r & ~1) | int(binary_message[data_index])
                data_index += 1
                
                new_g = g
                if data_index < message_length:
                    new_g = (g & ~1) | int(binary_message[data_index])
                    data_index += 1
                
                new_b = b
                if data_index < message_length:
                    new_b = (b & ~1) | int(binary_message[data_index])
                    data_index += 1

                pixels[x, y] = (new_r, new_g, new_b)
            else:
                break
        if data_index >= message_length:
            break

    try:
        img.save(output_path)
        print(f"메시지가 숨겨진 이미지가 '{output_path}'로 성공적으로 저장되었습니다.")
        return True
    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}")
        return False

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    original_img_name = input("원본 이미지 파일명: ")
    secret_message = input("이미지에 숨길 메시지를 입력하세요: ")
    stego_img_name = input("메시지를 숨긴 후 저장할 이미지 파일명: ")

    if hide_message(original_img_name, secret_message, stego_img_name):
        print("메시지 숨기기 작업이 완료되었습니다.")
    else:
        print("메시지 숨기기 작업에 실패했습니다.")