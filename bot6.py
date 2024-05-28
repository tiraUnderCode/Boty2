from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# مراحل الحوار
(NU, DA, DN, TA, RESULT, ATTEMPT_NUMBER, SHOW_DATA, EDIT_DATA, ANALYSIS) = range(9)

def start(update: Update, context):
    context.user_data['attempts_data'] = []
    context.user_data['current_attempt'] = 0
    context.user_data['excluded'] = []
    update.message.reply_text("שלום! אני אבקש ממך נתונים עבור 10 ניסיונות. בואו נתחיל בניסיון הראשון.")
    update.message.reply_text("אנא הזן את מספר הניסיון:")
    return NU

def nu(update: Update, context):
    context.user_data['nu'] = int(update.message.text)
    update.message.reply_text("אנא הזן את התאריך ללא פסיקים (לדוגמה, 270524):")
    return DA

def da(update: Update, context):
    context.user_data['da'] = int(update.message.text)
    update.message.reply_text("אנא הזן את היום במספרים (לדוגמה, 02):")
    return DN

def dn(update: Update, context):
    context.user_data['dn'] = int(update.message.text)
    update.message.reply_text("אנא הזן את השעה (לדוגמה, 1800):")
    return TA

def ta(update: Update, context):
    context.user_data['ta'] = int(update.message.text)
    update.message.reply_text("אנא הזן את התוצאה:")
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
        next_nu = context.user_data['nu'] + 1
        next_da = int(str(context.user_data['da'])[:-2] + f"{int(str(context.user_data['da'])[-2:]) + 1:02d}")
        update.message.reply_text(f"עכשיו, ניסיון מספר {context.user_data['current_attempt'] + 1}. אנא הזן את מספר הניסיון (ניחוש: {next_nu}):")
        context.user_data['nu'] = next_nu
        context.user_data['da'] = next_da
        return NU
    else:
        update.message.reply_text("נתוני כל הניסיונות העשרה נאספו. אנא בחר אחת מהאפשרויות למטה.")
        keyboard = [
            [InlineKeyboardButton("הניסיונות", callback_data='attempts')],
            [InlineKeyboardButton("התרגלות", callback_data='analysis')],
            [InlineKeyboardButton("התרגלות", callback_data='exclude')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('בחר:', reply_markup=reply_markup)
        return ConversationHandler.END

def button(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'attempts':
        keyboard = [[InlineKeyboardButton(str(i + 1), callback_data=f'attempt_{i}') for i in range(10)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="בחר ניסיון:", reply_markup=reply_markup)
    elif query.data.startswith('attempt_'):
        attempt_index = int(query.data.split('_')[1])
        attempt = context.user_data['attempts_data'][attempt_index]
        keyboard = [
            [InlineKeyboardButton("הצגת הנתונים", callback_data=f'show_data_{attempt_index}')],
            [InlineKeyboardButton("עריכת הנתונים", callback_data=f'edit_data_{attempt_index}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"ניסיון מספר {attempt_index + 1}", reply_markup=reply_markup)
    elif query.data.startswith('show_data_'):
        attempt_index = int(query.data.split('_')[2])
        attempt = context.user_data['attempts_data'][attempt_index]
        query.edit_message_text(text=f"בידוד מספר הניסיון {attempt_index + 1}: {attempt}")
    elif query.data.startswith('edit_data_'):
        attempt_index = int(query.data.split('_')[2])
                context.user_data['current_attempt'] = attempt_index
        query.edit_message_text(text="אנא הזן את מספר הניסיון:")
        return NU
    elif query.data == 'analysis':
        analysis_result = analyze_data(context.user_data['attempts_data'])
        query.edit_message_text(text=f"תוצאת הניתוח: {analysis_result}")
    elif query.data == 'exclude':
        excluded = context.user_data['excluded']
        exclude_result = exclude_analysis(context.user_data['attempts_data'], excluded)
        if exclude_result:
            context.user_data['excluded'] = excluded
            query.edit_message_text(text=f"תוצאת הניתוח עם הסרת {excluded[-1]}: {exclude_result}")
        else:
            query.edit_message_text(text="לא נמצא משוואה מתאימה לאחר הסרת כל המשתנים.")

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

    if mse < 1:  
        return f'{equation} (MSE: {mse})'
    else:
        excluded.append(columns[len(excluded)])
        return exclude_analysis(attempts_data, excluded)

def cancel(update: Update, context):
    update.message.reply_text('הפעולה בוטלה. אנא הקלד /start כדי להתחיל מחדש.')
    return ConversationHandler.END

def main():
    token = "6470010453:AAG4tRMuHwBiOzhOlAPEwU44hsh4TmPlTZk"
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

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

