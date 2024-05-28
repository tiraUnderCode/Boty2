import requests
from bs4 import BeautifulSoup

# URL الموقع
url = 'https://www.pais.co.il/123/archive.aspx'

# إرسال طلب HTTP للحصول على محتوى الصفحة
response = requests.get(url)
response.raise_for_status()  # التحقق من عدم وجود أخطاء في الطلب

# تحليل محتوى الصفحة باستخدام BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# البحث عن قائمة النتائج
latest_result_list = soup.find('ol', class_='cat_data_info archive _123')

if latest_result_list:
    # استخراج الأرقام من عناصر <li> داخل <ol>
    results = [li.find('div').text.strip() for li in latest_result_list.find_all('li', class_='loto_info_num _123 archive')]
    latest_result = ''.join(results)  # دمج الأرقام في سلسلة واحدة
    print(f"نتيجة السحب الأخيرة هي: {latest_result}")
else:
    print("لم يتم العثور على نتيجة السحب الأخيرة")

