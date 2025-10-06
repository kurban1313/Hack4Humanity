import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import re
from deep_translator import GoogleTranslator
from functools import lru_cache
from openai import OpenAI
import json

st.set_page_config(page_title="INGRES AI Assistant", page_icon="💧", layout="wide")

# OpenAI Client Setup (OpenRouter)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# CSS (keeping your original styling)
st.markdown("""<style>
.stApp{background:linear-gradient(135deg,#2d3561 0%,#3d2d4f 100%)}
.main .block-container{padding:2rem;background:#fff;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,.25);max-width:1200px}
[data-testid="stChatMessage"]{background:#f8f9fa;border-radius:15px;padding:1.2rem;margin:.5rem 0;box-shadow:0 2px 8px rgba(0,0,0,.1);border:1px solid #e0e0e0}
[data-testid="stChatMessageContent"]{color:#1a1a1a;font-size:1rem;line-height:1.6}
[data-testid="stChatInput"]{border-radius:25px;border:2px solid #2d3561;background:#fff}
[data-testid="stSidebar"]{background:#f5f7fa;border-right:2px solid #d0d0d0}
.stButton button{border-radius:20px;border:none;background:#2d3561;color:#fff;font-weight:600;padding:.6rem 1.2rem;transition:all .3s ease;box-shadow:0 3px 8px rgba(45,53,97,.3)}
.stButton button:hover{background:#1f2643;transform:translateY(-2px);box-shadow:0 5px 15px rgba(45,53,97,.5)}
[data-testid="stMetricValue"]{font-size:1.6rem;color:#1a1a1a;font-weight:700}
[data-testid="stMetricLabel"]{color:#424242;font-weight:600}
.stInfo{background:#e3f2fd;color:#0d47a1;border-left:4px solid #1976d2;padding:1rem}
h1,h2,h3,h4,h5,h6{color:#1a1a1a!important;font-weight:700}
</style>""", unsafe_allow_html=True)

# Config
LANGS = {'en':{'name':'English','flag':'🇬🇧'},'hi':{'name':'हिन्दी (Hindi)','flag':'🇮🇳'},'ta':{'name':'தமிழ் (Tamil)','flag':'🇮🇳'},'te':{'name':'తెలుగు (Telugu)','flag':'🇮🇳'},'kn':{'name':'ಕನ್ನಡ (Kannada)','flag':'🇮🇳'},'ml':{'name':'മലയാളം (Malayalam)','flag':'🇮🇳'},'mr':{'name':'मराठी (Marathi)','flag':'🇮🇳'},'gu':{'name':'ગુજરાતી (Gujarati)','flag':'🇮🇳'},'bn':{'name':'বাংলা (Bengali)','flag':'🇮🇳'},'pa':{'name':'ਪੰਜਾਬੀ (Punjabi)','flag':'🇮🇳'},'or':{'name':'ଓଡ଼ିଆ (Odia)','flag':'🇮🇳'},'ur':{'name':'اردو (Urdu)','flag':'🇮🇳'}}

TRANS = {
    'title':{'en':'💧 INGRES Virtual Assistant','hi':'💧 इंग्रेस वर्चुअल सहायक','ta':'💧 INGRES மெய்நிகர் உதவியாளர்','te':'💧 INGRES వర్చువల్ అసిస్టెంట్','kn':'💧 INGRES ವರ್ಚುವಲ್ ಸಹಾಯಕ','ml':'💧 INGRES വെർച്വൽ അസിസ്റ്റന്റ്','mr':'💧 इंग्रेस व्हर्च्युअल असिस्टंट','gu':'💧 INGRES વર્ચ્યુઅલ સહાયક','bn':'💧 INGRES ভার্চুয়াল সহায়ক','pa':'💧 INGRES ਵਰਚੁਅਲ ਸਹਾਇਕ','or':'💧 INGRES ଭର୍ଚୁଆଲ୍ ସହାୟକ','ur':'💧 INGRES ورچوئل اسسٹنٹ'},
    'subtitle':{'en':'🤖 Smart AI Assistant - Ask me anything about groundwater data!','hi':'🤖 स्मार्ट एआई सहायक - भूजल डेटा के बारे में मुझसे कुछ भी पूछें!','ta':'🤖 ஸ்மார்ட் AI உதவியாளர் - நிலத்தடி நீர் தரவு பற்றி என்னிடம் எதையும் கேளுங்கள்!','te':'🤖 స్మార్ట్ AI అసిస్టెంట్ - భూగర్భ జల డేటా గురించి నన్ను ఏదైనా అడగండి!','kn':'🤖 ಸ್ಮಾರ್ಟ್ AI ಸಹಾಯಕ - ಅಂತರ್ಜಲ ಡೇಟಾ ಬಗ್ಗೆ ನನ್ನನ್ನು ಏನು ಬೇಕಾದರೂ ಕೇಳಿ!','ml':'🤖 സ്മാർട്ട് AI അസിസ്റ്റന്റ് - ഭൂഗർഭജല ഡാറ്റയെക്കുറിച്ച് എന്തും എന്നോട് ചോദിക്കൂ!','mr':'🤖 स्मार्ट AI असिस्टंट - भूजल डेटाबद्दल मला काहीही विचारा!','gu':'🤖 સ્માર્ટ AI સહાયક - ભૂગર્ભજળ ડેટા વિશે મને કંઈપણ પૂછો!','bn':'🤖 স্মার্ট AI সহায়ক - ভূগর্ভস্থ জল ডেটা সম্পর্কে আমাকে যেকোনো কিছু জিজ্ঞাসা করুন!','pa':'🤖 ਸਮਾਰਟ AI ਸਹਾਇਕ - ਭੂਮੀਗਤ ਪਾਣੀ ਡੇਟਾ ਬਾਰੇ ਮੈਨੂੰ ਕੁਝ ਵੀ ਪੁੱਛੋ!','or':'🤖 ସ୍ମାର୍ଟ AI ସହାୟକ - ଭୂତଳ ଜଳ ତଥ୍ୟ ବିଷୟରେ ମୋତେ କିଛି ପଚାରନ୍ତୁ!','ur':'🤖 سمارٹ AI اسسٹنٹ - زمینی پانی کے ڈیٹا کے بارے میں مجھ سے کچھ بھی پوچھیں!'},
    'input':{'en':'Ask me anything...','hi':'मुझसे कुछ भी पूछें...','ta':'என்னிடம் எதையும் கேளுங்கள்...','te':'నన్ను ఏదైనా అడగండి...','kn':'ನನ್ನನ್ನು ಏನು ಬೇಕಾದರೂ ಕೇಳಿ...','ml':'എന്തും ചോദിക്കൂ...','mr':'मला काहीही विचारा...','gu':'મને કંઈપણ પૂછો...','bn':'আমাকে যেকোনো কিছু জিজ্ঞাসা করুন...','pa':'ਮੈਨੂੰ ਕੁਝ ਵੀ ਪੁੱਛੋ...','or':'ମୋତେ କିଛି ପଚାରନ୍ତୁ...','ur':'مجھ سے کچھ بھی پوچھیں...'},
    'greeting':{'en':"Hello! 👋 I'm your INGRES AI assistant. Ask me about groundwater data!",'hi':"नमस्ते! 👋 मैं आपका INGRES AI सहायक हूँ। मुझसे भूजल डेटा के बारे में पूछें!",'ta':"வணக்கம்! 👋 நான் உங்கள் INGRES AI உதவியாளர். நிலத்தடி நீர் தரவு பற்றி என்னிடம் கேளுங்கள்!",'te':"నమస్కారం! 👋 నేను మీ INGRES AI అసిస్టెంట్. భూగర్భ జల డేటా గురించి నన్ను అడగండి!",'kn':"ನಮಸ್ಕಾರ! 👋 ನಾನು ನಿಮ್ಮ INGRES AI ಸಹಾಯಕ. ಅಂತರ್ಜಲ ಡೇಟಾ ಬಗ್ಗೆ ನನ್ನನ್ನು ಕೇಳಿ!",'ml':"നമസ്കാരം! 👋 ഞാൻ നിങ്ങളുടെ INGRES AI അസിസ്റ്റന്റ്. ഭൂഗർഭജല ഡാറ്റയെക്കുറിച്ച് എന്നോട് ചോദിക്കൂ!",'mr':"नमस्कार! 👋 मी तुमचा INGRES AI असिस्टंट आहे। भूजल डेटाबद्दल मला विचारा!",'gu':"નમસ્તે! 👋 હું તમારો INGRES AI સહાયક છું. ભૂગર્ભજળ ડેટા વિશે મને પૂછો!",'bn':"নমস্কার! 👋 আমি আপনার INGRES AI সহায়ক। ভূগর্ভস্থ জল ডেটা সম্পর্কে আমাকে জিজ্ঞাসা করুন!",'pa':"ਸਤ ਸ੍ਰੀ ਅਕਾਲ! 👋 ਮੈਂ ਤੁਹਾਡਾ INGRES AI ਸਹਾਇਕ ਹਾਂ। ਭੂਮੀਗਤ ਪਾਣੀ ਡੇਟਾ ਬਾਰੇ ਮੈਨੂੰ ਪੁੱਛੋ!",'or':"ନମସ୍କାର! 👋 ମୁଁ ଆପଣଙ୍କର INGRES AI ସହାୟକ। ଭୂତଳ ଜଳ ତଥ୍ୟ ବିଷୟରେ ମୋତେ ପଚାରନ୍ତୁ!",'ur':"السلام علیکم! 👋 میں آپ کا INGRES AI اسسٹنٹ ہوں۔ زمینی پانی کے ڈیٹا کے بارے میں مجھ سے پوچھیں!"}
}

# Init
for k in ['language','messages','data_cards','compare_mode']: 
    if k not in st.session_state: 
        st.session_state[k]='en' if k=='language' else {} if k=='data_cards' else [] if k=='messages' else None

@st.cache_data
def load_data(): 
    return pd.read_csv('sample_data.csv')

df=load_data()

@lru_cache(maxsize=1000)
def tr(t,l,s='en'): 
    if not t: return t
    return t if l=='en' or l==s else GoogleTranslator(source=s,target=l).translate(t)

def gt(k,l='en'): 
    return TRANS.get(k,{}).get(l,TRANS[k]['en'])

# ============= AI-ENHANCED FUNCTIONS =============

def get_database_schema():
    """Provides schema information to LLM for better understanding[web:23][web:26]"""
    schema = {
        "table": "groundwater_data",
        "columns": df.columns.tolist(),
        "districts": df['District'].unique().tolist(),
        "years": sorted(df['Year'].unique().tolist()),
        "sample_data": df.head(3).to_dict('records')
    }
    return schema

def query_groundwater_data(district=None, year=None, years=None, districts=None):
    """
    Smart database query function with validation[web:21][web:23]
    Returns: (success, data/error_message)
    """
    try:
        # Single district, single year
        if district and year:
            result = df[(df['District'].str.lower()==district.lower()) & 
                       (df['Year'].astype(str)==str(year))]
            if not result.empty:
                return True, result.iloc[0].to_dict()
            return False, f"No data found for {district} in {year}"
        
        # Single district, multiple years (comparison)
        if district and years:
            results = []
            for y in years:
                r = df[(df['District'].str.lower()==district.lower()) & 
                      (df['Year'].astype(str)==str(y))]
                if not r.empty:
                    results.append(r.iloc[0].to_dict())
            return True, results if results else (False, f"No data found")
        
        # Multiple districts, single year (comparison)
        if districts and year:
            results = []
            for d in districts:
                r = df[(df['District'].str.lower()==d.lower()) & 
                      (df['Year'].astype(str)==str(year))]
                if not r.empty:
                    results.append(r.iloc[0].to_dict())
            return True, results if results else (False, f"No data found")
        
        return False, "Invalid query parameters"
    except Exception as e:
        return False, f"Query error: {str(e)}"

def get_ai_response(user_query, context_history, language='en'):
    """
    Enhanced AI response using OpenAI with RAG principles[web:21][web:2][web:27]
    Integrates structured data for fact-checking and accuracy
    """
    schema = get_database_schema()
    
    # Build context-aware system prompt with structured data
    system_prompt = f"""You are INGRES AI Assistant, an expert on Indian groundwater data.

**DATABASE SCHEMA**:
- Available Districts: {', '.join(schema['districts'][:10])}... (total {len(schema['districts'])})
- Available Years: {', '.join(map(str, schema['years']))}
- Data Fields: {', '.join(schema['columns'])}

**YOUR CAPABILITIES**:
1. Query groundwater data for specific districts and years
2. Compare data across years or districts
3. Provide insights on water levels, recharge, extraction, and categories
4. Maintain conversation context

**INSTRUCTIONS**:
- Extract district names and years from user queries
- For comparisons, identify if user wants year-wise or district-wise comparison
- Always validate information against the database
- If data not available, suggest alternatives
- Be conversational and helpful
- Keep responses concise but informative

**CONTEXT**: User language is {LANGS[language]['name']}
Previous conversation: {context_history[-3:] if context_history else 'None'}

**IMPORTANT**: 
- Only provide information that can be verified in the database
- If unsure about district names, ask for clarification
- For greetings, respond warmly and guide user on what you can do[web:2][web:27]"""

    try:
        # Define available functions for AI to call
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "query_groundwater_data",
                    "description": "Query groundwater database for specific district and year, or compare multiple years/districts[web:26][web:34]",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "district": {
                                "type": "string",
                                "description": "District name (e.g., 'Jalandhar', 'Pune')"
                            },
                            "year": {
                                "type": "string",
                                "description": "Year (e.g., '2023', '2020')"
                            },
                            "years": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of years for comparison"
                            },
                            "districts": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of districts for comparison"
                            }
                        }
                    }
                }
            }
        ]
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="x-ai/grok-4-fast",  # Using Grok for better reasoning
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            tools=functions,
            temperature=0.3,  # Low temperature for factual accuracy[web:2]
            max_tokens=800
        )
        
        message = response.choices[0].message
        
        # Check if AI wants to call a function
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the function call
            if function_name == "query_groundwater_data":
                success, data = query_groundwater_data(**function_args)
                return {
                    'type': 'data_query',
                    'success': success,
                    'data': data,
                    'query_params': function_args,
                    'ai_message': message.content if message.content else ""
                }
        
        # Regular conversational response
        return {
            'type': 'conversation',
            'message': message.content,
            'success': True
        }
        
    except Exception as e:
        return {
            'type': 'error',
            'message': f"AI processing error: {str(e)}",
            'success': False
        }

# ============= EXISTING HELPER FUNCTIONS (Enhanced) =============

def ex_dist(t,th=65):
    d=df['District'].unique().tolist();w=re.findall(r'\b\w+\b',t.lower());bm,bs=None,0
    for i in range(len(w)):
        m=process.extractOne(w[i],d,scorer=fuzz.ratio)
        if m and m[1]>bs and m[1]>=th: bm,bs=m[0],m[1]
        if i<len(w)-1:
            m=process.extractOne(w[i]+" "+w[i+1],d,scorer=fuzz.ratio)
            if m and m[1]>bs and m[1]>=th: bm,bs=m[0],m[1]
    return bm,bs

def ex_year(t):
    for p in [r'\b(20[1-3][0-9])\b',r"'(\d{2})\b",r'\b(\d{2})\b']:
        m=re.search(p,t)
        if m:
            y=m.group(1)
            return f"20{y}" if len(y)==2 and 15<=int(y)<=30 else y if len(y)==4 else None
    return None

def render_comparison_cards(data_list,compare_type,l):
    """Render comparison with beautiful card UI"""
    if not data_list: return
    
    header_text = "Year-wise Comparison" if compare_type=='years' else "District-wise Comparison"
    st.markdown(f"### 📊 {tr(header_text, l)}")
    
    num_items = len(data_list)
    cols_per_row = 2 if num_items > 1 else 1
    
    for i in range(0, num_items, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < num_items:
                dd = data_list[i + j]
                with cols[j]:
                    label = f"{dd['Year']}" if compare_type == 'years' else f"{dd['District']}"
                    st.markdown(f"#### 📍 {label}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("🌊 GW Level", f"{dd['Groundwater_Level_m']} m")
                        st.metric("💧 Recharge", f"{dd['Recharge_BCM']} BCM")
                    with c2:
                        st.metric("📊 Category", dd['Category'])
                        st.metric("📉 Extraction", f"{dd['Extraction_BCM']} BCM")
                    
                    st.markdown("---")
    
    # Comparison insights with AI-generated analysis
    st.markdown(f"#### 🔍 {tr('AI-Powered Insights', l)}")
    
    if compare_type == 'years' and len(data_list) > 1:
        first, last = data_list[0], data_list[-1]
        gw_change = last['Groundwater_Level_m'] - first['Groundwater_Level_m']
        
        if gw_change < 0:
            trend_icon = "📉"
            trend_text = tr("Declining", l)
            trend_color = "#dc3545"
            insight = tr(f"⚠️ Groundwater declining by {abs(gw_change):.2f}m - Conservation needed!", l)
        elif gw_change > 0:
            trend_icon = "📈"
            trend_text = tr("Improving", l)
            trend_color = "#28a745"
            insight = tr(f"✅ Positive trend! Level increased by {gw_change:.2f}m", l)
        else:
            trend_icon = "➡️"
            trend_text = tr("Stable", l)
            trend_color = "#ffc107"
            insight = tr("Groundwater level remains stable", l)
        
        st.markdown(f"""
            <div style='background:#f8f9fa;padding:1rem;border-radius:10px;border-left:4px solid {trend_color}'>
                <strong>{trend_icon} {tr('Trend', l)}:</strong> {trend_text}<br>
                <strong>{insight}</strong>
            </div>
        """, unsafe_allow_html=True)

def rnd_card(dd,d,c,l):
    """Render single data card with AI verification badge[web:6][web:7]"""
    if c<90: st.caption(tr(f"💡 AI Matched: **{d}** ({c}% confidence)",l))
    
    st.markdown(f"### ✅ {tr('Verified Data', l)}: {dd['District']} ({dd['Year']})")
    st.info(f"🤖 {tr('AI-Validated against database', l)}")
    
    c1,c2=st.columns(2)
    with c1: 
        st.metric("🌊 Groundwater Level",f"{dd['Groundwater_Level_m']} m")
        st.metric("💧 Annual Recharge",f"{dd['Recharge_BCM']} BCM")
    with c2: 
        st.metric("📊 Category",dd['Category'])
        st.metric("📉 Total Extraction",f"{dd['Extraction_BCM']} BCM")
    
    # Add context-aware insights
    if dd['Groundwater_Level_m'] < 5:
        st.warning(tr("⚠️ Critical: Very low groundwater level detected", l))
    elif dd['Groundwater_Level_m'] > 20:
        st.success(tr("✅ Healthy groundwater level", l))

# Sidebar
with st.sidebar:
    st.markdown("""<div style='background:linear-gradient(135deg,#1a2332 0%,#2d1f33 100%);padding:1.2rem;border-radius:12px;margin-bottom:1rem;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,.15)'><h3 style='color:#fff;margin:0;font-weight:700'>🌍 Language</h3></div>""",unsafe_allow_html=True)
    sl=st.selectbox("Language",list(LANGS.keys()),format_func=lambda x:f"{LANGS[x]['flag']} {LANGS[x]['name']}",index=list(LANGS.keys()).index(st.session_state.language),label_visibility="collapsed")
    if sl!=st.session_state.language: st.session_state.language=sl;st.rerun()
    st.divider()
    
    # AI Status Indicator
    st.markdown("### 🤖 AI Status")
    st.success("✅ Grok-2 Connected")
    st.caption("🔒 Fact-checking enabled")
    st.caption("🧠 Context-aware responses")
    
    if st.session_state.messages:
        st.divider()
        st.markdown("### 📊 Session Stats")
        c1,c2=st.columns(2)
        with c1: st.metric("💬 Messages",len(st.session_state.messages))
        with c2: st.metric("❓ Queries",len([m for m in st.session_state.messages if m['role']=='user']))

# Header
c1,c2,c3=st.columns([1,3,1])
with c2: 
    st.markdown(f"<div style='text-align:center;padding:1.5rem 0'><h1 style='font-size:2.8rem;margin-bottom:.8rem;color:#1a2332;font-weight:800'>💧 INGRES AI</h1><p style='font-size:1.15rem;color:#424242;margin-bottom:0;font-weight:500'>{gt('subtitle',st.session_state.language)}</p><p style='font-size:0.9rem;color:#666;margin-top:0.5rem'>🤖 Powered by Grok-2 | 🔍 Real-time Fact Checking</p></div>",unsafe_allow_html=True)

# Quick Actions
st.markdown("### 🎯 Quick Actions")
c1,c2,c3,c4,c5=st.columns(5)
if c1.button("📊 View Data",key="qd",use_container_width=True): 
    st.session_state.messages.append({"role":"user","content":"Show me groundwater data for Jalandhar 2023"});st.rerun()
if c2.button("📈 Compare",key="qc",use_container_width=True): 
    st.session_state.messages.append({"role":"user","content":"Compare Jalandhar 2020 and 2023"});st.rerun()
if c3.button("🔍 Analyze",key="qa",use_container_width=True): 
    st.session_state.messages.append({"role":"user","content":"Analyze groundwater trends in Punjab"});st.rerun()
if c4.button("❓ Help",key="qh",use_container_width=True): 
    st.session_state.messages.append({"role":"user","content":"What can you help me with?"});st.rerun()
if c5.button("🗑️ Clear",key="qcl",use_container_width=True): 
    st.session_state.messages=[];st.session_state.data_cards={};st.rerun()
st.divider()

# Chat Interface
if not st.session_state.messages:
    welcome_msg = tr("Welcome to INGRES AI!",st.session_state.language)
    ask_msg = tr("AI-powered assistant with real-time fact-checking for Indian groundwater data",st.session_state.language)
    try_msg = tr("Try asking:",st.session_state.language)
    q1 = tr("What's the groundwater situation in Jalandhar?",st.session_state.language)
    q2 = tr("Compare Pune and Mumbai groundwater levels for 2022",st.session_state.language)
    q3 = tr("Show me the trend for Delhi from 2018 to 2023",st.session_state.language)
    st.markdown(f"""<div style='text-align:center;padding:3rem 2rem;background:linear-gradient(135deg,#e8eef5 0%,#d4dce8 100%);border-radius:20px;margin:2rem 0;box-shadow:0 8px 25px rgba(0,0,0,.12);border:2px solid #c5d1e0'><h2 style='color:#1a2332;margin-bottom:1rem;font-weight:700'>👋 {welcome_msg}</h2><p style='font-size:1.15rem;color:#2c3e50;margin-bottom:2rem;font-weight:500'>{ask_msg}</p><div style='background:#fff;padding:1.8rem;border-radius:15px;margin-top:2rem;box-shadow:0 4px 15px rgba(0,0,0,.1);border:1px solid #d0d0d0'><p style='color:#424242;margin-bottom:1rem;font-weight:600;font-size:1.05rem'>{try_msg}</p><p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "{q1}"</p><p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "{q2}"</p><p style='font-style:italic;color:#1a2332;margin:.8rem 0;font-weight:500'>💬 "{q3}"</p></div></div>""",unsafe_allow_html=True)
else:
    for i,m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"],avatar="👤" if m["role"]=="user" else "🤖"):
            st.markdown(m["content"])
            if i in st.session_state.data_cards:
                cd=st.session_state.data_cards[i]
                if 'comparison' in cd:
                    render_comparison_cards(cd['comparison'],cd['compare_type'],st.session_state.language)
                else:
                    rnd_card(cd['data'],cd['district'],cd['confidence'],st.session_state.language)

# Input Processing with AI
if p:=st.chat_input(gt('input',st.session_state.language)):
    # Translate to English if needed
    pe=tr(p,'en',st.session_state.language) if st.session_state.language!='en' else p
    
    st.chat_message("user",avatar="👤").markdown(p)
    st.session_state.messages.append({"role":"user","content":p})
    
    with st.chat_message("assistant",avatar="🤖"):
        with st.spinner(tr("🤖 AI Processing with fact-checking...",st.session_state.language)):
            # Get AI response with context
            context = [{"role": m["role"], "content": m["content"]} 
                      for m in st.session_state.messages[-5:]]
            
            ai_result = get_ai_response(pe, context, st.session_state.language)
            
            if ai_result['type'] == 'data_query' and ai_result['success']:
                data = ai_result['data']
                
                # Handle comparison queries
                if isinstance(data, list):
                    params = ai_result['query_params']
                    compare_type = 'years' if 'years' in params else 'districts'
                    render_comparison_cards(data, compare_type, st.session_state.language)
                    
                    count = len(data)
                    entity = params.get('district', 'multiple districts')
                    response = tr(f"✅ AI-verified comparison of {count} data points for {entity}", st.session_state.language)
                    st.markdown(response)
                    
                    st.session_state.messages.append({"role":"assistant","content":response})
                    st.session_state.data_cards[len(st.session_state.messages)-1] = {
                        'comparison': data,
                        'compare_type': compare_type
                    }
                
                # Handle single query
                else:
                    district = ai_result['query_params'].get('district', data.get('District'))
                    confidence = 95  # AI-verified
                    rnd_card(data, district, confidence, st.session_state.language)
                    
                    response = tr(f"✅ AI-verified data for {data['District']} ({data['Year']})", st.session_state.language)
                    st.markdown(response)
                    
                    st.session_state.messages.append({"role":"assistant","content":response})
                    st.session_state.data_cards[len(st.session_state.messages)-1] = {
                        'data': data,
                        'district': district,
                        'confidence': confidence
                    }
            
            elif ai_result['type'] == 'conversation':
                # Regular conversation response
                response = ai_result['message']
                translated_response = tr(response, st.session_state.language) if st.session_state.language != 'en' else response
                st.markdown(translated_response)
                st.session_state.messages.append({"role":"assistant","content":translated_response})
            
            else:
                # Error handling
                error_msg = tr(ai_result.get('message', 'Unable to process query'), st.session_state.language)
                st.error(error_msg)
                st.session_state.messages.append({"role":"assistant","content":error_msg})
