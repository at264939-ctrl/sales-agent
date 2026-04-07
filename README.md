# Sales Agent - وكيل مبيعات ذكي

نظام ذكي للرد على استفسارات العملاء عبر WhatsApp باستخدام البحث الدلالي والاقتراحات الذكية.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Message Journey                                   │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Customer   │
    │  (WhatsApp)  │
    └──────┬───────┘
           │ 1. sends query
           ▼
    ┌──────────────────────────┐
    │   Twilio WhatsApp API    │
    │   (Webhook Gateway)      │
    └──────┬───────────────────┘
           │ 2. POST /webhook/whatsapp
           ▼
    ┌──────────────────────────┐
    │   Flask Server           │
    │   (server.py)            │
    └──────┬───────────────────┘
           │ 3. process_query()
           ▼
    ┌──────────────────────────────────────┐
    │         Sales Agent                  │
    │         (agent.py)                   │
    └──────┬───────────────────────────────┘
           │
           ├─────────────────────────┐
           │ 4a. search(query)       │ 4b. No match found
           ▼                         ▼
    ┌──────────────────┐    ┌─────────────────────┐
    │   ChromaDB       │    │   Groq LLM          │
    │   (Vector Store) │    │   (Fallback)        │
    │                  │    │                     │
    │ • Semantic search│    │ • Analyze query     │
    │ • Product match  │    │ • Suggest closest   │
    └──────┬───────────┘    │   alternative       │
           │                └──────────┬──────────┘
           │ 5. Found products          │ 5. Suggestion
           └──────────────┬────────────┘
                          ▼
    ┌──────────────────────────────────────┐
    │         Format Response              │
    │         (Arabic)                     │
    └──────┬───────────────────────────────┘
           │ 6. Send via Twilio
           ▼
    ┌──────────────┐
    │   Customer   │
    │  (Receives)  │
    └──────────────┘


    ┌──────────────────────────────────────┐
    │         LangSmith                    │
    │         (Monitoring)                 │
    │         • Trace all queries          │
    │         • Monitor costs              │
    │         • Quality tracking           │
    └──────────────────────────────────────┘
```

## Features

- ✅ **Semantic Search**: بحث ذكي في منتجات المخزن باستخدام ChromaDB
- ✅ **Groq Fallback**: اقتراح بدائل ذكية عند عدم وجود منتج مطابق
- ✅ **WhatsApp Integration**: استقبال وإرسال عبر Twilio WhatsApp API
- ✅ **LangSmith Monitoring**: تتبع جودة الردود والتكلفة
- ✅ **Clean Code**: بنية بسيطة وواضحة

## Quick Start

```bash
# 1. Clone and setup
chmod +x run.sh
./run.sh

# 2. Edit .env with your API keys
# - GROQ_API_KEY (from https://console.groq.com)
# - LANGCHAIN_API_KEY (from https://smith.langchain.com)
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN (from https://twilio.com)

# 3. Run again
./run.sh
```

## File Structure

```
Sales-Agent/
├── server.py          # Flask server + Twilio webhook
├── agent.py           # Sales Agent logic + Groq LLM
├── inventory.py       # CSV loader + ChromaDB store
├── products.csv       # Sample product data
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── run.sh             # Startup script
└── README.md          # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/whatsapp` | POST | Receive WhatsApp messages |
| `/health` | GET | Health check |

## Twilio Configuration

1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Set webhook URL to: `https://your-server.com/webhook/whatsapp`
3. Send WhatsApp message to: `whatsapp:+14155238886`

## LangSmith Tracing

All queries are automatically traced. View traces at:
https://smith.langchain.com/projects/sales-agent

## Example Flow

**Customer**: "أبحث عن سماعة لاسلكية بعزل ضوضاء"

**Agent** (if found):
```
✅ المنتج: Sony WH-1000XM5
💰 السعر: $349.99
📦 الحالة: متوفر

هل تريد إتمام الطلب؟
```

**Agent** (if not found - Groq fallback):
```
🤖 لم نجد المنتج المطلوب، لكن نقترح:

نوصي بـ Bose QuietComfort 45 - سماعة لاسلكية
بعزل ضوضاء ممتازة وسعر $329.99. بديل ممتاز
بنفس المواصفات المطلوبة



## License

MIT
---

## Support me☕

If you find this project helpful and would like to support its development, you can buy me a coffee via PayPal. Your support is greatly appreciated!

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/ncp/payment/FYTDX2XYNGAJ8)

---
