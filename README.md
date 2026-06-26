# Microsoft Account Creator Telegram Bot

بوت تيليجرام يقوم بإنشاء حسابات Microsoft (Outlook/Hotmail) تلقائياً مع معالجة الكابتشا الصوتية.

## المميزات
- طلب بيانات المستخدم (البريد، الاسم، كلمة المرور، تاريخ الميلاد، الدولة).
- محاكاة عملية التسجيل في Microsoft.
- دعم الكابتشا الصوتية (Audio Captcha).

## الاستضافة على Railway
1. ارفع الكود على مستودع (Repository) في GitHub.
2. ادخل على [Railway.app](https://railway.app/).
3. قم بإنشاء مشروع جديد وربطه بمستودع GitHub.
4. سيتعرف Railway تلقائياً على ملف `Procfile` ويبدأ تشغيل البوت.

## المتطلبات
- `python-telegram-bot`
- `requests`
- `pyyaml`
- `pycryptodome`
