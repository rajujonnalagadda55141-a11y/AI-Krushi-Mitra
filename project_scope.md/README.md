# GenAI Farming Assistant

An AI-powered agriculture assistant that uses **Generative AI** to help farmers with:

- Crop advice
- Fertilizer guidance
- Pest & disease support
- Weather-based farming suggestions

This project aims to make expert farming knowledge accessible through a simple chat-based interface.

---

## Project Type

**Generative AI Application**

This system uses a **Large Language Model (LLM)** to generate natural language responses for farmer queries instead of relying on fixed rules.

---

## Problem Statement

Farmers often face challenges in getting:

- Timely crop guidance
- Correct fertilizer usage
- Early pest and disease identification
- Actionable advice based on weather

This project solves these problems by providing a **smart AI assistant** that gives reliable and easy-to-understand recommendations.

---

## Supported Crops (Phase 1)

- Rice
- Cotton
- Maize
- Chilli

---

## Key Features

- 🤖 **AI Chat Assistant** for farming queries
- 🌾 **Crop Advice** – best practices for cultivation
- 🧪 **Fertilizer Guidance** – dosage and timing
- 🐛 **Pest & Disease Q&A** – symptoms to solutions
- ☁️ **Weather-Based Suggestions** – smarter decisions

---

## 🏗️ System Architecture

User → Web Interface → Backend API → Prompt Engine → LLM → AI Response
↓
Knowledge Base

### 🔹 Components Explanation

- **Web Interface**  
  Simple chat screen where farmers ask questions.

- **Backend API**  
  Handles user requests and sends them to the AI model.

- **Prompt Builder**  
  Formats the farmer’s question with instructions so the AI gives accurate agricultural advice.

- **LLM (Large Language Model)**  
  Generates human-like answers for crop, fertilizer, pest, and weather queries.

- **Knowledge Base**  
  Stores structured farming data used to improve response accuracy.

---

### 🔹 Data Flow

1. Farmer types a question
2. Request goes to backend
3. Backend builds a smart prompt
4. Prompt is sent to the LLM
5. LLM generates advice
6. Response is shown to the farmer

---

## 🛠️ Tech Stack

- **Backend:** Python (FastAPI)
- **Frontend:** HTML, CSS, JavaScript
- **AI Model:** LLM (Ollama / OpenAI / Llama)
- **Data:** Structured agriculture knowledge base
- **Version Control:** Git & GitHub

---

## ⚙️ How to Run the Project

### 1️⃣ Clone the repository

```bash
git clone <https://github.com//ai-krushi-mitra.git>
cd AI-Krushi-Mitra
```
