# FinTrend Pro: Advanced Market Analyzer

A sophisticated, AI-powered financial analysis platform built with Streamlit, designed specifically for analyzing Indian stock market trends, technical indicators, and market sentiment.

## 🚀 Features

### 📊 **Comprehensive Stock Analysis**
- **Real-time Price Data**: Fetch live stock prices and historical data using Yahoo Finance
- **Interactive Candlestick Charts**: Professional-grade price visualization with Plotly
- **Technical Indicators**: RSI, MACD, and Bollinger Bands calculations
- **Multi-timeframe Analysis**: Support for 1 month to 5 years of historical data

### 🤖 **AI-Powered Sentiment Analysis**
- **News Integration**: Automatic fetching of latest news articles for selected stocks
- **Sentiment Scoring**: Advanced NLP analysis using NLTK VADER sentiment analyzer
- **Market Mood Detection**: Bullish/Bearish/Neutral sentiment classification
- **AI Market Summary**: Intelligent summarization of market sentiment and price movements

### 🔮 **Machine Learning Forecasting**
- **3-Day Price Prediction**: Holt-Winters Exponential Smoothing model
- **Trend Analysis**: Automated forecasting based on historical patterns
- **Visual Predictions**: Interactive forecast charts with historical context

### ⚔️ **Stock Comparison Tools**
- **Multi-stock Comparison**: Compare performance of multiple stocks simultaneously
- **Normalized Returns**: Percentage-based growth comparison over selected periods
- **Competitor Analysis**: Easy selection from NIFTY 50 companies

### 💼 **Personal Portfolio Tracker**
- **Mock Portfolio**: Track hypothetical investments without real money
- **Performance Metrics**: Real-time P&L calculations and return percentages
- **Asset Management**: Add/remove stocks with custom quantities and buy prices

### 🎨 **Premium User Experience**
- **Glassmorphism Design**: Modern, professional UI with backdrop blur effects
- **Dark Theme**: Eye-friendly dark mode optimized for extended use
- **Responsive Layout**: Works seamlessly across different screen sizes
- **Interactive Elements**: Hover effects and smooth animations

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Financial Data**: Yahoo Finance (yfinance)
- **Sentiment Analysis**: NLTK VADER
- **Time Series Forecasting**: Statsmodels
- **Machine Learning**: Scikit-learn

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/fintrend-pro.git
   cd fintrend-pro
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Access the app**:
   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage

### Getting Started
1. Select an Indian stock from the dropdown menu in the sidebar
2. Choose your desired time period (1 month to 5 years)
3. Explore the different analysis tabs

### Key Features Guide

#### Overview & Sentiment Tab
- View current price, price change, and overall market sentiment
- Read AI-generated market summaries
- Browse recent news articles with sentiment badges
- Analyze price movements with interactive candlestick charts

#### Technical Analysis Tab
- Study RSI (Relative Strength Index) for overbought/oversold conditions
- Analyze MACD (Moving Average Convergence Divergence) signals
- Monitor Bollinger Bands for volatility and trend analysis

#### AI Forecast Tab
- View 3-day price predictions using machine learning
- Understand forecast accuracy and historical context
- Make informed trading decisions based on trend analysis

#### Compare Stocks Tab
- Select multiple competitors for comparison
- View normalized percentage returns over time
- Identify relative performance and market leaders

#### My Portfolio Tab
- Build a mock portfolio with hypothetical investments
- Track real-time performance and profit/loss
- Calculate returns and manage your virtual assets

## 🔧 Configuration

### Supported Stocks
The application includes pre-configured NIFTY 50 stocks plus custom ticker support. You can:
- Select from popular Indian companies
- Enter custom NSE tickers (e.g., ZOMATO.NS)
- Add international stocks if supported by Yahoo Finance

### Customization Options
- **Time Periods**: 1mo, 3mo, 6mo, 1y, 2y, 5y
- **Technical Indicators**: Configurable parameters for RSI, MACD, Bollinger Bands
- **Forecast Horizon**: Adjustable prediction periods

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing financial data
- **NLTK** for natural language processing capabilities
- **Streamlit** for the amazing web app framework
- **Plotly** for interactive data visualizations

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/fintrend-pro/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🔄 Future Enhancements

- [ ] Advanced ML models (LSTM, ARIMA) for better forecasting
- [ ] Real-time data streaming
- [ ] Portfolio optimization algorithms
- [ ] Risk analysis and volatility metrics
- [ ] Mobile app version
- [ ] Integration with trading platforms

---

**Made with ❤️ for the Indian stock market community**</content>
<parameter name="filePath">c:\Users\Admin\Desktop\finance_analyzer\README.md
