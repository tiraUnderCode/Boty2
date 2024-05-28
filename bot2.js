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

// دالة لتحليل النتائج ואגיד האנליזה
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

    for (let i = 0; i < 10; i++) {
        predictions.push(generateUniquePrediction());
    }
    return predictions;
}

// دالة لتحديث ملف الإكسل بالنتائج الجديدة
function updateExcel(predictions) {
    const newWorkbook = xlsx.readFile('results.xlsx');
    const newSheet = newWorkbook.Sheets[sheet_name_list[0]];

    // تحويل النتائج إلى صفوف جديدة
    const newRows = predictions.map(prediction => prediction.map(num => num.toString()));

    // إضافة الصفوف الجديدة إلى الشيت
    newRows.forEach(row => {
        xlsx.utils.sheet_add_aoa(newSheet, [row], { origin: -1 });
    });

    // كتابة التحديثات إلى ملف الإكسل
    xlsx.writeFile(newWorkbook, 'results.xlsx');
}

// أوامر البوت
bot.onText(/\/analyze/, (msg) => {
    const chatId = msg.chat.id;
    const analysis = analyzeResults(parsedResults);
    bot.sendMessage(chatId, `تحليل: ${JSON.stringify(analysis)}`);
});

bot.onText(/\/predict/, (msg) => {
    const chatId = msg.chat.id;
    const predictions = generatePredictions(parsedResults);
    updateExcel(predictions);
    bot.sendMessage(chatId, `التنبؤات التالية:\n${predictions.map(p => p.join(', ')).join('\n')}`);
});

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, "ברוך הבא! השתמש ב /analyze כדי לנתח תוצאות ו /predict כדי לחזות תוצאות עתידיות.");
});

bot.onText(/\/generate/, (msg) => {
    const chatId = msg.chat.id;
    const predictions = generatePredictions(parsedResults);
    updateExcel(predictions);
    bot.sendMessage(chatId, `נוצרו תחזיות חדשות:\n${predictions.map(p => p.join(', ')).join('\n')}`);
});
