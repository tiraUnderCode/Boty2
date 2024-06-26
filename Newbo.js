const TelegramBot = require('node-telegram-bot-api');
const mlRegression = require('ml-regression-multivariate-linear');

// استبدل هذا بمفتاح البوت الخاص بك
const token = "6470010453:AAG4tRMuHwBiOzhOlAPEwU44hsh4TmPlTZk";

const bot = new TelegramBot(token, { polling: true });

const states = {};
const userData = {};

const NU = 'NU';
const DA = 'DA';
const DN = 'DN';
const TA = 'TA';
const RESULT = 'RESULT';

bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  states[chatId] = NU;
  userData[chatId] = { attempts_data: [], current_attempt: 0, excluded: [] };
  
  bot.sendMessage(chatId, "שלום! אני אבקש ממך נתונים עבור 10 ניסיונות. בוא נתחיל עם הניסיון הראשון.");
  bot.sendMessage(chatId, "בבקשה, הכנס את מספר הניסיון:");
});

bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  if (!states[chatId]) return;

  switch (states[chatId]) {
    case NU:
      userData[chatId].nu = parseInt(msg.text);
      states[chatId] = DA;
      bot.sendMessage(chatId, "בבקשה, הכנס את התאריך ללא רווחים (לדוגמה 270524):");
      break;
    case DA:
      userData[chatId].da = parseInt(msg.text);
      states[chatId] = DN;
      bot.sendMessage(chatId, "בבקשה, הכנס את היום במספרים (לדוגמה 02):");
      break;
    case DN:
      userData[chatId].dn = parseInt(msg.text);
      states[chatId] = TA;
      bot.sendMessage(chatId, "בבקשה, הכנס את השעה (לדוגמה 1800):");
      break;
    case TA:
      userData[chatId].ta = parseInt(msg.text);
      states[chatId] = RESULT;
      bot.sendMessage(chatId, "בבקשה, הכנס את התוצאה:");
      break;
    case RESULT:
      userData[chatId].result = parseInt(msg.text);
      userData[chatId].attempts_data.push({
        nu: userData[chatId].nu,
        da: userData[chatId].da,
        dn: userData[chatId].dn,
        ta: userData[chatId].ta,
        result: userData[chatId].result
      });
      userData[chatId].current_attempt += 1;

      if (userData[chatId].current_attempt < 10) {
        let next_nu = userData[chatId].nu + 1;
        let next_da = parseInt(userData[chatId].da.toString().slice(0, -2) + ("0" + (parseInt(userData[chatId].da.toString().slice(-2)) + 1)).slice(-2));
        userData[chatId].nu = next_nu;
        userData[chatId].da = next_da;
        states[chatId] = NU;
        bot.sendMessage(chatId, `עכשיו, ניסיון מספר ${userData[chatId].current_attempt + 1}. בבקשה, הכנס את מספר הניסיון (הערכה שלי: ${next_nu}):`);
      } else {
        states[chatId] = null;
        const opts = {
          reply_markup: {
            inline_keyboard: [
              [{ text: 'ניסיונות', callback_data: 'attempts' }],
              [{ text: 'ניתוח', callback_data: 'analysis' }],
              [{ text: 'למעט', callback_data: 'exclude' }]
            ]
          }
        };
        bot.sendMessage(chatId, "הנתונים נאספו עבור כל 10 הניסיונות. בחר אחת מהאפשרויות הבאות:", opts);
      }
      break;
  }
});

bot.on('callback_query', (callbackQuery) => {
  const msg = callbackQuery.message;
  const chatId = msg.chat.id;
  const data = callbackQuery.data;

  if (data === 'attempts') {
    const opts = {
      reply_markup: {
        inline_keyboard: userData[chatId].attempts_data.map((_, i) => [{ text: (i + 1).toString(), callback_data: `attempt_${i}` }])
      }
    };
    bot.sendMessage(chatId, "בחר ניסיון:", opts);
  } else if (data.startsWith('attempt_')) {
    const attemptIndex = parseInt(data.split('_')[1]);
    const attempt = userData[chatId].attempts_data[attemptIndex];
    const opts = {
      reply_markup: {
        inline_keyboard: [
          [{ text: 'הצג נתונים', callback_data: `show_data_${attemptIndex}` }],
          [{ text: 'ערוך נתונים', callback_data: `edit_data_${attemptIndex}` }]
        ]
      }
    };
    bot.sendMessage(chatId, `ניסיון מספר ${attemptIndex + 1}`, opts);
  } else if (data.startsWith('show_data_')) {
    const attemptIndex = parseInt(data.split('_')[2]);
    const attempt = userData[chatId].attempts_data[attemptIndex];
    bot.sendMessage(chatId, `נתוני הניסיון מספר ${attemptIndex + 1}: ${JSON.stringify(attempt)}`);
  } else if (data.startsWith('edit_data_')) {
    const attemptIndex = parseInt(data.split('_')[2]);
    userData[chatId].current_attempt = attemptIndex;
    states[chatId] = NU;
    bot.sendMessage(chatId, "בבקשה, הכנס את מספר הניסיון:");
  } else if (data === 'analysis') {
    const analysisResult = analyzeData(userData[chatId].attempts_data);
    bot.sendMessage(chatId, `תוצאת הניתוח: ${analysisResult}`);
  } else if (data === 'exclude') {
    const excluded = userData[chatId].excluded;
    const excludeResult = excludeAnalysis(userData[chatId].attempts_data, excluded);
    if (excludeResult) {
      userData[chatId].excluded = excluded;
      bot.sendMessage(chatId, `תוצאת הניתוח עם חריגת ${excluded[excluded.length - 1]}: ${excludeResult}`);
    } else {
      bot.sendMessage(chatId, "לא נמצאה נוסחה תואמת לאחר חריגת כל המשתנים.");
    }
  }
});

function analyzeData(attemptsData) {
  const X = attemptsData.map(d => [d.nu, d.da, d.dn, d.ta]);
  const y = attemptsData.map(d => d.result);
  const model = new mlRegression(X, y);
  const coefficients = model.coefficients;
  const intercept = model.intercept;
  const equation = `result = ${coefficients[0]}*NU + ${coefficients[1]}*DA + ${coefficients[2]}*DN + ${coefficients[3]}*TA + ${intercept}`;
  const mse = meanSquaredError(y, model.predict(X));
  return `${equation} (MSE: ${mse})`;
}

function meanSquaredError(y_true, y_pred) {
  const n = y_true.length;
  let sum = 0;
  for (let i = 0; i < n; i++) {
    sum += Math.pow((y_true[i] - y_pred[i]), 2);
  }
  return sum / n;
}

function excludeAnalysis(attemptsData, excluded) {
  const columns = ['nu', 'da', 'dn', 'ta'];
  const remainingColumns = columns.filter(col => !excluded.includes(col));

  if (remainingColumns.length === 0) return null;

  const X = attemptsData.map(d => remainingColumns.map(col => d[col]));
  const y = attemptsData.map(d => d.result);
  const model = new mlRegression(X, y);
  const coefficients = model.coefficients;
  const intercept = model.intercept;
  const mse = meanSquaredError(y, model.predict(X));

  const equation = `result = ${coefficients[0]}*${remainingColumns[0].toUpperCase()} + ${coefficients[1]}*${remainingColumns[1].toUpperCase()} + ${coefficients[2]}*${remainingColumns[2].toUpperCase()} + ${intercept} (MSE: ${mse})`;
  return equation;
}
