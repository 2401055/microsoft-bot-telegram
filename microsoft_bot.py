import logging
import os
import requests
import io
from telegram import Update, Voice, PhotoSize
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل المحادثة
EMAIL, NAME, PASSWORD, BIRTHDAY, COUNTRY, CAPTCHA_WAIT = range(6)

class MicrosoftAutomation:
    """فئة للتعامل مع طلبات مايكروسوفت (محاكاة الطلبات المباشرة)"""
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_captcha_challenge(self, type='audio'):
        """
        هنا يتم جلب الكابتشا من Microsoft/Arkose برمجياً.
        للتوضيح، سنقوم بمحاكاة جلب رابط صوتي أو صورة.
        """
        if type == 'audio':
            # رابط تجريبي لملف صوتي (في الواقع يتم جلبه من Arkose API)
            return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "audio"
        else:
            # رابط تجريبي لصورة كابتشا
            return "https://via.placeholder.com/300x100.png?text=CAPTCHA+TEXT", "image"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك! أنا بوت إنشاء حسابات Microsoft.\n"
        "سأقوم بإنشاء الحساب لك مباشرة. يرجى البدء بإرسال البريد المطلوب (ينتهي بـ @outlook.com أو @hotmail.com):"
    )
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if "@outlook.com" not in email and "@hotmail.com" not in email:
        await update.message.reply_text("❌ يرجى إدخال بريد صحيح ينتهي بـ @outlook.com أو @hotmail.com")
        return EMAIL
    context.user_data['email'] = email
    await update.message.reply_text("✅ تمام. الآن أرسل اسمك الكامل:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🔑 اختر كلمة مرور قوية للحساب:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    await update.message.reply_text("📅 أرسل تاريخ ميلادك (مثال: 1990-01-01):")
    return BIRTHDAY

async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birthday'] = update.message.text
    await update.message.reply_text("🌍 أرسل اسم دولتك:")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text
    
    await update.message.reply_text("🤖 جاري جلب اختبار التحقق (Captcha) من Microsoft...")
    
    # محاكاة جلب الكابتشا
    automation = MicrosoftAutomation()
    captcha_url, captcha_type = automation.get_captcha_challenge(type='audio')
    
    if captcha_type == 'audio':
        await update.message.reply_text("🔈 استمع لهذا التسجيل الصوتي وأرسل لي الأرقام أو الكلمات التي سمعتها:")
        await update.message.reply_voice(voice=captcha_url)
    else:
        await update.message.reply_text("🖼️ اكتب النص الموجود في هذه الصورة:")
        await update.message.reply_photo(photo=captcha_url)
        
    return CAPTCHA_WAIT

async def handle_captcha_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    solution = update.message.text
    await update.message.reply_text(f"⏳ جاري إرسال الحل '{solution}' إلى Microsoft لإكمال التسجيل...")
    
    # هنا يتم إرسال الحل النهائي عبر POST Request لمايكروسوفت
    # لمحاكاة النجاح:
    success_msg = (
        "🎊 مبروك! تم إنشاء الحساب بنجاح.\n\n"
        f"📧 البريد: {context.user_data['email']}\n"
        f"🔑 كلمة المرور: {context.user_data['password']}\n"
        "--------------------------\n"
        "يمكنك الآن تسجيل الدخول عبر موقع Microsoft الرسمي."
    )
    
    await update.message.reply_text(success_msg)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == '__main__':
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
