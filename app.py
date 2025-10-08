import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import re
from deep_translator import GoogleTranslator
from openai import OpenAI
import json
import os


st.set_page_config(page_title="INGRES AI Assistant", page_icon="💧", layout="wide")


# ============= OPENAI CLIENT SETUP =============
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        st.error("⚠️ OPENROUTER_API_KEY not found. Please set it in .streamlit/secrets.toml or environment variables.")
        st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# ============= CSS STYLING =============
st.markdown("""<style>
.stApp{background:linear-gradient(135deg,#2d3561 0%,#3d2d4f 100%)}
.main .block-container{padding:2rem;background:#fff;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,.25);max-width:1200px}
[data-testid="stChatMessage"]{background:#f8f9fa;border-radius:15px;padding:1.2rem;margin:.5rem 0;box-shadow:0 2px 8px rgba(0,0,0,.1);border:1px solid #e0e0e0}
[data-testid="stChatMessageContent"]{color:#1a1a1a !important;font-size:1rem;line-height:1.6}
[data-testid="stChatMessageContent"] *{color:#1a1a1a !important}
[data-testid="stChatInput"]{border-radius:25px;border:2px solid #2d3561;background:#fff}
[data-testid="stChatInput"] textarea{color:#1a1a1a !important;background:#fff !important;font-size:1rem !important}
[data-testid="stChatInput"] input{color:#1a1a1a !important;background:#fff !important}
[data-testid="stSidebar"]{background:#f5f7fa;border-right:2px solid #d0d0d0}
.stButton button{border-radius:20px;border:none;background:#2d3561;color:#fff;font-weight:600;padding:.6rem 1.2rem;transition:all .3s ease;box-shadow:0 3px 8px rgba(45,53,97,.3)}
.stButton button:hover{background:#1f2643;transform:translateY(-2px);box-shadow:0 5px 15px rgba(45,53,97,.5)}
[data-testid="stMetricValue"]{font-size:1.6rem;color:#1a1a1a;font-weight:700}
[data-testid="stMetricLabel"]{color:#424242;font-weight:600}
.stInfo{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1976d2;padding:1rem}
h1,h2,h3,h4,h5,h6{color:#1a1a1a!important;font-weight:700}
.stMarkdown{color:#1a1a1a !important}
</style>""", unsafe_allow_html=True)


# ============= LANGUAGE CONFIG =============
LANGS = {
    'en': {'name': 'English', 'flag': '🇬🇧'},
    'hi': {'name': 'हिन्दी (Hindi)', 'flag': '🇮🇳'},
    'ta': {'name': 'தமிழ் (Tamil)', 'flag': '🇮🇳'},
    'te': {'name': 'తెలుగు (Telugu)', 'flag': '🇮🇳'},
    'kn': {'name': 'ಕನ್ನಡ (Kannada)', 'flag': '🇮🇳'},
    'ml': {'name': 'മലയാളം (Malayalam)', 'flag': '🇮🇳'},
    'mr': {'name': 'मराठी (Marathi)', 'flag': '🇮🇳'},
    'gu': {'name': 'ગુજરાતી (Gujarati)', 'flag': '🇮🇳'},
    'bn': {'name': 'বাংলা (Bengali)', 'flag': '🇮🇳'},
    'pa': {'name': 'ਪੰਜਾਬੀ (Punjabi)', 'flag': '🇮🇳'},
    'or': {'name': 'ଓଡ଼ିଆ (Odia)', 'flag': '🇮🇳'},
    'ur': {'name': 'اردو (Urdu)', 'flag': '🇮🇳'}
}

TRANS = {
    'title': {'en': '💧 INGRES Virtual Assistant', 'hi': '💧 इंग्रेस वर्चुअल सहायक'},
    'subtitle': {'en': '🤖 Smart AI Assistant - Ask me anything about groundwater data!', 
                 'hi': '🤖 स्मार्ट एआई सहायक - भूजल डेटा के बारे में मुझसे कुछ भी पूछें!'},
    'input': {'en': 'Ask me anything...', 'hi': 'मुझसे कुछ भी पूछें...'},
    'greeting': {'en': "Hello! 👋 I'm your INGRES AI assistant. Ask me about groundwater data!",
                 'hi': "नमस्ते! 👋 मैं आपका INGRES AI सहायक हूँ। मुझसे भूजल डेटा के बारे में पूछें!"}
}


# ============= SESSION STATE INITIALIZATION =============
for k in ['language', 'messages', 'data_cards', 'context_memory']:
    if k not in st.session_state:
        if k == 'language':
            st.session_state[k] = 'en'
        elif k == 'data_cards':
            st.session_state[k] = {}
        elif k == 'messages':
            st.session_state[k] = []
        elif k == 'context_memory':
            st.session_state[k] = {
                'last_district': None,
                'last_year': None,
                'recent_districts': [],
                'recent_years': []
            }


# ============= DATA LOADING WITH ERROR HANDLING =============
@st.cache_data
def load_data():
    try:
        return pd.read_csv('sample_data.csv')
    except FileNotFoundError:
        st.error("❌ Error: sample_data.csv not found. Please upload the data file to the root directory.")
        st.info("📝 The CSV should have columns: District, Year, Groundwater_Level_m, Recharge_BCM, Extraction_BCM, Category")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()


df = load_data()


# ============= TRANSLATION FUNCTIONS =============
@st.cache_data(ttl=3600)
def tr(t, l, s='en'):
    """Translate text with caching and error handling"""
    if not t:
        return t
    if l == 'en' or l == s:
        return t
    try:
        return GoogleTranslator(source=s, target=l).translate(str(t))
    except Exception as e:
        st.warning(f"⚠️ Translation error: {str(e)}")
        return t


def gt(k, l='en'):
    """Get translated text from TRANS dictionary"""
    return TRANS.get(k, {}).get(l, TRANS.get(k, {}).get('en', ''))


# ============= CONTEXT TRACKING =============
def update_context(district=None, year=None):
    """Update conversation context memory"""
    memory = st.session_state.context_memory

    if district:
        memory['last_district'] = district
        if district not in memory['recent_districts']:
            memory['recent_districts'].insert(0, district)
            memory['recent_districts'] = memory['recent_districts'][:5]

    if year:
        memory['last_year'] = year
        if year not in memory['recent_years']:
            memory['recent_years'].insert(0, year)
            memory['recent_years'] = memory['recent_years'][:5]


def get_context():
    """Get current context"""
    return st.session_state.context_memory


# ============= YEAR NORMALIZATION =============
def normalize_year(year_input):
    """Normalize year: 23 -> 2023, 2023 -> 2023"""
    if not year_input:
        return None

    year_str = str(year_input).strip().strip("'\"")

    if len(year_str) == 4 and year_str.isdigit():
        year_int = int(year_str)
        if 2000 <= year_int <= 2030:
            return year_str
    elif len(year_str) == 2 and year_str.isdigit():
        return str(2000 + int(year_str))
    elif len(year_str) == 1 and year_str.isdigit():
        return f"200{year_str}"

    return None


def extract_years(text):
    """Extract and normalize all years from text"""
    years = []

    # 4-digit years (2000-2030)
    four_digit = re.findall(r'\b(20[0-2][0-9])\b', text)
    years.extend(four_digit)

    # 2-digit years with apostrophe or standalone
    two_digit = re.findall(r"'(\d{2})\b|\b(\d{2})(?=\s*(?:to|vs|and|-|,|\s|$))", text)
    for match in two_digit:
        digit = match[0] or match[1]
        if digit and int(digit) <= 99:
            normalized = normalize_year(digit)
            if normalized and normalized not in years:
                years.append(normalized)

    return years


def extract_districts(text):
    """Extract district names from text using fuzzy matching"""
    all_districts = df['District'].unique().tolist()
    found_districts = []

    # Check exact matches first (case-insensitive)
    for district in all_districts:
        if district.lower() in text.lower():
            found_districts.append(district)

    # Fuzzy matching for remaining words (increased threshold to 75)
    if not found_districts:
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 3:  # Only match words with 4+ characters
                match = process.extractOne(word, all_districts, scorer=fuzz.ratio)
                if match and match[1] >= 75 and match[0] not in found_districts:
                    found_districts.append(match[0])

    return found_districts


# ============= DATABASE FUNCTIONS =============
def get_database_schema():
    """Get database schema info"""
    return {
        "districts": df['District'].unique().tolist(),
        "years": sorted(df['Year'].unique().tolist()),
        "columns": df.columns.tolist()
    }


def query_data(district=None, year=None, districts=None, years=None):
    """Query database with proper parameter handling"""
    try:
        # Normalize years
        if year:
            year = normalize_year(year)
        if years:
            years = [normalize_year(y) for y in years if normalize_year(y)]

        # Update context
        if district:
            update_context(district=district, year=year)
        if districts:
            for d in districts:
                update_context(district=d)

        # Single district, single year
        if district and year and not districts and not years:
            result = df[(df['District'].str.lower() == district.lower()) & 
                       (df['Year'].astype(str) == str(year))]
            if not result.empty:
                return True, result.iloc[0].to_dict()
            return False, f"No data for {district} in {year}"

        # Single district, multiple years (time series)
        if district and years and not districts:
            results = []
            for y in years:
                r = df[(df['District'].str.lower() == district.lower()) & 
                      (df['Year'].astype(str) == str(y))]
                if not r.empty:
                    results.append(r.iloc[0].to_dict())
            if results:
                return True, {'type': 'time_series', 'data': results}
            return False, f"No data for {district}"

        # Multiple districts, single year (spatial comparison)
        if districts and year and not years:
            results = []
            for d in districts:
                r = df[(df['District'].str.lower() == d.lower()) & 
                      (df['Year'].astype(str) == str(year))]
                if not r.empty:
                    results.append(r.iloc[0].to_dict())
            if results:
                return True, {'type': 'district_comparison', 'data': results, 'year': year}
            return False, f"No data for year {year}"

        # Multiple districts, multiple years
        if districts and years:
            results = []
            for d in districts:
                for y in years:
                    r = df[(df['District'].str.lower() == d.lower()) & 
                          (df['Year'].astype(str) == str(y))]
                    if not r.empty:
                        results.append(r.iloc[0].to_dict())
            if results:
                return True, {'type': 'matrix', 'data': results}
            return False, "No data found"

        # Only district - ask for year
        if district and not year and not years:
            available_years = df[df['District'].str.lower() == district.lower()]['Year'].unique().tolist()
            if available_years:
                return False, {
                    'type': 'need_year',
                    'district': district,
                    'available_years': sorted([str(y) for y in available_years])
                }
            return False, f"District '{district}' not found"

        # Only year - ask for district
        if year and not district and not districts:
            available = df[df['Year'].astype(str) == str(year)]['District'].unique().tolist()
            if available:
                return False, {
                    'type': 'need_district',
                    'year': year,
                    'available_districts': available[:10]
                }
            return False, f"No data for {year}"

        return False, "Invalid query"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ============= AI RESPONSE WITH ERROR HANDLING =============
def get_ai_response(user_query, language='en'):
    """Enhanced AI with better error handling"""
    schema = get_database_schema()
    context = get_context()

    # Extract entities from query
    extracted_districts = extract_districts(user_query)
    extracted_years = extract_years(user_query)

    system_prompt = f"""You are INGRES AI Assistant - expert on Indian groundwater data.

**DATABASE**:
- Districts: {', '.join(schema['districts'][:20])}... (total {len(schema['districts'])})
- Years: {', '.join(map(str, schema['years']))}

**CONTEXT MEMORY**:
- Last District: {context['last_district'] or 'None'}
- Last Year: {context['last_year'] or 'None'}
- Recent: {', '.join(context['recent_districts'][:3]) if context['recent_districts'] else 'None'}

**EXTRACTED FROM CURRENT QUERY**:
- Districts detected: {', '.join(extracted_districts) if extracted_districts else 'None'}
- Years detected: {', '.join(extracted_years) if extracted_years else 'None'}

**CRITICAL RULES**:
1. **District Comparison**: When user says "compare X and Y" or "X vs Y" → Use districts=[X, Y], year=last_year or most recent
2. **Time Comparison**: When user says "compare X in 2020 and 2023" → Use district=X, years=[2020, 2023]
3. **Context Usage**: 
   - "what about 2022?" → Use last_district
   - "compare with Pune" → Use last_year
   - "show that for 2023" → Use last_district
4. **Year Format**: Accept both 23 (→2023) and 2023
5. **Always specify** what you're comparing in your response

**FUNCTION CALLING**:
- For comparing 2+ districts in same year: districts=[...], year="2023"
- For comparing same district across years: district="X", years=["2020", "2023"]
- For single query: district="X", year="2023"

**RESPONSE FORMAT**:
Always explain what data you're showing:
- "Here's data for **Jalandhar** in **2023**"
- "Comparing **Pune** and **Mumbai** for **2022**"
- "Showing **Delhi** across **2020, 2021, 2022**"

User language: {LANGS[language]['name']}"""

    try:
        functions = [{
            "type": "function",
            "function": {
                "name": "query_data",
                "description": "Query groundwater database. For comparing districts use 'districts' array. For comparing years use 'years' array.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "district": {"type": "string", "description": "Single district name"},
                        "year": {"type": "string", "description": "Single year (4-digit)"},
                        "districts": {"type": "array", "items": {"type": "string"}, "description": "Multiple districts for comparison"},
                        "years": {"type": "array", "items": {"type": "string"}, "description": "Multiple years for time series"}
                    }
                }
            }
        }]

        response = client.chat.completions.create(
            model="z-ai/glm-4.5-air:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            tools=functions,
            temperature=0.3,
            max_tokens=1200
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]

            # JSON parsing with error handling
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                return {
                    'type': 'error',
                    'message': "AI returned invalid data format. Please try rephrasing your question.",
                    'success': False
                }

            success, data = query_data(**function_args)

            # Handle need_year/need_district
            if not success and isinstance(data, dict):
                if data.get('type') == 'need_year':
                    return {
                        'type': 'conversation',
                        'message': f"I found **{data['district']}**! 📍\n\nWhich year? Available: {', '.join(data['available_years'])}",
                        'success': True
                    }
                elif data.get('type') == 'need_district':
                    return {
                        'type': 'conversation',
                        'message': f"I have data for **{data['year']}**! 📅\n\nWhich district?\n\n{', '.join(data['available_districts'][:8])}...",
                        'success': True
                    }

            return {
                'type': 'data_query',
                'success': success,
                'data': data,
                'params': function_args,
                'ai_message': message.content
            }

        if message.content:
            return {
                'type': 'conversation',
                'message': message.content,
                'success': True
            }

        return {
            'type': 'conversation',
            'message': "I'm here to help! Ask about groundwater data for any district and year.",
            'success': True
        }

    except Exception as e:
        return {
            'type': 'error',
            'message': f"AI service error: {str(e)}. Please try again.",
            'success': False
        }


# ============= DISPLAY FUNCTIONS =============
def render_single_card(data, l):
    """Render single district data card"""
    st.markdown(f"### ✅ Data for **{data['District']}** ({data['Year']})")
    st.info(f"🤖 AI-Validated from database")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("🌊 Groundwater Level", f"{data['Groundwater_Level_m']} m")
        st.metric("💧 Annual Recharge", f"{data['Recharge_BCM']} BCM")
    with c2:
        st.metric("📊 Category", data['Category'])
        st.metric("📉 Total Extraction", f"{data['Extraction_BCM']} BCM")

    if data['Groundwater_Level_m'] < 5:
        st.warning("⚠️ Critical: Very low groundwater level")
    elif data['Groundwater_Level_m'] > 20:
        st.success("✅ Healthy groundwater level")


def render_district_comparison(data_list, year, l):
    """Render district comparison"""
    st.markdown(f"### 📊 District Comparison for **{year}**")

    num_items = len(data_list)
    cols_per_row = 2 if num_items > 1 else 1

    for i in range(0, num_items, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < num_items:
                dd = data_list[i + j]
                with cols[j]:
                    st.markdown(f"#### 📍 **{dd['District']}**")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("🌊 GW Level", f"{dd['Groundwater_Level_m']} m")
                        st.metric("💧 Recharge", f"{dd['Recharge_BCM']} BCM")
                    with c2:
                        st.metric("📊 Category", dd['Category'])
                        st.metric("📉 Extraction", f"{dd['Extraction_BCM']} BCM")

                    st.markdown("---")

    # Comparison insights
    st.markdown("#### 🔍 Comparison Insights")
    df_compare = pd.DataFrame(data_list)
    best = df_compare.loc[df_compare['Groundwater_Level_m'].idxmax()]
    worst = df_compare.loc[df_compare['Groundwater_Level_m'].idxmin()]

    st.markdown(f"""
        <div style='background:#f8f9fa;padding:1rem;border-radius:10px;border-left:4px solid #2d3561'>
            <strong>🏆 Highest Level:</strong> {best['District']} ({best['Groundwater_Level_m']}m)<br>
            <strong>⚠️ Lowest Level:</strong> {worst['District']} ({worst['Groundwater_Level_m']}m)<br>
            <strong>📊 Average:</strong> {df_compare['Groundwater_Level_m'].mean():.2f}m
        </div>
    """, unsafe_allow_html=True)


def render_time_series(data_list, l):
    """Render time series comparison"""
    district = data_list[0]['District']
    st.markdown(f"### 📈 Time Series for **{district}**")

    num_items = len(data_list)
    cols_per_row = min(3, num_items)

    for i in range(0, num_items, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < num_items:
                dd = data_list[i + j]
                with cols[j]:
                    st.markdown(f"#### 📅 **{dd['Year']}**")
                    st.metric("🌊 GW Level", f"{dd['Groundwater_Level_m']} m")
                    st.metric("📊 Category", dd['Category'])
                    st.markdown("---")

    # Trend analysis
    if len(data_list) > 1:
        st.markdown("#### 🔍 Trend Analysis")
        first, last = data_list[0], data_list[-1]
        change = last['Groundwater_Level_m'] - first['Groundwater_Level_m']

        if change < 0:
            color, icon, text = "#dc3545", "📉", "Declining"
        elif change > 0:
            color, icon, text = "#28a745", "📈", "Improving"
        else:
            color, icon, text = "#ffc107", "➡️", "Stable"

        st.markdown(f"""
            <div style='background:#f8f9fa;padding:1rem;border-radius:10px;border-left:4px solid {color}'>
                <strong>{icon} Trend:</strong> {text}<br>
                <strong>Change:</strong> {change:+.2f}m (from {first['Year']} to {last['Year']})
            </div>
        """, unsafe_allow_html=True)


# ============= MAIN UI =============
with st.sidebar:
    st.markdown("""<div style='background:linear-gradient(135deg,#1a2332 0%,#2d1f33 100%);padding:1.2rem;border-radius:12px;margin-bottom:1rem;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,.15)'><h3 style='color:#fff;margin:0;font-weight:700'>🌍 Language</h3></div>""", unsafe_allow_html=True)
    sl = st.selectbox("Language", list(LANGS.keys()), 
                      format_func=lambda x: f"{LANGS[x]['flag']} {LANGS[x]['name']}", 
                      index=list(LANGS.keys()).index(st.session_state.language), 
                      label_visibility="collapsed")
    if sl != st.session_state.language:
        st.session_state.language = sl
        st.rerun()
    st.divider()

    st.markdown("### 🤖 AI Status")
    st.success("✅ DeepSeek Connected")
    st.caption("✨ Smart district comparison")
    st.caption("🧠 Context-aware responses")
    st.caption("📅 Year normalization (23=2023)")

    if st.session_state.messages:
        st.divider()
        st.markdown("### 📊 Session Stats")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("💬 Messages", len(st.session_state.messages))
        with c2:
            st.metric("❓ Queries", len([m for m in st.session_state.messages if m['role'] == 'user']))

        st.divider()
        st.markdown("### 🧠 Context Memory")
        memory = st.session_state.context_memory
        if memory['last_district']:
            st.info(f"📍 Last: **{memory['last_district']}**")
        if memory['last_year']:
            st.info(f"📅 Year: **{memory['last_year']}**")


# Header
c1, c2, c3 = st.columns([1, 3, 1])
with c2:
    st.markdown(f"<div style='text-align:center;padding:1.5rem 0'><h1 style='font-size:2.8rem;margin-bottom:.8rem;color:#1a2332;font-weight:800'>💧 INGRES AI</h1><p style='font-size:1.15rem;color:#424242;margin-bottom:0;font-weight:500'>{gt('subtitle', st.session_state.language)}</p><p style='font-size:0.9rem;color:#666;margin-top:0.5rem'>🤖 Powered by DeepSeek | 🧠 Context-Aware</p></div>", unsafe_allow_html=True)


# Quick Actions
st.markdown("### 🎯 Quick Actions")
c1, c2, c3, c4, c5 = st.columns(5)
if c1.button("📊 View Data", key="qd", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": "Show me Jalandhar 23"})
    st.rerun()
if c2.button("📈 Time Series", key="qc", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": "Compare Jalandhar 20, 21, 22, 23"})
    st.rerun()
if c3.button("🗺️ Compare Districts", key="qa", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": "Compare Pune and Mumbai for 22"})
    st.rerun()
if c4.button("❓ Help", key="qh", use_container_width=True):
    st.session_state.messages.append({"role": "user", "content": "What can you do?"})
    st.rerun()
if c5.button("🗑️ Clear", key="qcl", use_container_width=True):
    st.session_state.messages = []
    st.session_state.data_cards = {}
    st.session_state.context_memory = {
        'last_district': None,
        'last_year': None,
        'recent_districts': [],
        'recent_years': []
    }
    st.rerun()
st.divider()


# Chat Display
if not st.session_state.messages:
    st.markdown(f"""<div style='text-align:center;padding:3rem 2rem;background:linear-gradient(135deg,#e8eef5 0%,#d4dce8 100%);border-radius:20px;margin:2rem 0;box-shadow:0 8px 25px rgba(0,0,0,.12);border:2px solid #c5d1e0'>
    <h2 style='color:#1a2332;margin-bottom:1rem;font-weight:700'>👋 Welcome to INGRES AI!</h2>
    <p style='font-size:1.15rem;color:#2c3e50;margin-bottom:2rem;font-weight:500'>Smart district comparison & context-aware assistant</p>
    <div style='background:#fff;padding:1.8rem;border-radius:15px;margin-top:2rem;box-shadow:0 4px 15px rgba(0,0,0,.1);border:1px solid #d0d0d0'>
    <p style='color:#424242;margin-bottom:1rem;font-weight:600;font-size:1.05rem'>Try these queries:</p>
    <p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "Show me Jalandhar 23"</p>
    <p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "Compare Pune and Mumbai for 22"</p>
    <p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "Compare Jalandhar 20, 21, 22"</p>
    </div></div>""", unsafe_allow_html=True)
else:
    for i, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
            st.markdown(m["content"])
            if i in st.session_state.data_cards:
                card = st.session_state.data_cards[i]
                if 'comparison_type' in card:
                    if card['comparison_type'] == 'districts':
                        render_district_comparison(card['data'], card['year'], st.session_state.language)
                    elif card['comparison_type'] == 'time_series':
                        render_time_series(card['data'], st.session_state.language)
                else:
                    render_single_card(card['data'], st.session_state.language)


# Chat Input Handler
if p := st.chat_input(gt('input', st.session_state.language)):
    pe = tr(p, 'en', st.session_state.language) if st.session_state.language != 'en' else p

    st.chat_message("user", avatar="👤").markdown(p)
    st.session_state.messages.append({"role": "user", "content": p})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤖 Processing..."):
            ai_result = get_ai_response(pe, st.session_state.language)

            if ai_result['type'] == 'data_query' and ai_result['success']:
                data = ai_result['data']
                params = ai_result['params']

                # Handle different response types
                if isinstance(data, dict):
                    if data.get('type') == 'district_comparison':
                        # District comparison
                        render_district_comparison(data['data'], data['year'], st.session_state.language)
                        response = f"✅ Comparing **{len(data['data'])} districts** for **{data['year']}**"
                        st.markdown(response)

                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.data_cards[len(st.session_state.messages) - 1] = {
                            'comparison_type': 'districts',
                            'data': data['data'],
                            'year': data['year']
                        }

                    elif data.get('type') == 'time_series':
                        # Time series
                        render_time_series(data['data'], st.session_state.language)
                        district = data['data'][0]['District']
                        response = f"✅ Time series for **{district}** ({len(data['data'])} years)"
                        st.markdown(response)

                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.data_cards[len(st.session_state.messages) - 1] = {
                            'comparison_type': 'time_series',
                            'data': data['data']
                        }

                    else:
                        # Single result
                        render_single_card(data, st.session_state.language)
                        response = f"✅ Data for **{data['District']}** ({data['Year']})"
                        st.markdown(response)

                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.data_cards[len(st.session_state.messages) - 1] = {
                            'data': data
                        }

                else:
                    # Single dict result
                    render_single_card(data, st.session_state.language)
                    response = f"✅ Data for **{data['District']}** ({data['Year']})"
                    st.markdown(response)

                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.data_cards[len(st.session_state.messages) - 1] = {
                        'data': data
                    }

            elif ai_result['type'] == 'conversation':
                response = ai_result['message']
                translated = tr(response, st.session_state.language) if st.session_state.language != 'en' else response
                st.markdown(translated)
                st.session_state.messages.append({"role": "assistant", "content": translated})

            else:
                error_msg = tr(ai_result.get('message', 'Error processing query'), st.session_state.language)
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # CRITICAL FIX: Rerun after processing
    st.rerun()

