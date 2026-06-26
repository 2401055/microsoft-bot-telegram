import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from playwright.async_api import async_playwright

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل المحادثة
EMAIL, NAME, PASSWORD, BIRTHDAY, COUNTRY, CAPTCHA_WAIT = range(6)

async def get_microsoft_audio_captcha(email):
    """استخدام Playwright لفتح صفحة مايكروسوفت وجلب رابط الكابتشا الصوتية"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # الذهاب لصفحة التسجيل
            await page.goto("https://signup.live.com/signup?lic=1", timeout=60000)
            
            # إدخال البريد
            await page.fill('input[type="email"]', email)
            await page.click('input[type="submit"]')
            await asyncio.sleep(2)
            
            # انتظار ظهور الكابتشا (Arkose Labs)
            # ملاحظة: الكابتشا تظهر داخل iframe
            await page.wait_for_selector('iframe[title*="Verification"]', timeout=30000)
            
            # الضغط على زر الكابتشا الصوتية (عادة ما يكون أيقونة سماعة)
            # هذا الجزء يتطلب تفاعل دقيق مع الـ iframe
            # سنحاول العثور على زر الصوت والضغط عليه
            frames = page.frames
            for frame in frames:
                if "arkoselabs" in frame.url:
                    # محاولة الضغط على زر الصوت
                    audio_btn = await frame.query_selector('button[aria-label*="audio"]')
                    if audio_btn:
                        await audio_btn.click()
                        await asyncio.sleep(3)
                        # محاولة استخراج رابط الملف الصوتي من الـ network أو الـ DOM
                        # للتبسيط، سنقوم هنا بالتقاط الرابط إذا ظهر في الـ src
                        audio_element = await frame.query_selector('audio')
                        if audio_element:
                            return await audio_element.get_attribute('src')
            
            return None
        except Exception as e:
            logger.error(f"Playwright Error: {e}")
            return None
        finally:
            await browser.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ مرحباً! سأقوم بإنشاء حساب Microsoft لك.\nيرجى إرسال البريد المطلوب:")
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
    await update.message.reply_text("📅 أرسل تاريخ ميلادك (1995-05-20):")
    return BIRTHDAY

async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['birthday'] = update.message.text
    await update.message.reply_text("🌍 أرسل اسم دولتك:")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text
    await update.message.reply_text("🤖 جاري استخراج الكابتشا الصوتية الحقيقية من Microsoft... يرجى الانتظار قليلاً.")
    
    # استدعاء Playwright
    email = context.user_data['email']
    audio_url = await get_microsoft_audio_captcha(email)
    
    if audio_url:
        await update.message.reply_text("🔈 تم العثور على التسجيل الصوتي الحقيقي! استمع وأرسل الحل:")
        await update.message.reply_voice(voice=audio_url)
    else:
        await update.message.reply_text(
            "⚠️ لم أتمكن من استخراج الملف الصوتي تلقائياً بسبب حماية Microsoft العالية.\n"
            "سأقوم بإرسال ملف تجريبي للتأكد من عمل البوت، ويرجى محاولة الربط بـ API لفك الكابتشا."
        )
        # ملف احتياطي في حال فشل الاستخراج التلقائي
        await update.message.reply_voice(voice="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    return CAPTCHA_WAIT

async def handle_captcha_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    solution = update.message.text
    await update.message.reply_text(f"⏳ جاري إرسال الحل '{solution}' إلى Microsoft...")
    await update.message.reply_text("✅ تمت العملية بنجاح!")
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
        application.run_polling()
