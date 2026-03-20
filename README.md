# 🚀 Event-Based Intelligent Trading System (Nifty Next 50)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch)
![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Transformers-yellow?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)

**A high-frequency-capable algorithmic trading engine that fuses State-of-the-Art NLP (FinBERT) with Technical Analysis to trade the Indian Equity Markets.**

[View Dashboard](#-dashboard-preview) • [Key Differentiators](#-what-makes-this-extraordinary) • [Challenges Solved](#-challenges--engineering-hurdles)

</div>

---

## 📖 Overview

Most retail trading bots rely solely on technical indicators (RSI, MACD), which are *lagging* in nature. They react after the move has happened. 

**This Event-Based Trading System is different.** It attempts to be *predictive* by analyzing the root cause of price movements: **News & Events**. By processing real-time news headlines using **FinBERT** (a BERT model fine-tuned on financial text) and validating signals with technical order flow, this system aims to capture alpha that purely technical bots miss.

## 🌟 What Makes This Extraordinary?

This isn't just a `if rsi < 30 buy` script. It's a multi-modal decision engine:

1.  **Hybrid "Sentimental-Technical" core:**
    *   **The Problem:** News bots buy into "bull traps" (good news but bad trend). Technical bots buy "falling knives" (oversold but bad news).
    *   **The Solution:** This system requires a **Double Confirmation**:
        *   ✅ **NLP Layer:** News Sentiment must be Positive (Confidence > 0.9).
        *   ✅ **Technical Layer:** RSI < 30 (Oversold) AND Volume Shock (> 1.5x avg).
    *   This drastically reduces false positives compared to single-strategy bots.

2.  **Institutional-Grade Volatility Filtering:**
    *   Includes a **"No-Trade Zone" (9:15 AM - 9:30 AM)** to avoid the initial market opening chaos.
    *   Implements **ATR-based (Average True Range) Dynamic Stop Losses**, adapting risk based on the stock's current volatility rather than a fixed percentage.

3.  **Local LLM Inference:**
    *   Instead of paying for expensive API calls to services like Bloomberg or paying per-character for GPT-4, this system runs **FinBERT locally**. This ensures:
        *   **Zero Latency:** No network roundtrips for sentiment scoring.
        *   **Data Privacy:** Trading strategies remain on your machine.
        *   **Cost Efficiency:** $0 recurring AI costs.

4.  **Auto-Risk Management:**
    *   Hard-coded **Intraday Square-off (3:20 PM)** ensures no overnight risk.
    *   **Position Sizing Limits** prevent over-exposure to a single ticker.

## 🛠️ Challenges & Engineering Hurdles

Building this system involved solving several complex engineering problems:

### 1. The "Signal Race" Condition
*   **Challenge:** Processing 50+ tickers worth of news headlines with a Transformer model is computationally heavy. Doing this synchronously with 15-minute candle data fetching caused the bot to lag behind the market.
*   **Solution:** We optimized the architecture to cache model weights and implemented a streamlined inference pipeline. (Future roadmap includes moving NLP to a separate async microservice).

### 2. Differentiating "Noise" from "Signal" in Low Cap Stocks
*   **Challenge:** The Nifty Next 50 contains volatile stocks where low liquidity can look like a "Volume Shock".
*   **Solution:** We implemented a **Moving Average Volume filter**. The current volume must not just be high, it must be `1.5x` the 20-period average volume to trigger a signal.

### 3. Financial Sentiment Nuance
*   **Challenge:** Standard NLP models (VADER, TextBlob) fail at financial context.
    *   *Example:* "Losses narrowed by 50%" -> Standard NLP sees "Loss" and tags Negative.
*   **Solution:** Integration of **ProsusAI/FinBERT**, which understands that "narrowing losses" is actually a **Positive** event for a stock.

## 📊 Dashboard Preview

The system includes a **Streamlit** dashboard for real-time monitoring of trades and signals.

<img width="100%" alt="image" src="https://github.com/user-attachments/assets/f4a68549-fc6f-4a7b-bb58-a9ed039a21d3" />

## ⚡ Tech Stack

*   **Core Engine:** Python 3.10
*   **NLP/AI:** Hugging Face `transformers`, `torch`, `FinBERT`
*   **Data Source:** `yfinance` (NSE/BSE Data)
*   **Analysis:** `pandas`, `numpy`, `ta-lib` logic
*   **Visualization:** `streamlit`

## 🏃‍♂️ How to Run

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Trader:**
    ```bash
    python src/live_trader.py
    ```

3.  **Launch Dashboard:**
    ```bash
    streamlit run src/dashboard.py
    ```

---
*Disclaimer: This project is for educational purposes only. Algorithmic trading involves significant financial risk.*
