const TelegramBot = require('node-telegram-bot-api');
const xlsx = require('xlsx');
const brain = require('brain.js');
const token = '6470010453:AAG4tRMuHwBiOzhOlAPEwU44hsh4TmPlTZk';

const bot = new TelegramBot(token, { polling: true });

// اقرأ ملف الإكسل
const workbook = xlsx.readFile('results.xlsx');
const sheet_name_list = workbook.SheetNames;
const resultsSheet = workbook.Sheets[sheet_name_list[0]];
const results = xlsx.utils.sheet_to_json(resultsSheet, { header: 1 });

// تحويل النتائج إلى أرقام
const parsedResults = results.map(row => row.map(cell => parseInt(cell, 10)));

// إعداد شبكة عصبية
const net = new brain.NeuralNetwork();

// تدريب الشبكة العصبية باستخدام البيانات الموجودة
const trainingData = parsedResults.map(row => ({
  input: row.slice(0, -1).map(num => num / 10), // تطبيع البيانات
  output: row.slice(1).map(num => num / 10)
}));

net.train(trainingData);

// دالة لتحليل النتائج وإيجاد الأنماط
function analyzeResults(data) {
  let summary = {};
  data.forEach(row => {
    row.forEach(number => {
      if (summary[number]) {
        summary[number]++;
      } else {
        summary[number] = 1;
      }
    });
  });
  return summary;
}

// دالة لتخمين النتائج المستقبلية بناءً على التحليل
function predictNextResults(data, count) {
  const predictions = [];
  let lastRow = data[data.length - 1];

  for (let i = 0; i < count; i++) {
    const input = lastRow.map(num => num / 10);
    const output = net.run(input).map(num => Math.round(num * 10));
    predictions.push(output);
    lastRow = output;
  }

  return predictions;
}

// أوامر البوت
bot.onText(/\/analyze/, (msg) => {
  const chatId = msg.chat.id;
  const analysis = analyzeResults(parsedResults);
  bot.sendMessage(chatId, `ניתוח: ${JSON.stringify(analysis)}`);
});

bot.onText(/\/predict/, (msg) => {
  const chatId = msg.chat.id;
  const predictions = predictNextResults(parsedResults, 15);
  const predictionText = predictions.map(pred => pred.join(', ')).join('\n');
  bot.sendMessage(chatId, `תחזיות הבאות:\n${predictionText}`);
});

bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "ברוך הבא! השתמש ב-/analyze כדי לנתח תוצאות ו-/predict כדי לחזות את התוצאה הבאה.");
});

