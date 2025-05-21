# Steganography

### hideapp.py
hideapp.py는 사진을 지정하고 지정된 사진에 넣을 문자열을 받아 사진의 픽셀 RGB 값을 수정하여 스테가노그래피 값을 삽입하는 파일

### reveal.py
reveal.py는 hideapp.py에서 사진에 삽입한 정보를 불러와 사용자에게 확인시켜주는 파일

### RGBvector.py
RGBvector.py는 위에서 저장된 사진들의 RGB 값을 불러와 텍스트 파일로 재생성시키는 파일

### contrast_rgb_values.py
contrast_rgb_values.py는 RGBvector.py에서 생성된 텍스트 파일 2개를 비교, 대조하여 사용자에게 값을 제공하는 파일


### *original_rgb_values.txt와 encrypted_rgb_valuse.txt는 파일 인코딩 이슈로 업로드 되어있지 않음.*


# 코드설명

## hideapp.py
```python
from PIL import Image # 이미지 처리 기능을 제공하는 Pillow 라이브러리를 임포트합니다.
import sys           # 시스템 관련 기능을 사용하기 위해 임포트하지만, 이 코드에서는 직접 사용되지 않습니다.

def text_to_binary(text):
    """
    입력받은 텍스트 문자열을 8비트 이진 문자열로 변환하는 함수입니다.
    예시: 'A'는 ASCII 값 65이고, 이는 8비트 이진수로 '01000001'이 됩니다.
    """
    # 각 문자(char)에 대해 반복합니다.
    # ord(char): 문자를 해당 아스키(ASCII) 정수 값으로 변환합니다 (예: 'A' -> 65).
    # format(value, '08b'): 정수 값을 8비트 이진 문자열로 변환합니다.
    #                       '08b'는 결과 문자열의 길이가 8이 되도록 앞자리를 '0'으로 채우라는 의미입니다.
    # ''.join(...): 변환된 모든 8비트 이진 문자열들을 공백 없이 하나의 긴 문자열로 연결합니다.
    return ''.join(format(ord(char), '08b') for char in text)

def hide_message(image_path, message, output_path="stego_image.png"):
    """
    지정된 이미지 파일에 텍스트 메시지를 숨기고, 결과 이미지를 새로운 파일로 저장하는 함수입니다.
    PNG 파일 사용을 강력히 권장합니다. JPEG는 손실 압축으로 인해 숨겨진 데이터가 손상될 수 있습니다.

    Args:
        image_path (str): 원본 이미지 파일의 경로입니다.
        message (str): 이미지에 숨길 텍스트 메시지입니다.
        output_path (str): 메시지가 숨겨진 이미지를 저장할 파일 경로 및 이름입니다 (기본값: "stego_image.png").

    Returns:
        bool: 메시지 숨김 작업이 성공하면 True, 실패하면 False를 반환합니다.
    """
    try:
        # 1. Image.open(): 지정된 경로의 이미지 파일을 엽니다.
        img = Image.open(image_path)
    except FileNotFoundError:
        # 파일이 없을 경우 오류 메시지를 출력하고 False를 반환하여 함수를 종료합니다.
        print(f"오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
        return False
    except Exception as e:
        # 이미지 로드 중 발생할 수 있는 다른 모든 예외(오류)를 처리합니다.
        print(f"이미지 로드 중 오류 발생: {e}")
        return False

    # 2. 이미지 모드 확인 및 변환:
    # LSB 스테가노그래피는 주로 RGB 3채널에 적용되므로, 다른 모드(예: L, CMYK)는 RGB로 변환합니다.
    # RGBA (알파 채널 포함)의 경우, 투명도 정보를 유지할 수도 있지만, 이 구현에서는 단순성을 위해 RGB로 변환합니다.
    if img.mode not in ['RGB', 'RGBA']:
        print(f"경고: 이미지 모드가 {img.mode}입니다. RGB로 변환하여 처리합니다.")
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        # RGBA 이미지를 RGB로 변환하면 알파 채널 정보는 손실됩니다.
        # 알파 채널을 보존하려면 img.split()으로 채널을 분리 후 RGB만 조작하고 다시 img.merge()해야 합니다.
        img = img.convert('RGB')

    # 3. 이미지의 너비(가로 픽셀 수)와 높이(세로 픽셀 수)를 가져옵니다.
    width, height = img.size
    # 4. img.load(): 픽셀 데이터에 직접 접근하고 수정할 수 있는 PixelAccess 객체를 로드합니다.
    #    이를 통해 픽셀 값을 직접 읽고 쓸 수 있습니다.
    pixels = img.load()

    # 5. 숨길 메시지 준비: 메시지의 끝을 명확히 알리기 위해 특정 마커 "###END###"를 메시지 뒤에 추가합니다.
    #    이 마커는 메시지 추출 시 메시지의 정확한 끝을 식별하는 데 사용됩니다.
    message_to_hide = message + "###END###"
    # 6. text_to_binary() 함수를 사용하여 최종 메시지(마커 포함)를 이진 비트열로 변환합니다.
    binary_message = text_to_binary(message_to_hide)
    
    # 7. 이미지에 숨길 수 있는 최대 비트 수를 계산합니다.
    #    각 픽셀은 R, G, B 세 가지 색상 채널을 가지며, 각 채널에 1비트씩 숨길 수 있으므로,
    #    전체 픽셀 수 * 3 이 최대 숨길 수 있는 비트 수가 됩니다.
    max_bits_to_hide = width * height * 3
    # 8. 숨길 메시지의 길이가 이미지의 최대 용량을 초과하는지 검사합니다.
    if len(binary_message) > max_bits_to_hide:
        print(f"오류: 메시지가 너무 깁니다.")
        print(f"  이미지에 숨길 수 있는 최대 비트 수: {max_bits_to_hide} bits")
        print(f"  숨길 메시지 비트 수: {len(binary_message)} bits")
        print("메시지 길이를 줄이거나 더 큰 이미지를 사용하세요.")
        return False # 용량 초과 시 False를 반환하고 종료합니다.

    data_index = 0       # 현재 이미지 픽셀에 삽입할 메시지 비트의 인덱스를 추적합니다.
    message_length = len(binary_message) # 숨길 전체 이진 메시지(마커 포함)의 총 비트 길이입니다.

    # 9. 이미지의 모든 픽셀을 순회하며 메시지 비트를 삽입합니다.
    for y in range(height):    # 이미지의 세로 방향 (행)으로 반복합니다.
        for x in range(width): # 이미지의 가로 방향 (열)으로 반복합니다.
            # 숨길 메시지 비트가 아직 남아있을 경우에만 픽셀을 조작합니다.
            if data_index < message_length:
                # 현재 픽셀의 RGB 값(튜플 형태)을 가져옵니다.
                r, g, b = pixels[x, y]

                # 각 색상 채널(R, G, B)의 최하위 비트(LSB)에 메시지 비트를 삽입합니다.
                # (값 & ~1): 비트 AND 연산을 통해 현재 픽셀 값의 LSB를 0으로 만듭니다.
                #             예시: 10110111 (183) & ~00000001 (0xFFFE) -> 10110110 (182)
                # | int(binary_message[data_index]): 논리적 OR 연산을 통해 LSB가 0인 자리에 숨길 비트(0 또는 1)를 삽입합니다.
                #                                      예시: 10110110 | 1 -> 10110111 (183), 10110110 | 0 -> 10110110 (182)
                new_r = (r & ~1) | int(binary_message[data_index])
                data_index += 1 # 다음 메시지 비트로 인덱스를 이동시킵니다.
                
                new_g = g # 기본적으로 원본 G 값을 유지합니다.
                if data_index < message_length: # 다음 메시지 비트가 남아있다면 G 채널에도 삽입합니다.
                    new_g = (g & ~1) | int(binary_message[data_index])
                    data_index += 1
                
                new_b = b # 기본적으로 원본 B 값을 유지합니다.
                if data_index < message_length: # 다음 메시지 비트가 남아있다면 B 채널에도 삽입합니다.
                    new_b = (b & ~1) | int(binary_message[data_index])
                    data_index += 1

                # 변경된 RGB 값으로 현재 픽셀을 업데이트합니다.
                pixels[x, y] = (new_r, new_g, new_b)
            else:
                # 모든 메시지 비트를 숨겼다면, 더 이상 픽셀을 변경할 필요가 없으므로 내부 루프를 종료합니다.
                break
        if data_index >= message_length:
            # 모든 메시지 비트를 숨겼다면, 외부 루프도 종료합니다.
            break

    # 10. 메시지가 숨겨진 이미지를 새로운 파일로 저장합니다.
    try:
        img.save(output_path)
        print(f"메시지가 숨겨진 이미지가 '{output_path}'로 성공적으로 저장되었습니다.")
        return True # 저장 성공 시 True를 반환합니다.
    except Exception as e:
        # 이미지 저장 중 발생한 오류를 처리합니다.
        print(f"이미지 저장 중 오류 발생: {e}")
        return False # 저장 실패 시 False를 반환합니다.

# --- 스크립트가 직접 실행될 때 (import 되지 않고) 동작하는 부분 ---
if __name__ == "__main__":
    # 사용자로부터 원본 이미지 파일명, 숨길 메시지, 출력 이미지 파일명을 입력받습니다.
    original_img_name = input("원본 이미지 파일명(확장자 포함, 예: original.png): ")
    secret_message = input("이미지에 숨길 메시지를 입력하세요: ")
    stego_img_name = input("메시지를 숨긴 후 저장할 이미지 파일명(예: stego_output.png): ")

    # hide_message 함수를 호출하고, 반환 값에 따라 성공/실패 메시지를 출력합니다.
    if hide_message(original_img_name, secret_message, stego_img_name):
        print("메시지 숨기기 작업이 완료되었습니다.")
    else:
        print("메시지 숨기기 작업에 실패했습니다. 오류 메시지를 확인하세요.")
```

## reveal.py

```python
from PIL import Image # 이미지 처리 기능을 제공하는 Pillow 라이브러리를 임포트합니다.
import sys           # 시스템 관련 기능을 사용하기 위해 임포트하지만, 이 코드에서는 직접 사용되지 않습니다.

def binary_to_text(binary_string):
    """
    이진 문자열을 텍스트 문자열로 변환하는 함수입니다.
    """
    text = ""
    # 이진 문자열을 8비트(1바이트) 단위로 잘라서 처리합니다.
    # len(binary_string) // 8 * 8: 전체 길이에서 8의 배수까지만 처리하여, 불완전한 마지막 바이트로 인한 오류를 방지합니다.
    for i in range(0, len(binary_string) // 8 * 8, 8):
        byte = binary_string[i:i+8] # 현재 8비트(1바이트)를 자릅니다.
        # int(byte, 2): 이진 문자열(예: '01000001')을 10진수(아스키 코드)로 변환합니다.
        # chr(...): 10진수 아스키 코드를 해당하는 문자(예: 65 -> 'A')로 변환합니다.
        text += chr(int(byte, 2)) # 변환된 문자를 결과 텍스트에 추가합니다.
    return text

def reveal_message(image_path):
    """
    메시지가 숨겨진 이미지 파일에서 메시지를 추출하여 반환하는 함수입니다.

    Args:
        image_path (str): 메시지가 숨겨진 이미지 파일의 경로입니다.

    Returns:
        str: 추출된 텍스트 메시지입니다. 메시지 추출에 실패하면 빈 문자열을 반환합니다.
    """
    try:
        # 1. Image.open(): 지정된 경로의 이미지 파일을 엽니다.
        img = Image.open(image_path)
    except FileNotFoundError:
        # 파일이 없을 경우 오류 메시지를 출력하고 빈 문자열을 반환합니다.
        print(f"오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
        return ""
    except Exception as e:
        # 이미지 로드 중 발생할 수 있는 다른 모든 예외(오류)를 처리합니다.
        print(f"이미지 로드 중 오류 발생: {e}")
        return ""

    # 2. 이미지 모드 확인 및 변환: 인코더와 동일하게 RGB 모드로 변환하여 처리합니다.
    if img.mode not in ['RGB', 'RGBA']:
        print(f"경고: 이미지 모드가 {img.mode}입니다. RGB로 변환하여 처리합니다.")
        img = img.convert('RGB')

    # 3. 이미지의 너비와 높이를 가져옵니다.
    width, height = img.size
    # 4. img.load(): 픽셀 데이터에 직접 접근할 수 있는 PixelAccess 객체를 로드합니다.
    pixels = img.load()

    binary_message_bits = "" # 추출된 모든 이진 비트들을 저장할 변수입니다.
    
    # 5. 이미지의 모든 픽셀을 순회하며 각 채널의 LSB를 추출합니다.
    for y in range(height):    # 이미지의 세로 방향 (행)으로 반복합니다.
        for x in range(width): # 이미지의 가로 방향 (열)으로 반복합니다.
            r, g, b = pixels[x, y] # 현재 픽셀의 RGB 값을 가져옵니다.
            
            # 각 채널(R, G, B)의 LSB를 추출합니다.
            # (값 & 1): 비트 AND 연산을 통해 해당 값의 LSB만 추출합니다.
            #            예시: 10110111 (183) & 00000001 (1) -> 1
            #            예시: 10110110 (182) & 00000001 (1) -> 0
            binary_message_bits += str(r & 1) # R 채널의 LSB를 추출하여 문자열로 추가
            binary_message_bits += str(g & 1) # G 채널의 LSB를 추출하여 문자열로 추가
            binary_message_bits += str(b & 1) # B 채널의 LSB를 추출하여 문자열로 추가

            # 6. 추출된 이진 비트열의 길이가 충분히 길어지면, 메시지 종료 마커 "###END###"가 포함되어 있는지 확인합니다.
            #    '###END###'는 9글자이므로, 9 * 8 = 72비트가 필요합니다.
            if len(binary_message_bits) >= 72:
                # 현재까지 추출된 비트열을 텍스트로 변환하여 마커 포함 여부를 확인합니다.
                current_text_check = binary_to_text(binary_message_bits)
                if "###END###" in current_text_check:
                    # 마커가 발견되면, 마커 앞부분까지만 실제 메시지로 간주하고 반환합니다.
                    final_message = current_text_check.split("###END###")[0]
                    return final_message # 최종 메시지를 반환하고 함수를 종료합니다.
    
    # 7. 이미지 전체를 탐색했지만 종료 마커를 찾지 못했을 경우
    print("경고: 이미지에서 종료 마커 '###END###'를 찾지 못했습니다.")
    # 마커를 찾지 못했더라도 현재까지 추출된 (불완전할 수 있는) 메시지를 텍스트로 변환하여 반환합니다.
    return binary_to_text(binary_message_bits)

# --- 스크립트가 직접 실행될 때 (import 되지 않고) 동작하는 부분 ---
if __name__ == "__main__":
    # 사용자로부터 메시지가 숨겨진 이미지 파일명을 입력받습니다.
    stego_img_name = input("메시지가 숨겨진 이미지 파일명(확장자 포함, 예: stego_output.png): ")

    print("\n--- 메시지 추출 시도 ---")
    # reveal_message 함수를 호출하여 메시지를 추출하고, 그 결과를 출력합니다.
    extracted_text = reveal_message(stego_img_name)
    if extracted_text:
        print(f"추출된 메시지: {extracted_text}")
    else:
        print("메시지 추출에 실패했거나 숨겨진 메시지가 없습니다.")
```
## RGBvector.py
```python
from PIL import Image  # 이미지를 열고 처리하기 위해 PIL 라이브러리의 Image 모듈을 가져옵니다.
import os              # 파일 경로와 관련된 기능을 위해 os 모듈을 불러옵니다.

# 이미지의 모든 픽셀 RGB 값을 추출하여 텍스트 파일로 저장하는 함수
def get_and_save_all_pixel_rgb(image_path, output_txt_path):
    try:
        # 이미지 파일 열기
        img = Image.open(image_path)

        # 이미지 모드가 RGB가 아니면 RGB로 변환 (예: RGBA → RGB)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # 이미지의 가로(width)와 세로(height) 크기 가져오기
        width, height = img.size

        # 출력 텍스트 파일을 쓰기 모드로 열기
        with open(output_txt_path, 'w') as f:
            # 전체 픽셀 순회 (위에서 아래로, 왼쪽에서 오른쪽으로)
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))  # 해당 픽셀의 RGB 값 가져오기
                    f.write(f"{r},{g},{b}\n")       # RGB 값을 쉼표로 구분해 텍스트 파일에 저장

        # 완료 메시지 출력
        print(f"성공: '{image_path}'의 모든 픽셀 RGB 값이 '{output_txt_path}'에 저장됨.")
        print(f"총 {width * height}개의 픽셀이 저장됨.")  # 전체 픽셀 수 출력

    except FileNotFoundError:
        # 이미지 파일을 찾지 못한 경우의 에러 처리
        print(f"오류: '{image_path}' 파일을 찾을 수 없음. 경로를 확인 필요.")
    except Exception as e:
        # 그 외 다른 예외 발생 시 출력
        print(f"이미지 처리 중 오류 발생: {e}")

# --- 프로그램 실행 부분 ---
if __name__ == "__main__":
    image_file = 'encrypted.png'  # 처리할 이미지 파일 경로
    output_text_file = 'original_rgb_values.txt'  # RGB 값을 저장할 텍스트 파일 경로

    # 함수 실행: 이미지의 픽셀 RGB 값을 추출하고 텍스트 파일로 저장
    get_and_save_all_pixel_rgb(image_file, output_text_file)

    # 생성된 텍스트 파일에서 처음 10줄을 출력해서 확인
    print(f"\n'{output_text_file}' 파일의 처음 10줄 내용:")
    try:
        with open(output_text_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(line.strip())  # 앞에서 10줄만 출력 (줄바꿈 제거)
                else:
                    break
    except FileNotFoundError:
        print("생성된 텍스트 파일을 찾을 수 없음.")
    except Exception as e:
        print(f"파일 읽기 중 오류 발생: {e}")
```

## contrast_rgb_values.py
```python
import os  # 파일 존재 여부를 확인하기 위해 os 모듈을 불러옵니다.

# 두 RGB 텍스트 파일을 비교하는 함수 정의
def compare_rgb_files(original_file_path, modified_file_path):
    changed_pixels = 0      # 변경된 픽셀 수를 저장할 변수
    total_pixels = 0        # 총 비교한 픽셀 수를 저장할 변수

    # 원본 파일이 존재하는지 확인
    if not os.path.exists(original_file_path):
        print(f"오류: 원본 파일 '{original_file_path}'을 찾을 수 없음.")
        return 0, 0

    # 수정된 파일이 존재하는지 확인
    if not os.path.exists(modified_file_path):
        print(f"오류: 수정된 파일 '{modified_file_path}'을 찾을 수 없음.")
        return 0, 0

    try:
        # 두 파일을 읽기 모드로 열기
        with open(original_file_path, 'r') as original_f, \
             open(modified_file_path, 'r') as modified_f:

            # 두 파일의 각 줄을 하나씩 동시에 읽어서 비교
            for original_line, modified_line in zip(original_f, modified_f):
                total_pixels += 1  # 비교한 픽셀 수 증가

                # 줄 끝의 줄바꿈 문자 제거
                original_rgb_str = original_line.strip()
                modified_rgb_str = modified_line.strip()

                # RGB 문자열을 정수형 튜플로 변환 (예: '255,0,0' -> (255, 0, 0))
                original_rgb = tuple(map(int, original_rgb_str.split(',')))
                modified_rgb = tuple(map(int, modified_rgb_str.split(',')))

                # RGB 값이 다르면 변경된 픽셀로 간주
                if original_rgb != modified_rgb:
                    changed_pixels += 1

            # 파일을 다 읽고도 한쪽에 남은 줄이 있으면 경고 출력
            if len(original_f.readlines()) != 0 or len(modified_f.readlines()) != 0:
                print("경고: 두 파일의 픽셀 수가 다름. 정확한 비교가 어려울 수 있음.")

    # RGB 값을 정수로 변환할 때 오류가 발생하면 메시지 출력
    except ValueError as e:
        print(f"오류: 파일 내용 중 RGB 형식이 올바르지 않음. {e}")
        return 0, 0
    # 그 외 다른 예외가 발생한 경우
    except Exception as e:
        print(f"파일 비교 중 오류 발생: {e}")
        return 0, 0

    # 변경된 픽셀 수와 전체 비교 픽셀 수 반환
    return changed_pixels, total_pixels

# 프로그램 실행 시작
if __name__ == "__main__":
    # 비교할 두 파일 경로 설정
    original_rgb_file = 'original_rgb_values.txt' 
    modified_rgb_file = 'encrypted_rgb_values.txt'

    print(f"'{original_rgb_file}'와 '{modified_rgb_file}' 파일 비교 시작...")

    # 비교 함수 호출
    num_changed, num_total = compare_rgb_files(original_rgb_file, modified_rgb_file)

    # 비교가 정상적으로 이루어졌다면 결과 출력
    if num_total > 0:
        percentage_changed = (num_changed / num_total) * 100  # 변경된 비율 계산

        print(f"\n--- 비교 결과 ---")
        print(f"총 픽셀 수: {num_total}")
        print(f"변경되지 않은 픽셀 수: {num_total - num_changed}")
        print(f"변경된 픽셀 수: {num_changed}")
        print(f"전체 픽셀 중 변경된 픽셀 비율: {percentage_changed:.10f}%")

        # 분석 결과에 따라 해석 메시지 출력
        if percentage_changed == 0:
            print("모든 픽셀이 일치함. 스테가노그래피가 적용되지 않았거나, 변경 사항을 감지할 수 없음.")
        elif percentage_changed > 0 and percentage_changed < 100:
            print("일부 픽셀이 변경되었음. 스테가노그래피 적용 결과일 수 있음.")
        else:
            print("모든 픽셀이 변경되었음. 예상치 못한 결과일 수 있음.")
    else:
        print("파일 비교를 완료할 수 없음.")
```
