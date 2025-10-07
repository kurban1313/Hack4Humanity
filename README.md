# 💧 INGRES AI Assistant

<div align="center">

![INGRES AI](https://img.shields.io/badge/INGRES-AI%20Assistant-2d3561?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)
![DeepSeek](https://img.shields.io/badge/DeepSeek-AI-00A67E?style=for-the-badge)

**Smart AI Assistant for Groundwater Data Analysis**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [License](#-license)

</div>

---

## 📖 Overview

INGRES AI Assistant is an intelligent chatbot powered by **DeepSeek AI** that helps analyze groundwater data across Indian districts. It features context-aware conversations, multi-language support (12 Indian languages), and advanced district/year comparison capabilities.

### ✨ Key Highlights

- 🤖 **AI-Powered**: Uses DeepSeek Chat v3.1 for natural language understanding
- 🌍 **Multi-Language**: Supports Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Urdu
- 📊 **Smart Comparisons**: Compare multiple districts or track time series data
- 🧠 **Context-Aware**: Remembers previous queries for seamless conversations
- 📈 **Data Visualization**: Beautiful cards and comparison tables
- ⚡ **Fast & Responsive**: Cached translations and optimized queries

## 🎯 Features

### Core Capabilities

✅ **Single District Query**: Get detailed data for any district and year  
✅ **District Comparison**: Compare 2+ districts for the same year  
✅ **Time Series Analysis**: Track changes across multiple years  
✅ **Context Memory**: Follow-up questions without repeating context  
✅ **Year Normalization**: Automatically handles "23" → "2023"  
✅ **Fuzzy Matching**: Understands misspelled district names  
✅ **Real-time Translation**: 12 Indian languages supported  
✅ **Error Handling**: Graceful failures with helpful messages

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- OpenRouter API key ([Get it here](https://openrouter.ai/keys))

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/kurban1313/Hack4Humanity.git 
cd Hack4Humanity
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up API Key

**Option A: Using secrets.toml (Recommended)**

```bash
# Create .streamlit folder
mkdir .streamlit

# Create secrets file
# Copy secrets.toml.template to .streamlit/secrets.toml
cp secrets.toml.template .streamlit/secrets.toml

# Edit .streamlit/secrets.toml and add your API key:
# OPENROUTER_API_KEY = "your-actual-key-here"
```

**Option B: Using Environment Variable**

```bash
# Windows
set OPENROUTER_API_KEY=your-api-key-here

# macOS/Linux
export OPENROUTER_API_KEY=your-api-key-here
```

#### 5. Run the App

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser 🎉

## 📊 Data Format

Your `sample_data.csv` should have these columns:

| Column | Type | Description |
|--------|------|-------------|
| `District` | string | District name (e.g., "Jalandhar") |
| `Year` | int | Year (e.g., 2023) |
| `Groundwater_Level_m` | float | Water level in meters |
| `Recharge_BCM` | float | Recharge in BCM |
| `Extraction_BCM` | float | Extraction in BCM |
| `Category` | string | Safe/Semi-Critical/Critical/Over-Exploited |

**Example:**

```csv
District,Year,Groundwater_Level_m,Recharge_BCM,Extraction_BCM,Category
Jalandhar,2023,10.9,2.1,2.1,Semi-Critical
Pune,2023,7.2,2.8,3.3,Critical
```

## 💬 Usage Examples

### Basic Queries

```
💬 "Show me Jalandhar 23"
💬 "What's the groundwater level in Pune for 2022?"
💬 "Give me data for Mumbai 2023"
```

### District Comparison

```
💬 "Compare Pune and Mumbai for 2022"
💬 "Show Delhi vs Bangalore for 23"
💬 "Compare Jalandhar, Ludhiana, and Amritsar for 2023"
```

### Time Series Analysis

```
💬 "Show Delhi 2020, 2021, 2022, 2023"
💬 "Compare Jalandhar across 20, 21, 22"
💬 "Time series for Pune from 2020 to 2023"
```

### Context-Aware Queries

```
User: "Show me Jalandhar 2023"
AI: [Shows data]

User: "What about 2022?"
AI: [Shows Jalandhar 2022 automatically]

User: "Compare with Pune"
AI: [Compares Pune and Jalandhar for 2022]
```

## 🌍 Supported Languages

| Language | Code | Native Name |
|----------|------|-------------|
| English | `en` | English |
| Hindi | `hi` | हिन्दी |
| Tamil | `ta` | தமிழ் |
| Telugu | `te` | తెలుగు |
| Kannada | `kn` | ಕನ್ನಡ |
| Malayalam | `ml` | മലയാളം |
| Marathi | `mr` | मराठी |
| Gujarati | `gu` | ગુજરાતી |
| Bengali | `bn` | বাংলা |
| Punjabi | `pa` | ਪੰਜਾਬੀ |
| Odia | `or` | ଓଡ଼ିଆ |
| Urdu | `ur` | اردو |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key | ✅ Yes |

### Customization Options

**Change AI Model:**
Edit line ~390 in `app.py`:
```python
model="deepseek/deepseek-chat-v3.1:free"
# Change to any OpenRouter model
```

**Modify Colors:**
Search for `#2d3561` in CSS section to change theme colors.

**Add More Languages:**
Update the `LANGS` dictionary in `app.py`.

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.39
- **AI Model**: DeepSeek Chat v3.1 (via OpenRouter)
- **Translation**: Google Translate (deep-translator)
- **Data Processing**: Pandas
- **Fuzzy Matching**: FuzzyWuzzy
- **API Client**: OpenAI Python SDK

## 📁 Project Structure

```
ingres-ai-assistant/
├── app.py                      # Main application (725 lines, fully fixed)
├── sample_data.csv             # Sample groundwater data
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
├── secrets.toml.template       # API key template
└── .streamlit/
    └── secrets.toml           # API keys (create this, not in git)
```

## 🐛 Troubleshooting

### Common Issues

**Issue: "OPENROUTER_API_KEY not found"**  
✅ Solution: Create `.streamlit/secrets.toml` or set environment variable

**Issue: "sample_data.csv not found"**  
✅ Solution: Ensure CSV is in root directory with correct column names

**Issue: "Translation error"**  
✅ Solution: Check internet connection (Google Translate requires it)

**Issue: Chat not updating after sending message**  
✅ Solution: This is fixed! The new code includes `st.rerun()` at line 700

**Issue: "ModuleNotFoundError"**  
✅ Solution: Run `pip install -r requirements.txt`

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Add secret: `OPENROUTER_API_KEY = "your-key"`
6. Click "Deploy"

### Deploy to Other Platforms

- **Heroku**: Add `Procfile` with `web: streamlit run app.py`
- **Railway**: Works out of the box
- **Render**: Add build command `pip install -r requirements.txt`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Amazing web framework
- [OpenRouter](https://openrouter.ai/) - AI model access
- [DeepSeek](https://www.deepseek.com/) - Powerful AI model
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Translation library

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ingres-ai-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ingres-ai-assistant/discussions)
- **Email**: your-email@example.com

## 🎯 Roadmap

- [ ] Add data visualization charts
- [ ] Export data to PDF/Excel
- [ ] Real-time data integration
- [ ] User authentication
- [ ] Historical trend predictions
- [ ] Mobile app version

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/ingres-ai-assistant?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/ingres-ai-assistant?style=social)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

<div align="center">

Made with ❤️ for Groundwater Management in India

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/yourusername/ingres-ai-assistant/issues) • [Request Feature](https://github.com/yourusername/ingres-ai-assistant/issues)

</div>
