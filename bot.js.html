const TelegramBot = require('node-telegram-bot-api');
const xlsx = require('xlsx');
const token = '6470010453:AAG4tRMuHwBiOzhOlAPEwU44hsh4TmPlTZk';

const bot = new TelegramBot(token, {polling: true});

// اقرأ ملف الإكسل
const workbook = xlsx.readFile('results.xlsx');
const sheet_name_list = workbook.SheetNames;
const resultsSheet = workbook.Sheets[sheet_name_list[0]];
const results = xlsx.utils.sheet_to_json(resultsSheet, {header: 1});

// تحويل النتائج إلى أرقام
const parsedResults = results.map(row => row.map(cell => parseInt(cell, 10)));

// دالة لتحليل النتائج وإيجاد الأنماط
function analyzeResults(data) {
    // هنا يمكنك إضافة الخوارزميات الخاصة بك لتحليل النتائج وإيجاد الأنماط
    // هذه دالة بسيطة لتوضيح الفكرة
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
function predictNextResult(data) {
    // هنا يمكنك إضافة الخوارزميات الخاصة بك لتخمين النتائج المستقبلية
    // هذه دالة بسيطة لتوضيح الفكرة
    const lastRow = data[data.length - 1];
    return lastRow.map(num => (num + 1) % 10); // مجرد مثال
}

// أوامر البوت
bot.onText(/\/analyze/, (msg) => {
    const chatId = msg.chat.id;
    const analysis = analyzeResults(parsedResults);
    bot.sendMessage(chatId, `Analysis: ${JSON.stringify(analysis)}`);
});

bot.onText(/\/predict/, (msg) => {
    const chatId = msg.chat.id;
    const prediction = predictNextResult(parsedResults);
    bot.sendMessage(chatId, `Next prediction: ${prediction.join(', ')}`);
});

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "Welcome! Use /analyze to analyze results and /predict to predict the next result.");
});

