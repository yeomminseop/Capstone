from ing_recommendation import recommend_from_ingredients
from atc_prediction import predict_atc_from_ingredients

# result = recommend_from_ingredients(["Acetaminophen"])
#
# # 결과 요약문 출력
# print(result['summary'])
#
# # 유사 제품 표 출력
# print(result['similar_products_table'])

# 사용 예시
result = predict_atc_from_ingredients(["acetaminophen"])
print(result)