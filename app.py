import streamlit as st
import re

class ISLRuleEngine:
    def __init__(self):
        self.current_sport = None

    # 25+ Indian Sports
    SPORTS_LIST = [
        "ਕਬੱਡੀ", "ਫੁੱਟਬਾਲ", "ਕ੍ਰਿਕਟ", "ਹਾਕੀ", "ਖੋ-ਖੋ", "ਬਾਸਕਟਬਾਲ", "ਵਾਲੀਬਾਲ",
        "ਬੈਡਮਿੰਟਨ", "ਤੈਰਾਕੀ", "ਕੁਸ਼ਤੀ", "ਗੋਲਫ", "ਟੈਨਿਸ", "ਐਥਲੈਟਿਕਸ", "ਵੈਟਲਿਫਟਿੰਗ",
        "ਬਾਕਸਿੰਗ", "ਸ਼ੂਟਿੰਗ", "ਆਰਚਰੀ", "ਜੂਡੋ", "ਕਰਾਤੇ", "ਫੈਨਸਿੰਗ", "ਟੇਬਲ ਟੈਨਿਸ"
    ]

    # 25+ Adjectives
    QUALITY_WORDS = [
        "ਹਰਮਨ-ਪਿਆਰੀ", "ਮਸ਼ਹੂਰ", "ਬਹੁਤ ਪ੍ਰਸਿੱਧ", "ਲੋਕਪ੍ਰਿਯ", "ਪ੍ਰਚਲਿਤ", "ਵਧੀਆ",
        "ਸਭ ਤੋਂ ਵਧੀਆ", "ਰਾਸ਼ਟਰੀ", "ਊਰਜਾਵਾਨ", "ਸਖ਼ਤ", "ਤਾਕਤਵਰ", "ਜਨਪ੍ਰਿਯ",
        "ਵਿਸ਼ਵਵਿਆਪੀ", "ਪਰੰਪਰਾਗਤ", "ਆਧੁਨਿਕ", "ਉੱਨਤ", "ਪ੍ਰੇਰਣਾਦਾਇਕ", "ਵੀਰਤਾਪੂਰਨ"
    ]

    def extract_sport(self, sentence: str):
        for sport in self.SPORTS_LIST:
            if sport in sentence:
                return sport
        words = sentence.split()
        if words and len(words[0]) > 2 and words[0] not in ["ਇਹ", "ਪੂਰੇ", "ਏਸ਼ੀਆ", "ਭਾਰਤ"]:
            return words[0]
        return None

    def process(self, sentence: str) -> str:
        sentence = sentence.strip().replace('।', '').replace('?', '').strip()
        if not sentence:
            return ""

        detected = self.extract_sport(sentence)
        if detected:
            self.current_sport = detected

        if "ਮਨਪਸੰਦ ਖੇਡ ਹੈ" in sentence:
            sport = self.extract_sport(sentence) or self.current_sport or "ਕਬੱਡੀ"
            self.current_sport = sport
            return f"ਪੰਜਾਬੀ ਮਨਪਸੰਦ ਖੇਡ {sport}"

        elif "ਖੇਡ ਹੈ" in sentence:
            if not self.current_sport:
                return "Error: No sport detected. Please enter favourite sport sentence first."
            cleaned = sentence.replace("ਇਹ", "").replace("ਦੀ", "").replace("ਹੈ", "").strip()
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return f"{self.current_sport} {cleaned}"

        else:
            if not self.current_sport:
                self.current_sport = "ਕਬੱਡੀ"
            cleaned = re.sub(r'(ਇਸ ਤਰ੍ਹਾਂ|ਇਸ ਨੂੰ|ਉਂਞ|ਕਬੱਡੀ|ਖੇਡ|ਹੈ)', '', sentence)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return f"{self.current_sport} {cleaned}"


# ==================== STREAMLIT UI ====================
st.set_page_config(page_title="Punjabi to ISL", layout="centered")
st.title("🇮🇳 Punjabi to ISL Gloss Converter")
st.caption("Smart Context-Aware Rule Engine")

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

# Sidebar - More Examples using your two patterns
st.sidebar.header("Test Examples")
examples = [
    "ਕਬੱਡੀ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
    "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਹਰਮਨ-ਪਿਆਰੀ ਖੇਡ ਹੈ।",
    "ਫੁੱਟਬਾਲ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
    "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਬਹੁਤ ਪ੍ਰਸਿੱਧ ਖੇਡ ਹੈ।",
    "ਕ੍ਰਿਕਟ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
    "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਮਸ਼ਹੂਰ ਖੇਡ ਹੈ।",
    "ਹਾਕੀ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
    "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਲੋਕਪ੍ਰਿਯ ਖੇਡ ਹੈ।",
    "ਖੋ-ਖੋ ਪੰਜਾਬੀਆਂ ਦੀ ਮਨਪਸੰਦ ਖੇਡ ਹੈ।",
    "ਇਹ ਪੂਰੇ ਭਾਰਤ ਦੀ ਵਧੀਆ ਖੇਡ ਹੈ।"
]

for ex in examples:
    if st.sidebar.button(ex):
        st.session_state.input_text = ex
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Click any example to load into input box")