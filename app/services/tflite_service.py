import numpy as np
from PIL import Image
import io
import tensorflow as tf
import os

class TFLiteModel:
    def __init__(self, model_path: str):
        """TFLite 모델 초기화"""
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # 입력/출력 정보 가져오기
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # 클래스 이름 TXT 파일 로드
            self.class_names = self._load_class_names(model_path)
            
            print(f"모델 로드 완료: {model_path}")
            print(f"입력 형태: {self.input_details[0]['shape']}")
            print(f"출력 형태: {self.output_details[0]['shape']}")
            print(f"클래스 수: {len(self.class_names)}")
            
        except Exception as e:
            print(f"모델 로드 실패: {str(e)}")
            raise e
    
    def _load_class_names(self, model_path: str) -> list:
        """클래스 이름 TXT 파일 로드"""
        try:
            # 모델 파일과 같은 디렉토리에서 labels_final.txt 찾기
            model_dir = os.path.dirname(model_path)
            class_names_path = os.path.join(model_dir, "labels_final.txt")
            
            if os.path.exists(class_names_path):
                with open(class_names_path, 'r', encoding='utf-8') as f:
                    # 각 줄을 읽어서 리스트로 변환
                    class_names = [line.strip() for line in f.readlines() if line.strip()]
                print(f"클래스 이름 로드 완료: {class_names_path}")
                return class_names
            else:
                print(f"클래스 이름 파일을 찾을 수 없음: {class_names_path}")
                # 기본 클래스 이름 반환 (인덱스 기반)
                return [f"음식_{i}" for i in range(100)]
                
        except Exception as e:
            print(f"클래스 이름 로드 실패: {str(e)}")
            # 기본 클래스 이름 반환
            return [f"음식_{i}" for i in range(100)]
    
    def preprocess_image(self, image_data: bytes, target_size: tuple = (224, 224)):
        """이미지 전처리"""
        try:
            # 바이트 데이터를 PIL Image로 변환
            image = Image.open(io.BytesIO(image_data))
            
            # RGB로 변환
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 리사이즈
            image = image.resize(target_size)
            
            # numpy 배열로 변환 및 정규화
            image_array = np.array(image, dtype=np.float32)
            image_array = image_array / 255.0  # 0-1 정규화
            
            # 배치 차원 추가
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            print(f"이미지 전처리 실패: {str(e)}")
            raise e
    
    def predict(self, image_data: bytes):
        """예측 수행"""
        try:
            # 이미지 전처리
            input_data = self.preprocess_image(image_data)
            
            # 입력 데이터 설정
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            
            # 추론 실행
            self.interpreter.invoke()
            
            # 결과 가져오기
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # 확률 배열을 1차원으로 변환
            probabilities = output_data[0]
            
            # 최고 확률 인덱스 찾기
            max_index = np.argmax(probabilities)
            max_probability = float(probabilities[max_index])
            
            # 상위 5개 예측 결과
            top_5_indices = np.argsort(probabilities)[-5:][::-1]
            top_5_predictions = []
            
            for idx in top_5_indices:
                # 배열 인덱스 범위 체크
                if idx < len(self.class_names):
                    food_name = self.class_names[idx]
                else:
                    food_name = f"음식_{idx}"
                
                top_5_predictions.append({
                    "food_name": food_name,
                    "probability": float(probabilities[idx]),
                    "confidence": f"{float(probabilities[idx]) * 100:.2f}%"
                })
            
            # 예측된 음식 이름
            if max_index < len(self.class_names):
                predicted_food = self.class_names[max_index]
            else:
                predicted_food = f"음식_{max_index}"
            
            return {
                "success": True,
                "predicted_food": predicted_food,
                "confidence": max_probability,
                "confidence_percentage": f"{max_probability * 100:.2f}%",
                "top_5_predictions": top_5_predictions,
                "raw_probabilities": probabilities.tolist()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        