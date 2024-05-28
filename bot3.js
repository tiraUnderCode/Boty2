const TelegramBot = require('node-telegram-bot-api');
const xlsx = require('xlsx');
const token = '6470010453:AAG4tRMuHwBiOzhOlAPEwU44hsh4TmPlTZk';
const bot = new TelegramBot(token, { polling: true });

// اقرأ ملف الإكسل
const workbook = xlsx.readFile('results.xlsx');
const sheet_name_list = workbook.SheetNames;
const resultsSheet = workbook.Sheets[sheet_name_list[0]];
const results = xlsx.utils.sheet_to_json(resultsSheet, { header: 1 });

// تحويل النتائج إلى أرقام
const parsedResults = results.map(row => row.map(cell => parseInt(cell, 10)));

// دالة لتحليل النتائج
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

// دالة لتوليد تخمينات جديدة باستخدام مولد أرقام عشوائية
function generatePredictions(data) {
    const predictions = [];
    const generateUniquePrediction = () => {
        const uniquePrediction = [];
        while (uniquePrediction.length < data[0].length) {
            const randomNum = Math.floor(Math.random() * 10); // توليد أرقام بين 0 و 9
            if (!uniquePrediction.includes(randomNum)) {
                uniquePrediction.push(randomNum);
            }
        }
        return uniquePrediction;
    };

    for (let i = 0; i < 15; i++) {
        predictions.push(generateUniquePrediction());
    }
    return predictions;
}

// دالة لتحديث ملف الإكسل بالنتائج الجديدة
function updateExcel(predictions) {
    const newWorkbook = xlsx.utils.book_new();
    const newSheet = xlsx.utils.aoa_to_sheet(predictions.map(prediction => prediction.map(num => num.toString())));
    xlsx.utils.book_append_sheet(newWorkbook, newSheet, 'Predictions');
    xlsx.writeFile(newWorkbook, 'new_predictions.xlsx');
}

// دالة لتنسيق النتائج كجدول
function formatAsTable(data) {
    let table = "------------------------------\n";
    data.forEach(row => {
        table += '| ' + row.join(' | ') + ' |\n';
        table += "------------------------------\n";
    });
    return table;
}

// دالة لتنسيق تحليل النتائج كجدول
function formatAnalysisAsTable(analysis) {
    let data = Object.entries(analysis).map(([key, value]) => [key, value.toString()]);
    return formatAsTable(data);
}

// أوامر البوت
bot.onText(/\/analyze/, (msg) => {
    const chatId = msg.chat.id;
    const analysis = analyzeResults(parsedResults);
    const analysisTable = formatAnalysisAsTable(analysis);
    bot.sendMessage(chatId, `تحليل:\n${analysisTable}`);
});

bot.onText(/\/predict/, (msg) => {
    const chatId = msg.chat.id;
    const predictions = generatePredictions(parsedResults);
    updateExcel(predictions);
    const predictionsTable = formatAsTable(predictions);
    bot.sendMessage(chatId, `التنبؤات التالية:\n${predictionsTable}`);
});

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "ברוך הבא! השתמש ב /analyze כדי לנתח תוצאות ו /predict כדי לחזות תוצאות עתידיות.");
});

bot.onText(/\/generate/, (msg) => {
    const chatId = msg.chat.id;
    const predictions = generatePredictions(parsedResults);
    updateExcel(predictions);
    const predictionsTable = formatAsTable(predictions);
    bot.sendMessage(chatId, `נוצרו תחזיות חדשות:\n${predictionsTable}`);
});

