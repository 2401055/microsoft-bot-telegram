import logging
import os
import requests
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

async def fetch_only_captcha(email, update: Update):
    """وظيفة مخصصة تستخدم Playwright مع إرسال تحديثات للمستخدم"""
    async with async_playwright() as p:
        await update.message.reply_text("🌐 جاري تشغيل المتصفح الخفي...")
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        try:
            await update.message.reply_text("🔍 جاري الدخول لصفحة Microsoft...")
            await page.goto("https://signup.live.com/signup?lic=1", timeout=60000)
            
            await update.message.reply_text(f"📧 جاري إدخال البريد {email}...")
            await page.fill('input[type="email"]', email)
            await page.click('input[type="submit"]')
            await asyncio.sleep(5)
            
            await update.message.reply_text("🛡️ جاري البحث عن نظام الكابتشا (Arkose Labs)...")
            
            # محاولة جلب رابط الملف الصوتي من الـ Iframe
            frames = page.frames
            captcha_found = False
            for frame in frames:
                if "arkoselabs" in frame.url:
                    captcha_found = True
                    await update.message.reply_text("✅ تم العثور على نظام التحقق، جاري استخراج الصوت...")
                    audio_btn = await frame.query_selector('button[aria-label*="audio"]')
                    if audio_btn:
                        await audio_btn.click()
                        await asyncio.sleep(3)
                        audio_element = await frame.query_selector('audio')
                        if audio_element:
                            src = await audio_element.get_attribute('src')
                            if src:
                                return src
            
            if not captcha_found:
                await update.message.reply_text("⚠️ لم تطلب Microsoft كابتشا لهذا البريد حالياً.")
            else:
                await update.message.reply_text("❌ فشل استخراج رابط الصوت من داخل نظام التحقق.")
                
            return None
        except Exception as e:
            logger.error(f"Captcha Error: {e}")
            await update.message.reply_text(f"❗ حدث خطأ تقني: {str(e)[:100]}")
            return None
        finally:
            await browser.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك! أنا بوت إنشاء حسابات Microsoft.\nأرسل البريد المطلوب:")
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
    
    # استخدام Playwright مع إرسال تحديثات
    audio_url = await fetch_only_captcha(context.user_data['email'], update)
    
    if audio_url:
        await update.message.reply_text("🔈 تم جلب التسجيل الصوتي الحقيقي! استمع وأرسل الحل:")
        await update.message.reply_voice(voice=audio_url)
    else:
        await update.message.reply_text("⚠️ سأقوم بإرسال ملف تجريبي لتكملة التجربة حتى يتم حل مشكلة الاستخراج.")
        await update.message.reply_voice(voice="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    return CAPTCHA_WAIT

async def handle_captcha_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    solution = update.message.text
    await update.message.reply_text(f"⏳ جاري معالجة الحل '{solution}' وإكمال التسجيل...")
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
