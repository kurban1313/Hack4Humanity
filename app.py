import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz, process
import re
from deep_translator import GoogleTranslator
from functools import lru_cache

st.set_page_config(page_title="INGRES AI Assistant", page_icon="💧", layout="wide")

# CSS
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
def load_data(): return pd.read_csv('sample_data.csv')
df=load_data()

@lru_cache(maxsize=1000)
def tr(t,l,s='en'): 
    if not t: return t
    return t if l=='en' or l==s else GoogleTranslator(source=s,target=l).translate(t)

def gt(k,l='en'): return TRANS.get(k,{}).get(l,TRANS[k]['en'])

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

def ex_multiple_years(t):
    years = []
    for p in [r'\b(20[1-3][0-9])\b',r"'(\d{2})\b",r'\b(\d{2})\b']:
        for m in re.finditer(p,t):
            y=m.group(1)
            year = f"20{y}" if len(y)==2 and 15<=int(y)<=30 else y if len(y)==4 else None
            if year and year not in years: years.append(year)
    return years

def ex_multiple_districts(t):
    districts=[]
    d_list=df['District'].unique().tolist()
    words=t.lower().split()
    for d in d_list:
        if d.lower() in t.lower():
            if d not in districts: districts.append(d)
    if not districts:
        for word in words:
            match=process.extractOne(word,d_list,scorer=fuzz.ratio)
            if match and match[1]>=70 and match[0] not in districts:
                districts.append(match[0])
    return districts

def det_int(t):
    lt=t.lower()
    if any(w in lt for w in ['compare','comparison','vs','versus','difference','between']):
        if any(w in lt for w in ['year','years','over time','across years']): return 'compare_years'
        if any(w in lt for w in ['district','districts','cities','regions']): return 'compare_districts'
        return 'compare_general'
    if any(w in lt for w in ['hello','hi','hey','namaste','नमस्ते','வணக்கம்','నమస్కారం','ನಮಸ್ಕಾರ']): return 'greet'
    if any(w in lt for w in ['chart','graph','plot','visuali']): return 'chart'
    if any(w in lt for w in ['language','भाषा','மொழி']): return 'lang'
    if any(w in lt for w in ['help','how to','what can']): return 'help'
    return 'data'

def qry_db(d,y):
    if not d or not y: return False,"Missing district or year"
    r=df[(df['District'].str.lower()==d.lower())&(df['Year'].astype(str)==str(y))]
    if not r.empty: return True,r.iloc[0].to_dict()
    dd=df[df['District'].str.lower()==d.lower()]
    return (False,f"No data for {d} in {y}. Available: {', '.join(dd['Year'].astype(str).tolist())}") if not dd.empty else (False,f"District '{d}' not found")

def compare_years(district,years):
    data=[]
    for year in years:
        r=df[(df['District'].str.lower()==district.lower())&(df['Year'].astype(str)==str(year))]
        if not r.empty: data.append(r.iloc[0].to_dict())
    return data

def compare_districts(districts,year):
    data=[]
    for district in districts:
        r=df[(df['District'].str.lower()==district.lower())&(df['Year'].astype(str)==str(year))]
        if not r.empty: data.append(r.iloc[0].to_dict())
    return data

def render_comparison_cards(data_list,compare_type,l):
    """Render comparison with beautiful card UI matching single data card"""
    if not data_list: return
    
    # Header
    header_text = "Year-wise Comparison" if compare_type=='years' else "District-wise Comparison"
    st.markdown(f"### 📊 {tr(header_text, l)}")
    
    # Render individual cards for each entry
    num_items = len(data_list)
    cols_per_row = 2 if num_items > 1 else 1
    
    for i in range(0, num_items, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < num_items:
                dd = data_list[i + j]
                with cols[j]:
                    # Individual card for each data point
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
    
    # Comparison insights
    st.markdown(f"#### 🔍 {tr('Comparison Insights', l)}")
    
    if compare_type == 'years' and len(data_list) > 1:
        first, last = data_list[0], data_list[-1]
        gw_change = last['Groundwater_Level_m'] - first['Groundwater_Level_m']
        
        # Trend indicator
        if gw_change < 0:
            trend_icon = "📉"
            trend_text = tr("Decreasing", l)
            trend_color = "#dc3545"
        elif gw_change > 0:
            trend_icon = "📈"
            trend_text = tr("Increasing", l)
            trend_color = "#28a745"
        else:
            trend_icon = "➡️"
            trend_text = tr("Stable", l)
            trend_color = "#ffc107"
        
        st.markdown(f"""
            <div style='background:#f8f9fa;padding:1rem;border-radius:10px;border-left:4px solid {trend_color}'>
                <strong>{trend_icon} {tr('Groundwater Trend', l)}:</strong> {trend_text}<br>
                <strong>{tr('Change', l)}:</strong> {gw_change:+.2f}m ({tr('from', l)} {first['Year']} {tr('to', l)} {last['Year']})
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"📅 {first['Year']}", f"{first['Groundwater_Level_m']}m", help="Starting level")
        with c2:
            st.metric(f"📅 {last['Year']}", f"{last['Groundwater_Level_m']}m", f"{gw_change:+.2f}m")
        with c3:
            avg_level = sum(d['Groundwater_Level_m'] for d in data_list) / len(data_list)
            st.metric("📊 Average", f"{avg_level:.2f}m", help="Average across all years")
    
    elif compare_type == 'districts' and len(data_list) > 1:
        df_compare = pd.DataFrame(data_list)
        best = df_compare.loc[df_compare['Groundwater_Level_m'].idxmax()]
        worst = df_compare.loc[df_compare['Groundwater_Level_m'].idxmin()]
        avg_level = df_compare['Groundwater_Level_m'].mean()
        
        st.markdown(f"""
            <div style='background:#f8f9fa;padding:1rem;border-radius:10px;border-left:4px solid #2d3561'>
                <strong>🏆 {tr('Highest Level', l)}:</strong> {best['District']} ({best['Groundwater_Level_m']}m)<br>
                <strong>📉 {tr('Lowest Level', l)}:</strong> {worst['District']} ({worst['Groundwater_Level_m']}m)<br>
                <strong>📊 {tr('Average', l)}:</strong> {avg_level:.2f}m
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🏆 Best", best['District'], f"{best['Groundwater_Level_m']}m")
        with c2:
            st.metric("📉 Lowest", worst['District'], f"{worst['Groundwater_Level_m']}m")
        with c3:
            st.metric("📊 Avg", f"{avg_level:.2f}m", help="Average across all districts")

def get_ctx(m=5): return st.session_state.messages[-m:] if st.session_state.messages else []

def ex_ent(cm):
    e={'districts':[],'years':[],'last_district':None,'last_year':None}
    if not cm: return e
    for m in reversed(cm):
        d,_=ex_dist(m.get('content',''),60)
        if d and d not in e['districts']:
            e['districts'].append(d)
            if not e['last_district']: e['last_district']=d
        y=ex_year(m.get('content',''))
        if y and y not in e['years']:
            e['years'].append(y)
            if not e['last_year']: e['last_year']=y
    return e

def res_ctx(p,e):
    d,_=ex_dist(p,60);y=ex_year(p);lp=p.lower()
    if not d and y and e.get('last_district'): return e['last_district'],y
    if d and not y and e.get('last_year'): return d,e['last_year']
    if not d and not y and any(w in lp for w in ['again','repeat','same','that']): return e.get('last_district'),e.get('last_year')
    return d,y

def rnd_card(dd,d,c,l):
    if c<90: st.caption(tr(f"💡 Interpreted as **{d}** ({c}% match)",l))
    header = f"Data for {dd['District']} ({dd['Year']})"
    st.markdown(f"### ✅ {tr(header, l)}")
    c1,c2=st.columns(2)
    with c1: 
        st.metric("🌊 Groundwater Level",f"{dd['Groundwater_Level_m']} m")
        st.metric("💧 Annual Recharge",f"{dd['Recharge_BCM']} BCM")
    with c2: 
        st.metric("📊 Category",dd['Category'])
        st.metric("📉 Total Extraction",f"{dd['Extraction_BCM']} BCM")

# Sidebar
with st.sidebar:
    st.markdown("""<div style='background:linear-gradient(135deg,#1a2332 0%,#2d1f33 100%);padding:1.2rem;border-radius:12px;margin-bottom:1rem;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,.15)'><h3 style='color:#fff;margin:0;font-weight:700'>🌍 Language</h3></div>""",unsafe_allow_html=True)
    sl=st.selectbox("Language",list(LANGS.keys()),format_func=lambda x:f"{LANGS[x]['flag']} {LANGS[x]['name']}",index=list(LANGS.keys()).index(st.session_state.language),label_visibility="collapsed")
    if sl!=st.session_state.language: st.session_state.language=sl;st.rerun()
    st.divider()
    if st.session_state.messages:
        st.markdown("### 📊 Session Stats")
        c1,c2=st.columns(2)
        with c1: st.metric("💬 Messages",len(st.session_state.messages))
        with c2: st.metric("❓ Queries",len([m for m in st.session_state.messages if m['role']=='user']))
        st.divider()
        with st.expander("🧠 Context Memory",expanded=False):
            ctx=get_ctx();ent=ex_ent(ctx)
            if ent['last_district']: st.info(f"📍 **Last:** {ent['last_district']}")
            if ent['last_year']: st.info(f"📅 **Year:** {ent['last_year']}")
            if not ent['last_district'] and not ent['last_year']: st.caption("No context")
    st.divider();st.caption("🔋 Deep Translator");st.caption("💡 Streamlit")

# Header
c1,c2,c3=st.columns([1,3,1])
with c2: st.markdown(f"<div style='text-align:center;padding:1.5rem 0'><h1 style='font-size:2.8rem;margin-bottom:.8rem;color:#1a2332;font-weight:800'>💧 INGRES</h1><p style='font-size:1.15rem;color:#424242;margin-bottom:0;font-weight:500'>{gt('subtitle',st.session_state.language)}</p></div>",unsafe_allow_html=True)

# Quick Actions
st.markdown("### 🎯 Quick Actions")
c1,c2,c3,c4,c5=st.columns(5)
if c1.button("📊 View Data",key="qd",use_container_width=True): st.session_state.messages.append({"role":"user","content":"Show me groundwater data for Jalandhar 2023"});st.rerun()
if c2.button("📈 Charts",key="qc",use_container_width=True): st.session_state.messages.append({"role":"user","content":"Show chart for Jalandhar"});st.rerun()
if c3.button("🔄 Compare",key="qcmp",use_container_width=True): st.session_state.messages.append({"role":"user","content":"Compare Jalandhar 2020 and 2023"});st.rerun()
if c4.button("❓ Help",key="qh",use_container_width=True): st.session_state.messages.append({"role":"user","content":"Help"});st.rerun()
if c5.button("🗑️ Clear",key="qcl",use_container_width=True): st.session_state.messages=[];st.session_state.data_cards={};st.rerun()
st.divider()

# Chat
if not st.session_state.messages:
    welcome_msg = tr("Welcome to INGRES!",st.session_state.language)
    ask_msg = tr("Ask me anything about groundwater data across Indian districts",st.session_state.language)
    try_msg = tr("Try asking questions like:",st.session_state.language)
    q1 = tr("What is the groundwater level in Jalandhar for 2023?",st.session_state.language)
    q2 = tr("Compare Jalandhar 2020 and 2023",st.session_state.language)
    q3 = tr("Compare Pune and Mumbai for 2022",st.session_state.language)
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

# Input
if p:=st.chat_input(gt('input',st.session_state.language)):
    pe=tr(p,'en',st.session_state.language) if st.session_state.language!='en' else p
    st.chat_message("user",avatar="👤").markdown(p)
    st.session_state.messages.append({"role":"user","content":p})
    cm=get_ctx();ce=ex_ent(cm)
    
    with st.chat_message("assistant",avatar="🤖"):
        with st.spinner(tr("🤔 Thinking...",st.session_state.language)):
            ad=False;r=tr("I'm not sure I understood that. Try asking about specific districts with a year!",st.session_state.language)
            it=det_int(pe)
            
            if it=='greet': r=gt('greeting',st.session_state.language)
            elif it=='lang': r=tr(f"Current: {LANGS[st.session_state.language]['name']}\n\nChange from sidebar.",st.session_state.language)
            elif it=='help': 
                help_text = """**Here's what I can help with:**

🔍 **Ask naturally:**
- 'Groundwater in Jalandhar 2023?'
- 'Show Pune 2022'

📊 **Compare data:**
- 'Compare Jalandhar 2020 and 2023'
- 'Compare Pune vs Mumbai 2022'
- 'Compare Jalandhar across 2020, 2021, 2022'

📈 **Request charts:**
- 'Show chart for Jalandhar'

💬 **Districts:** """+", ".join(df['District'].unique().tolist())
                r=tr(help_text,st.session_state.language)
            
            elif it in ['compare_years','compare_districts','compare_general']:
                districts=ex_multiple_districts(pe)
                years=ex_multiple_years(pe)
                
                if len(districts)==1 and len(years)>=2:
                    comp_data=compare_years(districts[0],years)
                    if comp_data:
                        render_comparison_cards(comp_data,'years',st.session_state.language)
                        r=tr(f"Comparison of {districts[0]} across {len(years)} years",st.session_state.language)
                        st.session_state.messages.append({"role":"assistant","content":r})
                        st.session_state.data_cards[len(st.session_state.messages)-1]={'comparison':comp_data,'compare_type':'years'}
                        ad=True
                    else: r=tr(f"Could not find data for {districts[0]} in specified years",st.session_state.language)
                
                elif len(districts)>=2 and len(years)==1:
                    comp_data=compare_districts(districts,years[0])
                    if comp_data:
                        render_comparison_cards(comp_data,'districts',st.session_state.language)
                        r=tr(f"Comparison of {len(districts)} districts in {years[0]}",st.session_state.language)
                        st.session_state.messages.append({"role":"assistant","content":r})
                        st.session_state.data_cards[len(st.session_state.messages)-1]={'comparison':comp_data,'compare_type':'districts'}
                        ad=True
                    else: r=tr(f"Could not find data for specified districts in {years[0]}",st.session_state.language)
                
                else:
                    if ce.get('last_district') and len(years)>=2:
                        comp_data=compare_years(ce['last_district'],years)
                        if comp_data:
                            render_comparison_cards(comp_data,'years',st.session_state.language)
                            r=tr(f"Comparison of {ce['last_district']} across years",st.session_state.language)
                            st.session_state.messages.append({"role":"assistant","content":r})
                            st.session_state.data_cards[len(st.session_state.messages)-1]={'comparison':comp_data,'compare_type':'years'}
                            ad=True
                    else:
                        r=tr("Please specify: 1) One district + multiple years OR 2) Multiple districts + one year\n\nExample: 'Compare Jalandhar 2020 and 2023' or 'Compare Pune vs Mumbai 2022'",st.session_state.language)
            
            elif it=='chart':
                d,c=res_ctx(pe,ce)
                if not d: d,c=ex_dist(pe,60)
                if d and d.lower()=='jalandhar':
                    r=tr(f"📈 Chart for **{d}**:",st.session_state.language);st.markdown(r)
                    try: st.image("jalandhar_chart.png")
                    except: st.info(tr("📊 Chart not found",st.session_state.language))
                    st.session_state.messages.append({"role":"assistant","content":r});ad=True
                elif d: r=tr(f"Found **{d}**, but only have Jalandhar chart. Want data?",st.session_state.language)
                else: r=tr("📈 Which district? Try: 'Show chart for Jalandhar'",st.session_state.language)
            
            elif it=='data':
                d,y=res_ctx(pe,ce)
                if not d: d,c=ex_dist(pe,60)
                else: _,c=ex_dist(d,100) if d else (None,0)
                if not y: y=ex_year(pe)
                cu=False
                if d and d==ce.get('last_district') and d.lower() not in pe.lower(): cu=True
                if y and y==ce.get('last_year') and y not in pe: cu=True
                
                if d and y:
                    s,res=qry_db(d,y)
                    if s:
                        rnd_card(res,d,c,st.session_state.language)
                        if cu: st.caption(tr("🧠 _(Used context)_",st.session_state.language))
                        rt=tr(f"Data for {res['District']} ({res['Year']})",st.session_state.language)
                        st.session_state.messages.append({"role":"assistant","content":rt})
                        st.session_state.data_cards[len(st.session_state.messages)-1]={'data':res,'district':d,'confidence':c}
                        ad=True
                    else: r=tr(f"❌ {res}",st.session_state.language)
                elif d and not y:
                    ay=df[df['District'].str.lower()==d.lower()]['Year'].astype(str).tolist()
                    if ay: r=tr(f"📍 Found **{d}**! Which year?\n\n📅 Available: {', '.join(ay)}",st.session_state.language)
                    else: r=tr("District not found",st.session_state.language)
                elif y and not d:
                    dl=", ".join(df['District'].unique().tolist()[:5])
                    sg=f"\n\n💡 Mean **{ce['last_district']}** for {y}?" if ce.get('last_district') else ""
                    r=tr(f"📅 Year **{y}**! Which district?\n\n📍 Available: {dl}...{sg}",st.session_state.language)
                else: 
                    districts_list = ", ".join(df['District'].unique().tolist())
                    r=tr(f"🤔 Couldn't identify district/year.\n\nTry: 'Jalandhar 2023' or 'Compare Jalandhar 2020 vs 2023'\n\n**Districts:** {districts_list}",st.session_state.language)
            
            if not ad: st.markdown(r);st.session_state.messages.append({"role":"assistant","content":r})
