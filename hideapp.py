from PIL import Image
import sys

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def hide_message(image_path, message, output_path="stego_image.png"):

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인 필요.")
        return False
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}")
        return False

    original_mode = img.mode
    if img.mode not in ['RGB', 'RGBA']:
        print(f"경고: 이미지 모드가 {img.mode}입니다. RGB로 변환하여 처리.")
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        img = img.convert('RGB')


    width, height = img.size
    pixels = img.load()

    message_to_hide = message + "###END###"
    binary_message = text_to_binary(message_to_hide)
    

    max_bits_to_hide = width * height * 3
    if len(binary_message) > max_bits_to_hide:
        print(f"오류: 메시지가 너무 김.")
        print(f"이미지에 숨길 수 있는 최대 비트 수: {max_bits_to_hide} bits")
        print(f"숨길 메시지 비트 수: {len(binary_message)} bits")
        print("메시지 길이를 줄이거나 더 큰 이미지를 사용 필요.")
        return False

    data_index = 0
    message_length = len(binary_message)

    for y in range(height):
        for x in range(width):
            if data_index < message_length:
                r, g, b = pixels[x, y] 


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
        print(f"메시지가 숨겨진 이미지가 '{output_path}'로 성공적으로 저장됨")
        return True
    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}")
        return False

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    original_img_name = input("원본 이미지 파일명: ")
    secret_message = input("이미지에 숨길 메시지: ")
    stego_img_name = input("메시지를 숨긴 후 저장할 이미지 파일명: ")

    if hide_message(original_img_name, secret_message, stego_img_name):
        print("메시지 숨기기 작업 완료.")
    else:
        print("메시지 숨기기 작업 실패.")