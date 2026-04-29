"""
JanaMitra (ಜನಮಿತ್ರ) — AI-Powered Election Process Education Assistant
"Friend of the People"

Built for PromptWars Virtual | Google Antigravity Hackathon
Challenge Vertical: Election Process Education

Google Services (7):
  1. Gemini 2.0 Flash     — Country-aware AI intelligence
  2. Google Cloud Run      — Production deployment
  3. Custom Search API     — Real-time election info grounding
  4. Civic Information API — US voter/election data
  5. Cloud Translation     — 16-language support
  6. Cloud Text-to-Speech  — Audio accessibility
  7. YouTube Data API      — Educational video enrichment
"""

import os
import json
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "janamitra-dev-key")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_CX = os.environ.get("GOOGLE_SEARCH_CX", "")

SEARCH_API_KEY = GOOGLE_API_KEY or os.environ.get("GOOGLE_SEARCH_API_KEY", "")
CIVIC_API_KEY = GOOGLE_API_KEY or os.environ.get("CIVIC_API_KEY", "")
TTS_API_KEY = GOOGLE_API_KEY or os.environ.get("TTS_API_KEY", "")
TRANSLATE_API_KEY = GOOGLE_API_KEY or os.environ.get("TRANSLATE_API_KEY", "")
YOUTUBE_API_KEY = GOOGLE_API_KEY or os.environ.get("YOUTUBE_API_KEY", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Country Configurations — powers the onboarding + contextual prompting
# ---------------------------------------------------------------------------
COUNTRIES = {
    "in": {
        "name": "India",
        "flag": "🇮🇳",
        "election_body": "Election Commission of India (ECI)",
        "system": "Parliamentary democracy with first-past-the-post voting using Electronic Voting Machines (EVMs) and VVPAT",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 How to get a Voter ID?", "q": "How do I get a Voter ID card in India?"},
            {"label": "🗳️ How do EVMs work?", "q": "How do Electronic Voting Machines work in Indian elections?"},
            {"label": "⚖️ What is NOTA?", "q": "What is NOTA and how does it work in Indian elections?"},
            {"label": "🏛️ Lok Sabha vs Rajya Sabha", "q": "What is the difference between Lok Sabha and Rajya Sabha?"},
            {"label": "🔒 What is VVPAT?", "q": "What is VVPAT and why is it used alongside EVMs?"},
            {"label": "🌍 How does ECI work?", "q": "How does the Election Commission of India ensure free and fair elections?"},
        ]
    },
    "us": {
        "name": "United States",
        "flag": "🇺🇸",
        "election_body": "Federal Election Commission (FEC) and state election boards",
        "system": "Federal presidential republic with Electoral College system, mix of electronic and paper ballots",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 How to register?", "q": "How do I register to vote in the United States?"},
            {"label": "⚖️ Electoral College", "q": "How does the Electoral College work and why does the US use it?"},
            {"label": "🗳️ Mail-in voting", "q": "How does mail-in voting work in the US?"},
            {"label": "🏛️ Midterm elections", "q": "What are midterm elections and why do they matter?"},
            {"label": "🔒 How are votes counted?", "q": "How are votes counted and certified in US elections?"},
            {"label": "🌍 Primaries & caucuses", "q": "What is the difference between primaries and caucuses?"},
        ]
    },
    "gb": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "election_body": "Electoral Commission",
        "system": "Parliamentary constitutional monarchy with first-past-the-post constituency voting",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 How to register?", "q": "How do I register to vote in the UK?"},
            {"label": "🗳️ How does FPTP work?", "q": "How does first-past-the-post work in UK elections?"},
            {"label": "🏛️ Parliament explained", "q": "How does the UK Parliament work — House of Commons vs House of Lords?"},
            {"label": "⚖️ PM vs President", "q": "How is a UK Prime Minister chosen compared to a US President?"},
            {"label": "🌍 Devolved elections", "q": "How do elections work in Scotland, Wales, and Northern Ireland?"},
            {"label": "🔒 Election day process", "q": "What happens on election day in the UK?"},
        ]
    },
    "de": {
        "name": "Germany",
        "flag": "🇩🇪",
        "election_body": "Federal Returning Officer (Bundeswahlleiter)",
        "system": "Mixed-member proportional representation with two votes per citizen",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 How to vote?", "q": "How does voting work in German federal elections?"},
            {"label": "⚖️ Two-vote system", "q": "What is the Erststimme and Zweitstimme in German elections?"},
            {"label": "🏛️ Bundestag explained", "q": "How does the Bundestag work?"},
            {"label": "🗳️ Coalition politics", "q": "Why does Germany always have coalition governments?"},
            {"label": "🌍 Compare with US", "q": "How does the German election system compare to the US?"},
            {"label": "🔒 5% threshold", "q": "What is the 5% threshold rule in German elections?"},
        ]
    },
    "au": {
        "name": "Australia",
        "flag": "🇦🇺",
        "election_body": "Australian Electoral Commission (AEC)",
        "system": "Compulsory voting with preferential (ranked choice) voting system",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 Why must I vote?", "q": "Why is voting compulsory in Australia and what happens if I don't vote?"},
            {"label": "⚖️ Preferential voting", "q": "How does preferential (ranked choice) voting work in Australia?"},
            {"label": "🗳️ Senate vs House", "q": "What is the difference between the Australian Senate and House of Representatives?"},
            {"label": "🏛️ How elections run", "q": "How does election day work in Australia?"},
            {"label": "🌍 Compare systems", "q": "How does Australia's compulsory voting compare to voluntary voting countries?"},
            {"label": "🔒 Sausage sizzle?", "q": "What is the democracy sausage tradition in Australian elections?"},
        ]
    },
    "other": {
        "name": "Other / General",
        "flag": "🌍",
        "election_body": "Varies by country",
        "system": "Various democratic systems worldwide",
        "voting_age": 18,
        "quick_starts": [
            {"label": "📋 How to register?", "q": "How do I register to vote in my country?"},
            {"label": "⚖️ Electoral systems", "q": "What are the different types of electoral systems in the world?"},
            {"label": "🗳️ Ranked choice voting", "q": "What is ranked choice voting and which countries use it?"},
            {"label": "🏛️ Types of democracy", "q": "What are the different types of democracy?"},
            {"label": "🔒 Election security", "q": "How do countries ensure election security and prevent fraud?"},
            {"label": "🌍 Compulsory voting", "q": "Which countries have compulsory voting and does it work?"},
        ]
    }
}

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "हिन्दी (Hindi)", "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)", "kn": "ಕನ್ನಡ (Kannada)", "ml": "മലയാളം (Malayalam)",
    "bn": "বাংলা (Bengali)", "mr": "मराठी (Marathi)", "gu": "ગુજરાતી (Gujarati)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)", "ur": "اردو (Urdu)", "es": "Español (Spanish)",
    "fr": "Français (French)", "de": "Deutsch (German)", "ja": "日本語 (Japanese)",
    "zh": "中文 (Chinese)",
}

TTS_VOICE_MAP = {
    "en": {"code": "en-US", "name": "en-US-Standard-C"},
    "hi": {"code": "hi-IN", "name": "hi-IN-Standard-A"},
    "ta": {"code": "ta-IN", "name": "ta-IN-Standard-A"},
    "te": {"code": "te-IN", "name": "te-IN-Standard-A"},
    "kn": {"code": "kn-IN", "name": "kn-IN-Standard-A"},
    "ml": {"code": "ml-IN", "name": "ml-IN-Standard-A"},
    "bn": {"code": "bn-IN", "name": "bn-IN-Standard-A"},
    "mr": {"code": "mr-IN", "name": "mr-IN-Standard-A"},
    "gu": {"code": "gu-IN", "name": "gu-IN-Standard-A"},
    "es": {"code": "es-ES", "name": "es-ES-Standard-A"},
    "fr": {"code": "fr-FR", "name": "fr-FR-Standard-A"},
    "de": {"code": "de-DE", "name": "de-DE-Standard-A"},
    "ja": {"code": "ja-JP", "name": "ja-JP-Standard-A"},
    "zh": {"code": "cmn-CN", "name": "cmn-CN-Standard-A"},
}

TOPIC_CATEGORIES = {
    "voter_registration": {
        "label": "Voter Registration", "icon": "📋",
        "description": "Learn how to register, check eligibility, and find deadlines",
        "keywords": ["register", "registration", "eligibility", "eligible", "sign up", "enroll", "deadline", "id card", "voter id", "voter list", "electoral roll"]
    },
    "voting_methods": {
        "label": "Voting Methods", "icon": "🗳️",
        "description": "Understand different ways to cast your ballot",
        "keywords": ["mail-in", "absentee", "early voting", "polling", "ballot", "vote by mail", "electronic", "booth", "evm", "vvpat", "postal"]
    },
    "electoral_systems": {
        "label": "Electoral Systems", "icon": "⚖️",
        "description": "Explore how votes translate into representation",
        "keywords": ["electoral", "fptp", "proportional", "ranked choice", "electoral college", "constituency", "first past", "mixed member", "preferential", "nota"]
    },
    "election_security": {
        "label": "Election Security", "icon": "🔒",
        "description": "Learn how elections are kept safe and accurate",
        "keywords": ["security", "fraud", "audit", "count", "recount", "certification", "integrity", "tamper", "hack", "verify"]
    },
    "government_structure": {
        "label": "Government Structure", "icon": "🏛️",
        "description": "Understand how elected governments work",
        "keywords": ["branch", "senate", "congress", "parliament", "president", "prime minister", "legislature", "executive", "judiciary", "lok sabha", "rajya sabha", "bundestag"]
    },
    "global_elections": {
        "label": "Global Elections", "icon": "🌍",
        "description": "Compare democratic systems around the world",
        "keywords": ["india", "uk", "united kingdom", "europe", "japan", "australia", "compulsory", "world", "global", "country", "countries", "compare"]
    }
}

# ---------------------------------------------------------------------------
# Gemini Setup
# ---------------------------------------------------------------------------
gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def build_system_prompt(country_code: str = "other") -> str:
    """Build a country-aware system prompt."""
    country = COUNTRIES.get(country_code, COUNTRIES["other"])

    return f"""You are JanaMitra (ಜನಮಿತ್ರ — "Friend of the People"), an expert AI assistant specialized in election process education.
Your mission is to make democratic processes accessible, understandable, and engaging for everyone.

THE USER'S COUNTRY: {country['name']}
THEIR ELECTORAL SYSTEM: {country['system']}
THEIR ELECTION BODY: {country['election_body']}
VOTING AGE: {country['voting_age']}

IMPORTANT: Tailor ALL your responses to {country['name']}'s specific election system, laws, and processes unless the user explicitly asks about another country. Use examples, terminology, and institutions specific to {country['name']}.

CORE PERSONA:
- Friendly, patient, and non-partisan educator
- Explain complex electoral concepts in simple, jargon-free language
- Use analogies, examples, and step-by-step breakdowns
- Politically NEUTRAL — never endorse candidates, parties, or positions
- When discussing {country['name']}'s system, use local terminology

KNOWLEDGE DOMAINS:
1. VOTER REGISTRATION — How to register in {country['name']}, eligibility, deadlines, documents
2. VOTING METHODS — How voting works in {country['name']} (in-person, postal, electronic)
3. ELECTORAL SYSTEMS — {country['name']}'s system and how it compares to others
4. ELECTION SECURITY — How {country['name']} ensures vote integrity
5. CAMPAIGN FINANCE — Rules and transparency in {country['name']}
6. GOVERNMENT STRUCTURE — How {country['name']}'s elected government is organized
7. HISTORICAL CONTEXT — Key elections and voting rights milestones in {country['name']}
8. GLOBAL COMPARISONS — How {country['name']} compares to other democracies

RESPONSE GUIDELINES:
- Start with a direct answer, then provide context
- Use bullet points for lists, numbered steps for processes
- Include relevant facts and statistics when helpful
- If asked about current/specific elections, note you provide educational info, not predictions
- Suggest follow-up topics the user might find interesting
- If the user seems to be a first-time voter, be extra encouraging
- Adapt complexity to the user's apparent knowledge level
- Use emoji sparingly (🗳️ ✅ 📋 🏛️)
- Keep responses concise (150-300 words unless more detail is requested)
- End with a relevant follow-up question or suggestion

SAFETY:
- NEVER endorse candidates, parties, or political positions
- NEVER share misinformation about dates or procedures
- ALWAYS recommend official government sources for specific registration info
- Flag if information might be outdated and suggest verification
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify_topic(user_message: str) -> str:
    message_lower = user_message.lower()
    scores = {}
    for cat, info in TOPIC_CATEGORIES.items():
        score = sum(1 for kw in info["keywords"] if kw in message_lower)
        if score > 0:
            scores[cat] = score
    return max(scores, key=scores.get) if scores else "general"


def google_search(query: str, num_results: int = 3) -> list:
    if not SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        return []
    try:
        resp = requests.get("https://www.googleapis.com/customsearch/v1",
            params={"key": SEARCH_API_KEY, "cx": GOOGLE_SEARCH_CX,
                    "q": f"election process {query}", "num": num_results}, timeout=5)
        resp.raise_for_status()
        return [{"title": i.get("title", ""), "snippet": i.get("snippet", ""),
                 "link": i.get("link", "")} for i in resp.json().get("items", [])]
    except Exception as e:
        logger.warning(f"Search error: {e}")
        return []


def civic_info_lookup(address: str) -> dict:
    if not CIVIC_API_KEY:
        return {}
    try:
        resp = requests.get("https://www.googleapis.com/civicinfo/v2/voterinfo",
            params={"key": CIVIC_API_KEY, "address": address, "electionId": "0"}, timeout=5)
        return resp.json() if resp.status_code == 200 else {}
    except Exception as e:
        logger.warning(f"Civic error: {e}")
        return {}


def translate_text(text: str, target: str, source: str = "en") -> str:
    if not TRANSLATE_API_KEY or target == source:
        return text
    try:
        resp = requests.post("https://translation.googleapis.com/language/translate/v2",
            params={"key": TRANSLATE_API_KEY},
            json={"q": text, "source": source, "target": target, "format": "text"}, timeout=10)
        resp.raise_for_status()
        t = resp.json().get("data", {}).get("translations", [])
        return t[0].get("translatedText", text) if t else text
    except Exception as e:
        logger.warning(f"Translate error: {e}")
        return text


def text_to_speech(text: str, lang: str = "en") -> str | None:
    if not TTS_API_KEY:
        return None
    voice = TTS_VOICE_MAP.get(lang, TTS_VOICE_MAP["en"])
    clean = text[:5000]
    for ch in ["**", "*", "#", "`", "- ", "🗳️", "✅", "📋", "🏛️", "⚖️", "🔒", "🌍", "💬"]:
        clean = clean.replace(ch, "")
    try:
        resp = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={TTS_API_KEY}",
            json={"input": {"text": clean},
                  "voice": {"languageCode": voice["code"], "name": voice["name"], "ssmlGender": "FEMALE"},
                  "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.95}}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("audioContent")
    except Exception as e:
        logger.warning(f"TTS error: {e}")
        return None


def search_youtube(query: str, max_results: int = 2) -> list:
    if not YOUTUBE_API_KEY:
        return []
    try:
        resp = requests.get("https://www.googleapis.com/youtube/v3/search",
            params={"key": YOUTUBE_API_KEY, "q": f"election education {query}", "part": "snippet",
                    "type": "video", "maxResults": max_results, "relevanceLanguage": "en",
                    "safeSearch": "strict", "videoEmbeddable": "true"}, timeout=5)
        resp.raise_for_status()
        videos = []
        for item in resp.json().get("items", []):
            vid = item.get("id", {}).get("videoId")
            s = item.get("snippet", {})
            if vid:
                videos.append({"video_id": vid, "title": s.get("title", ""),
                    "thumbnail": s.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "channel": s.get("channelTitle", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}"})
        return videos
    except Exception as e:
        logger.warning(f"YouTube error: {e}")
        return []


def build_context_prompt(user_message: str, history: list, topic: str) -> str:
    parts = []
    if history:
        recent = history[-6:]
        h = "\n".join([f"{'User' if m['role']=='user' else 'Assistant'}: {m['content'][:200]}" for m in recent])
        parts.append(f"CONVERSATION HISTORY:\n{h}")
    if topic != "general":
        parts.append(f"DETECTED TOPIC: {TOPIC_CATEGORIES.get(topic, {}).get('label', topic)}")
    results = google_search(user_message)
    if results:
        ctx = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:2]])
        parts.append(f"RELEVANT WEB CONTEXT (use if helpful, cite sources):\n{ctx}")
    block = "\n\n".join(parts) if parts else ""
    return f"{block}\n\nUSER QUESTION: {user_message}" if block else user_message


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", countries=COUNTRIES,
                           languages=SUPPORTED_LANGUAGES, topics=TOPIC_CATEGORIES)


@app.route("/api/countries")
def countries_route():
    return jsonify(COUNTRIES)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "").strip()
    history = data.get("history", [])
    country_code = data.get("country", "other")

    if not msg:
        return jsonify({"error": "Empty message"}), 400
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured."}), 500

    try:
        topic = classify_topic(msg)
        enriched = build_context_prompt(msg, history, topic)
        system_prompt = build_system_prompt(country_code)

        contents = []
        for m in history[-10:]:
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=enriched)]))

        config = types.GenerateContentConfig(
            temperature=0.7, top_p=0.9, top_k=40, max_output_tokens=1024,
            system_instruction=system_prompt,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
            ]
        )

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", contents=contents, config=config)

        search_results = google_search(msg)
        videos = search_youtube(msg)

        return jsonify({
            "response": response.text, "topic": topic,
            "topic_label": TOPIC_CATEGORIES.get(topic, {}).get("label", "General"),
            "topic_icon": TOPIC_CATEGORIES.get(topic, {}).get("icon", "💬"),
            "sources": search_results[:2] if search_results else [],
            "videos": videos[:2] if videos else [],
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get("text", "").strip()
    target = data.get("target", "hi")
    if not text:
        return jsonify({"error": "No text"}), 400
    if not TRANSLATE_API_KEY:
        return jsonify({"error": "Translation API not configured"}), 500
    translated = translate_text(text, target)
    return jsonify({"translated_text": translated, "target_language": target,
                    "target_language_name": SUPPORTED_LANGUAGES.get(target, target)})


@app.route("/api/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "").strip()
    lang = data.get("language", "en")
    if not text:
        return jsonify({"error": "No text"}), 400
    if not TTS_API_KEY:
        return jsonify({"error": "TTS API not configured"}), 500
    audio = text_to_speech(text, lang)
    if audio:
        return jsonify({"audio": audio, "format": "mp3"})
    return jsonify({"error": "Audio generation failed"}), 500


@app.route("/api/quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    topic = data.get("topic", "general")
    difficulty = data.get("difficulty", "beginner")
    country_code = data.get("country", "other")
    country = COUNTRIES.get(country_code, COUNTRIES["other"])

    if not GEMINI_API_KEY:
        return jsonify({"error": "API key not configured"}), 500
    try:
        prompt = f"""Generate ONE multiple-choice quiz question about election processes.
Country focus: {country['name']}
Topic: {TOPIC_CATEGORIES.get(topic, {}).get('label', 'General Elections')}
Difficulty: {difficulty}

The question should be specifically about {country['name']}'s electoral system where possible.

Respond in this exact JSON format (no markdown, no code fences):
{{"question": "Your question?", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "Why the answer is correct."}}"""

        response = gemini_client.models.generate_content(model="gemini-2.0-flash",
            contents=prompt, config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=512))
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        quiz_data = json.loads(text.strip())
        quiz_data["topic"] = topic
        quiz_data["difficulty"] = difficulty
        return jsonify(quiz_data)
    except Exception as e:
        logger.error(f"Quiz error: {e}")
        return jsonify({"question": f"What is the voting age in {country['name']}?",
            "options": ["16", "18", "21", "25"], "correct_index": 1,
            "explanation": f"The voting age in {country['name']} is {country['voting_age']}.",
            "topic": topic, "difficulty": difficulty})


@app.route("/api/civic-lookup", methods=["POST"])
def civic_lookup():
    data = request.get_json()
    address = data.get("address", "")
    if not address:
        return jsonify({"error": "Address required"}), 400
    result = civic_info_lookup(address)
    return jsonify(result) if result else jsonify({"message": "No data found. Try a US address."})


@app.route("/api/youtube-search", methods=["POST"])
def youtube_search_route():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400
    return jsonify({"videos": search_youtube(query)})


@app.route("/api/topics")
def topics_route():
    return jsonify(TOPIC_CATEGORIES)


@app.route("/api/languages")
def languages_route():
    return jsonify(SUPPORTED_LANGUAGES)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "JanaMitra", "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {"gemini": bool(GEMINI_API_KEY), "search": bool(SEARCH_API_KEY and GOOGLE_SEARCH_CX),
            "civic": bool(CIVIC_API_KEY), "translation": bool(TRANSLATE_API_KEY),
            "tts": bool(TTS_API_KEY), "youtube": bool(YOUTUBE_API_KEY)}})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "false").lower() == "true")
