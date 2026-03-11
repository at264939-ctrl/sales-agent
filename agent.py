"""Sales Agent: Process customer queries with Groq LLM fallback."""

import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq
from langsmith import traceable

load_dotenv()


class SalesAgent:
    """AI Sales Agent with Groq LLM for intelligent fallback suggestions."""

    def __init__(self, inventory_store):
        self.inventory = inventory_store
        self.llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"

    @traceable(name="process_query")
    def process_query(self, customer_message: str) -> str:
        """Process customer query and return response."""
        # Step 1: Semantic search in inventory
        results = self.inventory.search(customer_message, n_results=3)

        if results:
            # Found matching products
            return self._format_product_response(results, customer_message)

        # Step 2: No exact match - use Groq for intelligent fallback
        return self._suggest_alternatives(customer_message)

    def _format_product_response(self, products: list[dict], query: str) -> str:
        """Format found products into customer-friendly response."""
        if len(products) == 1:
            p = products[0]
            stock_msg = "متوفر" if int(p["stock"]) > 0 else "غير متوفر حالياً"
            return (
                f"✅ المنتج: {p['name']}\n"
                f"💰 السعر: ${p['price']}\n"
                f"📦 الحالة: {stock_msg}\n\n"
                f"هل تريد إتمام الطلب؟"
            )

        # Multiple products found
        response = f"🔍 وجدت {len(products)} منتجات مناسبة لطلبك:\n\n"
        for i, p in enumerate(products, 1):
            stock_msg = "✓" if int(p["stock"]) > 0 else "✗"
            response += f"{i}. {p['name']} - ${p['price']} [{stock_msg}]\n"
        response += "\nأي منتج تفضل؟"
        return response

    @traceable(name="suggest_alternatives")
    def _suggest_alternatives(self, query: str) -> str:
        """Use Groq LLM to suggest alternatives when no product matches."""
        # Get all products for context
        all_products = self.inventory.collection.get(include=["metadatas", "documents"])

        product_context = ""
        for i, meta in enumerate(all_products["metadatas"][0][:5], 1):
            product_context += f"{i}. {meta['name']} - {meta.get('description', 'N/A')}\n"

        prompt = f"""أنت وكيل مبيعات ذكي. العميل يبحث عن: "{query}"

المنتجات المتوفرة لدينا:
{product_context}

لم نجد منتج مطابق تماماً. اقترح أفضل بديل من المنتجات المتوفرة مع شرح السبب.
كن مختصراً ومفيداً. اكتب الرد بالعربية."""

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        suggestion = response.choices[0].message.content.strip()
        return f"🤖 لم نجد المنتج المطلوب، لكن نقترح:\n\n{suggestion}"
