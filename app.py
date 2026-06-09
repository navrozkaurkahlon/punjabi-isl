import re
import streamlit as st

class ISLRuleEngine:
    def __init__(self):
        self.current_sport = None

    SPORTS_LIST = [
        "ਕਬੱਡੀ", "ਫੁੱਟਬਾਲ", "ਕ੍ਰਿਕਟ", "ਹਾਕੀ", "ਖੋ-ਖੋ", "ਬਾਸਕਟਬਾਲ", "ਵਾਲੀਬਾਲ",
        "ਬੈਡਮਿੰਟਨ", "ਤੈਰਾਕੀ", "ਕੁਸ਼ਤੀ", "ਗੋਲਫ", "ਟੈਨਿਸ", "ਐਥਲੈਟਿਕਸ", "ਵੈਟਲਿਫਟਿੰਗ",
        "ਬਾਕਸਿੰਗ", "ਸ਼ੂਟਿੰਗ", "ਆਰਚਰੀ", "ਜੂਡੋ", "ਕਰਾਤੇ", "ਫੈਨਸਿੰਗ", "ਟੇਬਲ ਟੈਨਿਸ",
        "ਸਕੁਐਸ਼", "ਯੋਗਾ", "ਗਤਕਾ", "ਮਲਖੰਭ"
    ]

    COMMON_NAMES = [
        "ਰਾਮ", "ਬੁੱਧੂ", "ਸੁਖਵਿੰਦਰ", "ਅਮਨ", "ਪ੍ਰੀਤ", "ਹਰਪ੍ਰੀਤ", "ਗੁਰਪ੍ਰੀਤ", "ਦਾਦੀ", "ਨਾਨੀ",
        "ਹਰਜੀਤ", "ਬਲਜੀਤ", "ਰਵਿੰਦਰ", "ਜਸਪ੍ਰੀਤ", "ਕਿਰਨ", "ਸਿਮਰਨ", "ਅੰਮ੍ਰਿਤ", "ਗੁਰਜੀਤ",
        "ਮਨਪ੍ਰੀਤ", "ਬੀਬੀ", "ਚਾਚਾ", "ਤਾਇਆ", "ਮਾਸੀ", "ਭਰਾ", "ਭੈਣ", "ਪਿਤਾ", "ਮਾਤਾ",
        "ਸੋਨਮ", "ਵਿਕਰਮ", "ਅਜੈ", "ਰਾਜਿੰਦਰ", "ਸਤਵਿੰਦਰ", "ਕੁਲਵਿੰਦਰ", "ਇੰਦਰਜੀਤ", "ਪਰਮਜੀਤ",
        "ਜਸਵਿੰਦਰ", "ਗੁਰਮੀਤ", "ਬਲਵਿੰਦਰ", "ਰਾਣੀ", "ਰਾਜ", "ਅਭਿਨਵ", "ਨੀਲਮ", "ਪੂਜਾ", "ਪ੍ਰੀਤੀ"
    ]

    def process(self, sentence: str) -> str:
        sentence = sentence.strip().replace('।', '').replace('?', '').strip()
        if not sentence:
            return ""

        # Daily Routine has HIGHEST priority - completely isolated
        daily_keywords = ["ਸਵੇਰੇ", "ਰਾਤ", "ਸ਼ਾਮ", "ਹਰ ਰੋਜ਼", "ਸਾਰਾ ਦਿਨ"]
        if any(kw in sentence for kw in daily_keywords):
            return self.rule_daily_routine(sentence)

        # Sports logic only runs if not daily routine
        if any(sport in sentence for sport in self.SPORTS_LIST) or "ਖੇਡ ਹੈ" in sentence or "ਮਨਪਸੰਦ ਖੇਡ" in sentence:
            return self.rule_sports(sentence)

        return "No matching rule found."

    def rule_sports(self, sentence: str) -> str:
        detected = self.extract_sport(sentence)
        if detected:
            self.current_sport = detected

        if "ਖੇਡ ਹੈ" in sentence:
            sport = self.extract_sport(sentence) or self.current_sport or "ਕਬੱਡੀ"
            self.current_sport = sport
            cleaned = sentence
            if "ਇਹ" in cleaned:
                cleaned = cleaned.replace("ਇਹ", sport)
            cleaned = cleaned.replace("ਦੀ", "").replace("ਹੈ", "").strip()
            words = cleaned.split()
            stemmed = [self.stem_punjabi(w) for w in words]
            cleaned = " ".join(stemmed).strip()
            return f"{cleaned}".strip()
        else:
            if not self.current_sport:
                self.current_sport = "ਕਬੱਡੀ"
            cleaned = re.sub(r'(ਇਸ ਤਰ੍ਹਾਂ|ਇਸ ਨੂੰ|ਉਂਞ|ਕਬੱਡੀ|ਹੈ)', '', sentence)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return f"{self.current_sport} {cleaned}"

    # ==================== DAILY ROUTINE (Isolated) ====================
    def rule_daily_routine(self, sentence: str) -> str:
        sentence = sentence.strip()

        # Normalize time
        sentence = sentence.replace("ਸਾਰਾ ਦਿਨ", "ਸਾਰਾ-ਦਿਨ").replace("ਹਰ ਰੋਜ਼", "ਹਰ-ਰੋਜ਼")

        # Extract Time
        time_part = ""
        for t in ["ਸਵੇਰੇ", "ਰਾਤ", "ਸ਼ਾਮ", "ਸਾਰਾ-ਦਿਨ", "ਹਰ-ਰੋਜ਼"]:
            if t in sentence:
                time_part = t
                break
        if not time_part:
            time_part = "ਸਵੇਰੇ"

        # Remove time word
        cleaned = sentence
        for t in ["ਸਵੇਰੇ", "ਰਾਤ", "ਸ਼ਾਮ", "ਸਾਰਾ-ਦਿਨ", "ਹਰ-ਰੋਜ਼"]:
            cleaned = cleaned.replace(t, "")

        # Remove particles (including gender)
        cleaned = re.sub(r'ਦਾ ਹੈ|ਦੀ ਹੈ|ਦੇ ਹਨ|ਰਹਿੰਦਾ|ਰਹਿੰਦੀ|ਹੈ|ਨੂੰ', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Detect Subject
        subject = self.extract_subject(cleaned)
        if subject:
            cleaned = cleaned.replace(subject, "").strip()

        # Get original action
        action = cleaned.split()[-1] if cleaned.split() else "ਕੰਮ"

        # Strong verb stemming (male + female)
        stemmed_action = re.sub(r'ਉਂਦਾ|ਉਂਦੀ|ਆਉਂਦਾ|ਆਉਂਦੀ|ਇੰਦਾ|ਇੰਦੀ|ਦਾ|ਦੀ|ਣਾ|ਆਂਦਾ|ਆਂਦੀ|ਜਾਂਦਾ|ਜਾਂਦੀ|ਜਾਣਾ|ਜਾਂ|ਚਲਾਉਂਦਾ|ਚਲਾਉਂਦੀ|ਖਾਂਦਾ|ਖਾਂਦੀ|ਗਾਉਂਦਾ|ਗਾਉਂਦੀ', '', action)
        stemmed_action = stemmed_action.strip()

        # Special cases
        if "ਜਾ" in stemmed_action or stemmed_action == "":
            stemmed_action = "ਜਾ"
        if "ਚਲਾ" in stemmed_action:
            stemmed_action = "ਚਲਾ"
        if "ਵੇਖ" in stemmed_action:
            stemmed_action = "ਵੇਖ"
        if "ਖਾ" in action or "ਖਾਂ" in action:
            stemmed_action = "ਖਾ"
        if "ਗਾ" in action or "ਗਾਉਂ" in action:
            stemmed_action = "ਗਾ"

        # Remove original action
        if action:
            cleaned = cleaned.replace(action, "").strip()

        gloss = f"{time_part} {subject} {cleaned} {stemmed_action}++"
        gloss = re.sub(r'\s+', ' ', gloss).strip()
        return gloss

    def extract_subject(self, text: str) -> str:
        words = text.split()
        for word in words:
            if any(name in word for name in self.COMMON_NAMES):
                return word
            if len(word) >= 3:
                return word
        return "ਰਾਮ"

    def stem_punjabi(self, word: str) -> str:
        if word.endswith("ਪੰਜਾਬੀਆਂ"):
            return "ਪੰਜਾਬੀ"
        if word.endswith("ਆਂ") or word.endswith("ਾਂ"):
            return word[:-2]
        if word.endswith("ੀਆਂ"):
            return word[:-3] + "ੀ"
        return word

    def extract_sport(self, sentence: str):
        for sport in self.SPORTS_LIST:
            if sport in sentence:
                return sport
        words = sentence.split()
        if words and len(words[0]) > 2:
            return words[0]
        return None


# ===================== UI =====================
st.set_page_config(page_title="Punjabi to ISL", layout="centered")
st.title("🇮🇳 Punjabi to ISL Gloss Converter")
st.caption("Rule Engine - Sports + Daily Routine")

if 'engine' not in st.session_state:
    st.session_state.engine = ISLRuleEngine()

if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

engine = st.session_state.engine

sentence = st.text_area("Enter Punjabi Sentence:",
                        value=st.session_state.input_text,
                        height=150,
                        placeholder="ਇਥੇ ਲਿਖੋ...")

if st.button("Convert to ISL Gloss", type="primary"):
    if sentence.strip():
        result = engine.process(sentence)
        st.success("**ISL Gloss:**")
        st.write(f"**{result}**")

        if engine.current_sport:
            st.info(f"**Current Sport in Memory:** {engine.current_sport}")
    else:
        st.warning("Please enter a sentence.")

# ==================== SIDEBAR - BOTH CATEGORIES ====================
st.sidebar.header("🏏 Category 1: Sports")
with st.sidebar.expander("Example Sentences", expanded=True):
    for ex in [
        "ਕਬੱਡੀ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
        "ਫੁੱਟਬਾਲ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
        "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਹਰਮਨ-ਪਿਆਰੀ ਖੇਡ ਹੈ।"
    ]:
        if st.button(ex, key=f"s_{ex}"):
            st.session_state.input_text = ex
            st.rerun()

st.sidebar.header("🕒 Category 2: Daily Routine")
with st.sidebar.expander("Example Sentences (Male & Female)", expanded=True):
    for ex in [
        "ਰਾਮ ਹਰ ਰੋਜ਼ ਸਕੂਲ ਜਾਂਦਾ ਹੈ।",
        "ਹਰਪ੍ਰੀਤ ਹਰ ਰੋਜ਼ ਗੀਤ ਗਾਉਂਦਾ ਹੈ।",
        "ਹਰਪ੍ਰੀਤ ਹਰ ਰੋਜ਼ ਗੀਤ ਗਾਉਂਦੀ ਹੈ।",
        "ਸੁਖਵਿੰਦਰ ਰਾਤ ਨੂੰ ਟੀਵੀ ਵੇਖਦਾ ਹੈ।",
        "ਪ੍ਰੀਤੀ ਰਾਤ ਨੂੰ ਟੀਵੀ ਵੇਖਦੀ ਹੈ।",
        "ਬੁੱਧੂ ਸਵੇਰੇ ਯੋਗਾ ਕਰਦਾ ਹੈ।"
    ]:
        if st.button(ex, key=f"d_{ex}"):
            st.session_state.input_text = ex
            st.rerun()
