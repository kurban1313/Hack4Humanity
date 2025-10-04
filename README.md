# Hack4Humanity
💧 INGRES AI Assistant

A multilingual AI-powered virtual assistant built with Streamlit, designed to help users explore and interact with groundwater data across Indian districts.
This tool supports natural language queries, fuzzy search, contextual memory, and comparisons across years/districts with a clean interactive UI.

🚀 Features
🔍 Natural Language Queries

Ask in plain English or regional languages.

Queries like:

"Groundwater in Jalandhar 2023?"

"Compare Pune vs Mumbai 2022"

🌐 Multilingual Support

Supports 12+ Indian languages (via deep-translator
):

English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Urdu.

📊 Groundwater Data Explorer

Fetches district-wise groundwater data for given years.

Provides key metrics:

🌊 Groundwater Level (m)

💧 Annual Recharge (BCM)

📉 Extraction (BCM)

📊 Category

🔄 Comparisons

Year-wise Comparison → Track trends over time for a single district.

District-wise Comparison → Compare multiple districts in the same year.

Insights with highlights of best/worst/average.

📈 Visualizations

Chart rendering (demo chart for Jalandhar included).

🤖 AI Assistant Capabilities

Contextual memory: remembers last district/year if missing in query.

Fuzzy matching: understands misspelled district names.

Quick Actions: Buttons for fast queries (View data, Compare, Charts, Help).

🛠️ Tech Stack

Streamlit
 → UI & app framework.

Pandas
 → Data handling.

FuzzyWuzzy
 → Fuzzy district matching.

Deep Translator
 → Language translation.

Regex
 → Year & entity extraction.

LRU Cache
 → Optimized translation & lookups.

📂 Repository Structure
📦 ingres-ai-assistant
 ┣ 📜 app.py                # Main Streamlit app
 ┣ 📜 sample_data.csv       # Demo groundwater dataset
 ┣ 📜 jalandhar_chart.png   # Example visualization
 ┣ 📜 requirements.txt      # Python dependencies
 ┣ 📜 README.md             # Documentation

⚡ Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/ingres-ai-assistant.git
cd ingres-ai-assistant

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Run App
streamlit run app.py

📊 Data

The demo uses sample_data.csv with columns:

District	Year	Groundwater_Level_m	Recharge_BCM	Extraction_BCM	Category
Jalandhar	2023	23.5	12.4	8.9	Safe

👉 Replace this file with real groundwater datasets (e.g., from CGWB India reports).

🌍 Multilingual Support
Code	Language	Flag
en	English	🇬🇧
hi	हिन्दी	🇮🇳
ta	தமிழ்	🇮🇳
te	తెలుగు	🇮🇳
kn	ಕನ್ನಡ	🇮🇳
ml	മലയാളം	🇮🇳
mr	मराठी	🇮🇳
gu	ગુજરાતી	🇮🇳
bn	বাংলা	🇮🇳
pa	ਪੰਜਾਬੀ	🇮🇳
or	ଓଡ଼ିଆ	🇮🇳
ur	اردو	🇮🇳
📌 Usage Examples

Single Query

Input: "Groundwater in Pune 2022"

Output: Metrics card with groundwater level, recharge, extraction.

Comparison Across Years

Input: "Compare Jalandhar 2020 and 2023"

Output: Year-wise comparison cards + trend insights.

Comparison Across Districts

Input: "Compare Pune vs Mumbai 2022"

Output: District-wise comparison with highest/lowest/average levels.

🧩 Future Enhancements

✅ Support for interactive charts (line/bar/heatmaps).

✅ Integration with real-time government datasets.

✅ Export results to PDF/Excel.

✅ Voice-based query support.

🙏 Acknowledgments

This project leverages several open-source libraries:

Streamlit

Pandas

FuzzyWuzzy

Deep Translator

And inspired by groundwater datasets from Central Ground Water Board (CGWB), India.

📜 License

This project is licensed under the MIT License – feel free to use, modify, and share!
