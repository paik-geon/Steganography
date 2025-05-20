# stego_reveal.py

from PIL import Image
import sys

def binary_to_text(binary_string):
    text = ""
    for i in range(0, len(binary_string) // 8 * 8, 8):
        byte = binary_string[i:i+8]
        text += chr(int(byte, 2))
    return text

def reveal_message(image_path):

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
        return ""
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}")
        return ""

    if img.mode not in ['RGB', 'RGBA']:
        print(f"경고: 이미지 모드가 {img.mode}입니다. RGB로 변환하여 처리합니다.")
        img = img.convert('RGB')

    width, height = img.size
    pixels = img.load()

    binary_message_bits = ""
    

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            binary_message_bits += str(r & 1)
            binary_message_bits += str(g & 1)
            binary_message_bits += str(b & 1)


            if len(binary_message_bits) >= 72:
                current_text_check = binary_to_text(binary_message_bits)
                if "###END###" in current_text_check:
                    final_message = current_text_check.split("###END###")[0]
                    return final_message
    
    print("경고: 이미지에서 종료 마커 '###END###'를 찾지 못했습니다.")
    return binary_to_text(binary_message_bits)

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    stego_img_name = input("메시지가 숨겨진 이미지 파일명: ")

    print("\n--- 메시지 추출 시도 ---")
    extracted_text = reveal_message(stego_img_name)
    if extracted_text:
        print(f"추출된 메시지: {extracted_text}")
    else:
        print("메시지 추출에 실패했거나 숨겨진 메시지가 없습니다.")