from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import logging

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

API_TOKEN = "6679199332:AAHqGIBwKE1_9XmK6fIANglEZQ78yzvHn-Q"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# مراحل الحوار
(NU, DA, DN, TA, RESULT) = range(5)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {'attempts_data': [], 'current_attempt': 0, 'excluded': []}
    await message.answer("مرحبًا! سأطلب منك بيانات لـ 10 محاولات. لنبدأ بالمحاولة الأولى.")
    await message.answer("من فضلك، أدخل رقم التجربة:")
    return NU

@dp.message_handler(state=NU)
async def nu(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['nu'] = int(message.text)
    await message.answer("من فضلك، أدخل التاريخ بدون فواصل (مثلاً 270524):")
    return DA

@dp.message_handler(state=DA)
async def da(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['da'] = int(message.text)
    await message.answer("من فضلك، أدخل اليوم بالأعداد (مثلاً 02):")
    return DN

@dp.message_handler(state=DN)
async def dn(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['dn'] = int(message.text)
    await message.answer("من فضلك، أدخل الساعة (مثلاً 1800):")
    return TA

@dp.message_handler(state=TA)
async def ta(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['ta'] = int(message.text)
    await message.answer("من فضلك، أدخل النتيجة:")
    return RESULT

@dp.message_handler(state=RESULT)
async def result(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['result'] = int(message.text)
    user_data[user_id]['attempts_data'].append({
        'nu': user_data[user_id]['nu'],
        'da': user_data[user_id]['da'],
        'dn': user_data[user_id]['dn'],
        'ta': user_data[user_id]['ta'],
        'result': user_data[user_id]['result']
    })
    user_data[user_id]['current_attempt'] += 1

    if user_data[user_id]['current_attempt'] < 10:
        next_nu = user_data[user_id]['nu'] + 1
        next_da = int(str(user_data[user_id]['da'])[:-2] + f"{int(str(user_data[user_id]['da'])[-2:]) + 1:02d}")
        await message.answer(f"الآن، المحاولة رقم {user_data[user_id]['current_attempt'] + 1}. من فضلك، أدخل رقم التجربة (تخميني: {next_nu}):")
        user_data[user_id]['nu'] = next_nu
        user_data[user_id]['da'] = next_da
        return NU
    else:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("المحاولات", callback_data='attempts'),
            InlineKeyboardButton("التحليل", callback_data='analysis'),
            InlineKeyboardButton("استبعاد", callback_data='exclude')
        )
        await message.answer("تم جمع البيانات لجميع المحاولات العشرة. اختر أحد الأزرار أدناه.", reply_markup=keyboard)
        return

@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == 'attempts':
        keyboard = InlineKeyboardMarkup(row_width=5)
        buttons = [InlineKeyboardButton(str(i + 1), callback_data=f'attempt_{i}') for i in range(10)]
        keyboard.add(*buttons)
        await bot.send_message(user_id, "اختر محاولة:", reply_markup=keyboard)
    elif data.startswith('attempt_'):
        attempt_index = int(data.split('_')[1])
        attempt = user_data[user_id]['attempts_data'][attempt_index]
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("إظهار البيانات", callback_data=f'show_data_{attempt_index}'),
            InlineKeyboardButton("تعديل البيانات", callback_data=f'edit_data_{attempt_index}')
        )
        await bot.send_message(user_id, f"محاولة رقم {attempt_index + 1}", reply_markup=keyboard)
    elif data.startswith('show_data_'):
        attempt_index = int(data.split('_')[2])
        attempt = user_data[user_id]['attempts_data'][attempt_index]
        await bot.send_message(user_id, f"بيانات المحاولة رقم {attempt_index + 1}: {attempt}")
    elif data.startswith('edit_data_'):
        attempt_index = int(data.split('_')[2])
        user_data[user_id]['current_attempt'] = attempt_index
        await bot.send_message(user_id, "من فضلك، أدخل رقم التجربة:")
        return NU
    elif data == 'analysis':
        analysis_result = analyze_data(user_data[user_id]['attempts_data'])
        await bot.send_message(user_id, f"نتيجة التحليل: {analysis_result}")
    elif data == 'exclude':
        excluded = user_data[user_id]['excluded']
        exclude_result = exclude_analysis(user_data[user_id]['attempts_data'], excluded)
        if exclude_result:
            user_data[user_id]['excluded'] = excluded
            await bot.send_message(user_id, f"نتيجة التحليل مع استبعاد {excluded[-1]}: {exclude_result}")
        else:
            await bot.send_message(user_id, "لم يتم العثور على معادلة متوافقة بعد استبعاد جميع المتغيرات.")

def analyze_data(attempts_data):
    X = np.array([[d['nu'], d['da'], d['dn'], d['ta']] for d in attempts_data])
    y = np.array([d['result'] for d in attempts_data])
    model = LinearRegression()
    model.fit(X, y)
    coefficients = model.coef_
    intercept = model.intercept_
    equation = f'result = {coefficients[0]}*NU + {coefficients[1]}*DA + {coefficients[2]}*DN + {coefficients[3]}*TA + {intercept}'
    mse = mean_squared_error(y, model.predict(X))
    return f'{equation} (MSE: {mse})'

def exclude_analysis(attempts_data, excluded):
    columns = ['nu', 'da', 'dn', 'ta']
    remaining_columns = [col for col in columns if col not in excluded]

    if not remaining_columns:
        return None

    X = np.array([[d[col] for col in remaining_columns] for d in attempts_data])
    y = np.array([d['result'] for d in attempts_data])
    model = LinearRegression()
    model.fit(X, y)
    coefficients = model.coef_
    intercept = model.intercept_
    mse = mean_squared_error(y, model.predict(X))

    equation = 'result = ' + ' + '.join([f'{coeff}*{col.upper()}' for coeff, col in zip(coefficients, remaining_columns)]) + f' + {intercept}'

    if mse < 1:  # قم بتعديل هذا الشرط حسب الحاجة
        return f'{equation} (MSE: {mse})'
    else:
        excluded.append(columns[len(excluded)])
        return exclude_analysis(attempts_data, excluded)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
