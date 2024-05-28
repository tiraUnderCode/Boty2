import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# تحميل بيانات الإكسل
data = pd.read_excel('results.xlsx')

# عرض البيانات الأولية
print(data.head())

# رسم البيانات لفهم التوزيع
plt.plot(data['numbers'])
plt.xlabel('Index')
plt.ylabel('Number')
plt.title('Distribution of Numbers')
plt.show()

# تحليل التوزيع الإحصائي
mean = data['numbers'].mean()
median = data['numbers'].median()
std_dev = data['numbers'].std()

print(f'Mean: {mean}, Median: {median}, Standard Deviation: {std_dev}')

# استخراج الأنماط المحتملة
def analyze_patterns(data):
    numbers = data['numbers']
    differences = np.diff(numbers)
    print("Differences between consecutive numbers:")
    print(differences)
    
    # تحليل الأنماط البسيطة (الزيادة الثابتة، الضرب الثابت، إلخ.)
    increment_pattern = all(d == differences[0] for d in differences)
    if increment_pattern:
        print(f"Pattern detected: Increment by {differences[0]}")
    else:
        print("No simple increment pattern detected.")
    
    # البحث عن نمط الضرب الثابت
    ratios = numbers[1:] / numbers[:-1]
    multiplication_pattern = all(r == ratios[0] for r in ratios)
    if multiplication_pattern:
        print(f"Pattern detected: Multiplication by {ratios[0]}")
    else:
        print("No simple multiplication pattern detected.")
    
    # تحليل نمط التسلسل الخطي
    slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(numbers)), numbers)
    print(f"Linear regression slope: {slope}, intercept: {intercept}, r_value: {r_value}")
    
    if abs(r_value) > 0.9:  # معامل التحديد يجب أن يكون قريبًا من 1 لنمط خطي
        print("Pattern detected: Linear sequence")
    else:
        print("No clear linear pattern detected.")
    
    return differences, ratios, slope, intercept, r_value

# تطبيق تحليل الأنماط
differences, ratios, slope, intercept, r_value = analyze_patterns(data)

# توقع الرقم التالي بناءً على الأنماط المكتشفة
def predict_next_number(data, differences, ratios, slope, intercept, r_value):
    numbers = data['numbers']
    increment_pattern = all(d == differences[0] for d in differences)
    
    if increment_pattern:
        next_number = numbers.iloc[-1] + differences[0]
        print(f"Predicted next number (increment pattern): {next_number}")
        return next_number
    
    multiplication_pattern = all(r == ratios[0] for r in ratios)
    
    if multiplication_pattern:
        next_number = numbers.iloc[-1] * ratios[0]
        print(f"Predicted next number (multiplication pattern): {next_number}")
        return next_number
    
    if abs(r_value) > 0.9:
        next_index = len(numbers)
        next_number = slope * next_index + intercept
        print(f"Predicted next number (linear pattern): {next_number}")
        return next_number
    
    print("No simple pattern detected to predict the next number.")
    return None

# توقع الرقم التالي
predicted_number = predict_next_number(data, differences, ratios, slope, intercept, r_value)

