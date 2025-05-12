import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import numpy as np

# 데이터 로드
df = pd.read_csv("data/filtered_medicine_info.csv")

# ATC 그룹별 개수 세기
atc_counts = df['atc_3'].value_counts()

# 2개 이상인 ATC 그룹만 남기기
valid_atcs = atc_counts[atc_counts >= 2].index
df = df[df['atc_3'].isin(valid_atcs)].copy()

# 2. 성분 정제 함수
def clean_ingredient_list(raw):
    return sorted(list({i.strip().lower() for i in str(raw).split('/') if i.strip()}))

df['ing_list'] = df['ing_en'].fillna('').apply(clean_ingredient_list)

# 3. 벡터화용 문자열 생성
df['joined_ings'] = df['ing_list'].apply(lambda x: ' | '.join(x))

# 4. CountVectorizer 적용 (multi-hot encoding)
def pipe_split_tokenizer(text):
    return text.split(' | ')

vectorizer = CountVectorizer(tokenizer=pipe_split_tokenizer)
X = vectorizer.fit_transform(df['joined_ings'])

# 5. 라벨 인코딩 (ATC 코드 → 숫자)
le = LabelEncoder()
y = le.fit_transform(df['atc_3'])

# 희소 행렬 → numpy 배열로 변환
X_values = X.toarray()
y_values = y

# 훈련/검증 분할
X_train, X_val, y_train, y_val = train_test_split(
    X_values, y_values, test_size=0.2, random_state=42, stratify=y_values
)

# DMatrix 변환
dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(X_val, label=y_val)

# 하이퍼파라미터
params = {
    "objective": "multi:softprob",
    "num_class": len(le.classes_),
    "eval_metric": "mlogloss",
    "max_depth": 6,
    "eta": 0.1,
    "seed": 42
}

# 학습
evallist = [(dtrain, 'train'), (dval, 'eval')]
xgb_model = xgb.train(params, dtrain, num_boost_round=100, evals=evallist, early_stopping_rounds=10)

# 저장
xgb_model.save_model("xgb_atc_model.json")


joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(le, "label_encoder.pkl")

# 🔸 저장된 벡터라이저와 라벨인코더가 필요하므로 미리 저장해두자 (훈련 시 저장했다면 여기서 로드)
# joblib.dump(vectorizer, 'vectorizer.pkl')
# joblib.dump(le, 'label_encoder.pkl')

# 🔸 로드
vectorizer = joblib.load("vectorizer.pkl")
le = joblib.load("label_encoder.pkl")
model = xgb.Booster()
model.load_model("xgb_atc_model.json")

# 🔸 예측 함수
def predict_atc_from_ingredients(ingredients: list):
    # 성분 정제 및 벡터화
    ingredients = sorted(list({i.strip().lower() for i in ingredients if i.strip()}))
    input_str = ' | '.join(ingredients)
    vec = vectorizer.transform([input_str])

    # 예측
    dmatrix = xgb.DMatrix(vec)
    probs = model.predict(dmatrix)[0]
    pred_idx = np.argmax(probs)
    pred_atc = le.inverse_transform([pred_idx])[0]

    # 결과 출력
    return {
        "입력 성분": ingredients,
        "예측 ATC": pred_atc,
        "확률 TOP 3": [
            {"ATC": le.inverse_transform([i])[0], "확률": round(prob, 3)}
            for i, prob in sorted(enumerate(probs), key=lambda x: -x[1])[:3]
        ]
    }
