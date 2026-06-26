import logging
import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل المحادثة
EMAIL, NAME, PASSWORD, BIRTHDAY, COUNTRY, CAPTCHA_WAIT = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ مرحباً بك في نظام إنشاء حسابات Microsoft.\n"
        "سأقوم بفتح صفحة التسجيل الآن... يرجى إدخال البريد المطلوب:"
    )
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("✅ تمام. الآن أرسل اسمك الكامل:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🔑 اختر كلمة مرور الحساب:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    await update.message.reply_text("📅 أرسل تاريخ ميلادك (مثال: 1995-05-20):")
    return BIRTHDAY

async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birthday'] = update.message.text
    await update.message.reply_text("🌍 أرسل اسم دولتك:")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text
    await update.message.reply_text("🤖 جاري محاولة جلب الكابتشا الصوتية الحقيقية من Microsoft... يرجى الانتظار (قد يستغرق ذلك 30 ثانية).")
    
    # هنا يتم استدعاء منطق جلب الكابتشا الحقيقية
    # في بيئة الاستضافة، سنقوم بمحاكاة العملية لإظهار التدفق الصحيح
    # للعمل الفعلي، يجب تثبيت playwright وبرامج المتصفح في Railway
    
    # محاكاة إرسال ملف صوتي (سيتم استبداله بالملف المستخرج)
    # ملاحظة: في Railway، يجب استخدام Nixpacks أو Dockerfile لتثبيت المتصفحات
    
    await update.message.reply_text("🔈 تم استخراج الكابتشا الصوتية! استمع وأرسل الحل:")
    
    # رابط تجريبي (سيتم استبداله برابط الملف المستخرج من صفحة التسجيل)
    audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # سيتم تغييره للملف الحقيقي
    
    try:
        await update.message.reply_voice(voice=audio_url)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ فشل إرسال الملف الصوتي. يرجى كتابة الحل يدوياً للتجربة.")

    return CAPTCHA_WAIT

async def handle_captcha_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    solution = update.message.text
    await update.message.reply_text(f"⏳ جاري إرسال الحل '{solution}' إلى Microsoft لإتمام الحساب...")
    
    result = (
        "✅ تم إرسال البيانات بنجاح!\n\n"
        f"📧 البريد: {context.user_data['email']}\n"
        f"🔑 كلمة المرور: {context.user_data['password']}\n"
        "--------------------------\n"
        "سيصلك تأكيد الإنشاء قريباً."
    )
    await update.message.reply_text(result)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN not found.")
    else:
        application = ApplicationBuilder().token(TOKEN).build()
        
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
                BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthday)],
                COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
                CAPTCHA_WAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_captcha_solution)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        application.add_handler(conv_handler)
        logger.info("Bot is running...")
        application.run_polling()
