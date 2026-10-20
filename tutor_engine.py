"""
AI English Tutor Engine
Generates:
1. Natural conversational spoken dialogue in English
2. Real-time grammar & pronunciation analysis
3. Native phrasing alternatives (Casual & Professional)
4. Vocabulary & Idiom booster
"""

import json
import os
import re
import urllib.request
import urllib.error

SCENARIOS = [
    {
        "id": "job_interview",
        "category": "A. Business & Career",
        "icon": "💼",
        "title": "Job Interview (Tell Me About Yourself)",
        "desc": "ซ้อมตอบคำถามสัมภาษณ์งานคลาสสิก แนะนำตัว จุดแข็ง จุดอ่อน และการแก้ปัญหา",
        "greeting": "Hello and welcome to the interview! Thank you for taking the time to meet with us today. To start off, could you please tell me a little bit about yourself and your background?"
    },
    {
        "id": "business_pitch",
        "category": "A. Business & Career",
        "icon": "📊",
        "title": "Project Pitch & Presentation Q&A",
        "desc": "ซ้อมนำเสนอไอเดียโปรเจกต์ นโยบาย หรือผลิตภัณฑ์ต่อผู้บริหารและตอบข้อซักถาม",
        "greeting": "Hi! We're really excited to hear your proposal today. Whenever you're ready, please walk us through the core problem you're solving and how your solution stands out."
    },
    {
        "id": "client_negotiation",
        "category": "A. Business & Career",
        "icon": "🤝",
        "title": "Client Negotiation & Disagreement",
        "desc": "ฝึกการเจรจาต่อรอง การปฏิเสธหรือเห็นต่างอย่างสุภาพในบริบทธุรกิจ (Polite Disagreement)",
        "greeting": "Thanks for getting back to us. Looking at your contract proposal, we'd like to discuss the delivery timeline and pricing. We were hoping for a 15% discount for a two-year commitment. What are your thoughts?"
    },
    {
        "id": "cafe_ordering",
        "category": "B. Daily Life & Fluency",
        "icon": "☕",
        "title": "Coffee Shop & Casual Ordering",
        "desc": "ฝึกสั่งเครื่องดื่ม ปรับแต่งเมนู (Customization) และถามคำแนะนำจากบาริสต้า",
        "greeting": "Hi there! Welcome to The Daily Roast. What can I get started for you today?"
    },
    {
        "id": "airport_travel",
        "category": "B. Daily Life & Fluency",
        "icon": "✈️",
        "title": "Airport Check-in & Immigration",
        "desc": "จำลองการตอบคำถามเจ้าหน้าที่ ตม. และการเช็คอินสัมภาระที่สนามบินต่างประเทศ",
        "greeting": "Good morning. May I see your passport and boarding pass, please? What is the primary purpose of your visit, and how long do you plan to stay?"
    },
    {
        "id": "casual_small_talk",
        "category": "B. Daily Life & Fluency",
        "icon": "🌤️",
        "title": "Casual Weekend Small Talk",
        "desc": "ฝึกการเริ่มบทสนทนาแบบเป็นกันเอง คุยเรื่องงานอดิเรก ดินฟ้าอากาศ และภาพยนตร์",
        "greeting": "Hey there! It's so good to see you. How has your week been going so far? Did you get up to anything fun over the weekend?"
    },
    {
        "id": "grammar_freetalk",
        "category": "C. Grammar Lab & Free Talk",
        "icon": "🎯",
        "title": "Free Talk & Real-time Grammar Lab",
        "desc": "คุยเรื่องอะไรก็ได้ตามใจคุณอย่างอิสระ พร้อมระบบตรวจจับแกรมม่าและเกลาภาษาแบบเรียลไทม์",
        "greeting": "Hello! I'm your English speaking coach. You can talk about anything you like—your day, your hobbies, or tech news. Whenever you speak, I'll keep the conversation going and help polish your grammar. What's on your mind today?"
    }
]

SYSTEM_PROMPT = """You are "Alex", a friendly, charismatic, and highly encouraging Native English Speaking Coach.
Your goal is to help ESL students build speaking confidence, master natural conversational rhythm, and eliminate grammar mistakes.

Your task for every student message:
1. Respond to the student naturally and warmly in English (keep your conversational reply between 2-4 sentences, encouraging them to keep talking).
2. Analyze the student's English input for:
   - Grammatical errors (tenses, subject-verb agreement, prepositions, articles).
   - Awkward or literal translations (Konglish/Tinglish phrasing).
3. Provide constructive, friendly feedback in Thai & English so the student learns immediately.

OUTPUT FORMAT:
You MUST ALWAYS respond with a strict JSON object with these exact keys:
{
  "reply": "Your natural conversational response in English to continue the dialogue",
  "feedback": {
    "has_error": true/false,
    "original": "The student's exact phrase or sentence",
    "corrected": "The corrected version in natural English",
    "explanation_th": "คำอธิบายภาษาไทยสั้นๆ กระชับเข้าใจง่ายว่าทำไมถึงแก้ และหลักการใช้คืออะไร",
    "native_alternatives": [
      "Option 1: A casual native way to say this",
      "Option 2: A more professional/formal way to say this"
    ],
    "vocab_booster": [
      {"word": "idiom or phrasal verb", "meaning_th": "ความหมายภาษาไทย", "example": "Short example sentence"}
    ]
  }
}
Do NOT wrap the output in markdown codeblocks like ```json. Return ONLY valid JSON.
"""

def extract_json(raw: str) -> dict:
    clean = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    clean = re.sub(r"\s*```$", "", clean)
    try:
        return json.loads(clean)
    except Exception:
        # Fallback regex extraction
        m = re.search(r"\{.*\}", clean, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None


def call_gemini_tutor(api_key: str, messages: list[dict]) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    contents = []
    for m in messages:
        role = "user" if m["role"] in ["user", "student"] else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json",
            "maxOutputTokens": 600
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = extract_json(text)
        if parsed:
            return parsed
    raise RuntimeError("Failed to parse Gemini tutor JSON response")


def call_openai_tutor(api_key: str, messages: list[dict]) -> dict:
    url = "https://api.openai.com/v1/chat/completions"
    formatted = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        role = "user" if m["role"] in ["user", "student"] else "assistant"
        formatted.append({"role": role, "content": m["content"]})

    payload = {
        "model": "gpt-4o-mini",
        "messages": formatted,
        "temperature": 0.5,
        "response_format": {"type": "json_object"},
        "max_tokens": 600
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"]
        parsed = extract_json(text)
        if parsed:
            return parsed
    raise RuntimeError("Failed to parse OpenAI tutor JSON response")


# Built-in ESL Rule Engine (Zero-dependency Fallback)
COMMON_ESL_FIXES = [
    (r"\bi am agree\b", "I agree", "ภาษาอังกฤษคำว่า 'agree' เป็นคำกริยา (verb) อยู่แล้ว ไม่ต้องใส่ verb to be ('am') ข้างหน้า ใช้ 'I agree' ได้เลยครับ"),
    (r"\bi have (\d+) years old\b", r"I am \1 years old", "การบอกอายุในภาษาอังกฤษใช้ 'I am ... years old' ไม่ใช้คำว่า 'have' เหมือนบางภาษาครับ"),
    (r"\bmore better\b", "much better / way better", "คำว่า 'better' เป็นขั้นกว่าของ good อยู่แล้ว ห้ามซ้อน 'more' เข้าไป ให้ใช้ 'much better' แทนครับ"),
    (r"\bexplain me\b", "explain to me", "คำกริยา 'explain' ต้องตามด้วย 'to someone' เช่น 'explain this to me' ครับ"),
    (r"\bi am graduate from\b", "I graduated from", "การจบการศึกษาเป็นเหตุการณ์ในอดีต ใช้ past tense 'I graduated from' ครับ"),
    (r"\bvery like\b", "really like / like ... very much", "ในภาษาอังกฤษไม่วาง 'very' ไว้หน้าคำกริยา ให้ใช้ 'I really like' หรือ 'I like it very much' ครับ"),
    (r"\bhe go\b", "he goes", "ประธานเอกพจน์บุรุษที่ 3 (He/She/It) ใน Present Simple กริยาต้องเติม -s หรือ -es ครับ"),
    (r"\bshe go\b", "she goes", "ประธานเอกพจน์บุรุษที่ 3 (He/She/It) ใน Present Simple กริยาต้องเติม -s หรือ -es ครับ"),
    (r"\byesterday i go\b", "yesterday I went", "มีคำว่า 'yesterday' บอกเวลาในอดีต ต้องเปลี่ยนรูปเป็น Past Simple กริยาช่อง 2 คือ 'went' ครับ"),
    (r"\bi didn't went\b", "I didn't go", "หลังกริยาช่วย 'didn't' ต้องตามด้วยกริยารูป infinitive (ช่อง 1) เสมอครับ"),
]

def rule_based_grammar_check(text: str) -> dict:
    t_lower = text.lower()
    for pattern, replacement, explanation in COMMON_ESL_FIXES:
        if re.search(pattern, t_lower):
            corrected = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            return {
                "has_error": True,
                "original": text,
                "corrected": corrected,
                "explanation_th": explanation,
                "native_alternatives": [
                    f"Naturally: \"{corrected}\"",
                    "Native polish: Try expressing it with more details or idioms"
                ],
                "vocab_booster": [
                    {"word": "hands down", "meaning_th": "อย่างไม่ต้องสงสัย / แน่นอนที่สุด", "example": "That was hands down the best coffee I've had."}
                ]
            }

    # If no obvious mistake spotted in basic rules
    return {
        "has_error": False,
        "original": text,
        "corrected": text,
        "explanation_th": "ประโยคนี้ใช้ไวยากรณ์ได้ถูกต้องและสื่อความหมายได้ชัดเจนดีมากครับ!",
        "native_alternatives": [
            f"Casual: \"To be honest, {text.lower()}\"",
            f"Polished: \"From my perspective, {text.lower()}\""
        ],
        "vocab_booster": [
            {"word": "hit the spot", "meaning_th": "ถูกใจมาก / ถึงใจ (อาหาร/เครื่องดื่ม)", "example": "That cold drink really hit the spot on a hot day."}
        ]
    }


def generate_tutor_response(user_speech: str, history: list[dict], scenario_id: str = "grammar_freetalk", gemini_key: str = "", openai_key: str = "") -> dict:
    # 1. Try Gemini
    g_key = gemini_key or os.environ.get("GEMINI_API_KEY", "")
    if g_key:
        try:
            return call_gemini_tutor(g_key, history + [{"role": "student", "content": user_speech}])
        except Exception as e:
            print(f"[Gemini Tutor Exception]: {e}")

    # 2. Try OpenAI
    o_key = openai_key or os.environ.get("OPENAI_API_KEY", "")
    if o_key:
        try:
            return call_openai_tutor(o_key, history + [{"role": "student", "content": user_speech}])
        except Exception as e:
            print(f"[OpenAI Tutor Exception]: {e}")

    # 3. Rule-based Fallback
    grammar_res = rule_based_grammar_check(user_speech)
    
    # Contextual reply templates
    text_l = user_speech.lower()
    if any(k in text_l for k in ["hello", "hi", "how are you", "good morning"]):
        reply = "Hello! It's fantastic to connect with you. I'm doing well, thanks for asking! What would you like to talk about today?"
    elif any(k in text_l for k in ["coffee", "latte", "cappuccino", "order"]):
        reply = "Great choice! We have oat milk, almond milk, and whole milk. Would you like that hot or iced, and what size can I get for you?"
    elif any(k in text_l for k in ["job", "interview", "experience", "work"]):
        reply = "That's an impressive background! Could you share a specific challenge you faced in your previous role and how you handled it?"
    elif any(k in text_l for k in ["weekend", "movie", "travel", "hobby"]):
        reply = "That sounds so relaxing! How long have you been interested in that, and do you usually get much free time during the week?"
    else:
        reply = f"That's really interesting! You mentioned '{user_speech[:35]}...'. Could you tell me a little more about your perspective on that?"

    return {
        "reply": reply,
        "feedback": grammar_res
    }
