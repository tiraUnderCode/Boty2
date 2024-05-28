from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import logging

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# مراحل الحوار
(NU, DA, DN, TA, RESULT, ATTEMPT_NUMBER, SHOW_DATA, EDIT_DATA, ANALYSIS) = range(9)

# متغيرات لتخزين البيانات
attempts_data = []

def start(update: Update, context):
    context.user_data['attempts_data'] = []
    context.user_data['current_attempt'] = 0
    update.message.reply_text("مرحبًا! سأطلب منك بيانات لـ 10 محاولات. لنبدأ بالمحاولة الأولى.")
    update.message.reply_text("من فضلك، أدخل رقم التجربة:")
    return NU

def nu(update: Update, context):
    context.user_data['nu'] = int(update.message.text)
    update.message.reply_text("من فضلك، أدخل التاريخ بدون فواصل:")
    return DA

def da(update: Update, context):
    context.user_data['da'] = int(update.message.text)
    update.message.reply_text("من فضلك، أدخل اليوم بالأعداد:")
    return DN

def dn(update: Update, context):
    context.user_data['dn'] = int(update.message.text)
    update.message.reply_text("من فضلك، أدخل الساعة:")
    return TA

def ta(update: Update, context):
    context.user_data['ta'] = int(update.message.text)
    update.message.reply_text("من فضلك، أدخل النتيجة:")
    return RESULT

def result(update: Update, context):
    context.user_data['result'] = int(update.message.text)
    context.user_data['attempts_data'].append({
        'nu': context.user_data['nu'],
        'da': context.user_data['da'],
        'dn': context.user_data['dn'],
        'ta': context.user_data['ta'],
        'result': context.user_data['result']
    })
    context.user_data['current_attempt'] += 1

    if context.user_data['current_attempt'] < 10:
        update.message.reply_text(f"الآن، المحاولة رقم {context.user_data['current_attempt'] + 1}. من فضلك، أدخل رقم التجربة:")
        return NU
    else:
        update.message.reply_text("تم جمع البيانات لجميع المحاولات العشرة. اختر أحد الأزرار أدناه.")
        keyboard = [
            [InlineKeyboardButton("المحاولات", callback_data='attempts')],
            [InlineKeyboardButton("التحليل", callback_data='analysis')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('اختر:', reply_markup=reply_markup)
        return ConversationHandler.END

def button(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'attempts':
        keyboard = [[InlineKeyboardButton(str(i + 1), callback_data=f'attempt_{i}') for i in range(10)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="اختر محاولة:", reply_markup=reply_markup)
    elif query.data.startswith('attempt_'):
        attempt_index = int(query.data.split('_')[1])
        attempt = context.user_data['attempts_data'][attempt_index]
        keyboard = [
            [InlineKeyboardButton("إظهار البيانات", callback_data=f'show_data_{attempt_index}')],
            [InlineKeyboardButton("تعديل البيانات", callback_data=f'edit_data_{attempt_index}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"محاولة رقم {attempt_index + 1}", reply_markup=reply_markup)
    elif query.data.startswith('show_data_'):
        attempt_index = int(query.data.split('_')[2])
        attempt = context.user_data['attempts_data'][attempt_index]
        query.edit_message_text(text=f"بيانات المحاولة رقم {attempt_index + 1}: {attempt}")
    elif query.data.startswith('edit_data_'):
        attempt_index = int(query.data.split('_')[2])
        context.user_data['current_attempt'] = attempt_index
        query.edit_message_text(text="من فضلك، أدخل رقم التجربة:")
        return NU
    elif query.data == 'analysis':
        # تنفيذ التحليل هنا
        analysis_result = analyze_data(context.user_data['attempts_data'])
        query.edit_message_text(text=f"نتيجة التحليل: {analysis_result}")

def analyze_data(attempts_data):
    # تنفيذ تحليل البيانات والعثور على المعادلة المناسبة هنا
    import numpy as np
    from sklearn.linear_model import LinearRegression

    # تحويل البيانات إلى مصفوفات
    X = np.array([[d['nu'], d['da'], d['dn'], d['ta']] for d in attempts_data])
    y = np.array([d['result'] for d in attempts_data])

    # إنشاء وتدريب نموذج الانحدار الخطي
    model = LinearRegression()
    model.fit(X, y)

    # استخراج المعاملات
    coefficients = model.coef_
    intercept = model.intercept_

    # إنشاء المعادلة
    equation = f'result = {coefficients[0]}*NU + {coefficients[1]}*DA + {coefficients[2]}*DN + {coefficients[3]}*TA + {intercept}'
    return equation

def cancel(update: Update, context):
    update.message.reply_text('تم إلغاء العملية. اكتب /start للبدء من جديد.')
    return ConversationHandler.END

def main():
    # ضع هنا مفتاح البوت
    token = "6679199332:AAHqGIBwKE1_9XmK6fIANglEZQ78yzvHn-Q"
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # إنشاء محادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NU: [MessageHandler(Filters.text & ~Filters.command, nu)],
            DA: [MessageHandler(Filters.text & ~Filters.command, da)],
            DN: [MessageHandler(Filters.text & ~Filters.command, dn)],
            TA: [MessageHandler(Filters.text & ~Filters.command, ta)],
            RESULT: [MessageHandler(Filters.text & ~Filters.command, result)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

