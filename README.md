# KiranaAI 🛒🤖

## AI-Powered Supermarket Operations Agent for Indian Kirana Stores

KiranaAI is an AI-powered supermarket operations agent that allows a kirana store owner to manage day-to-day store operations through natural language on Telegram.

Instead of using multiple forms, menus, or an admin dashboard, the shopkeeper can simply chat with the AI agent to manage inventory, billing, customer credit, sales analysis, and business operations.

> **Chat is the product.**

## 🚀 Live Demo

**Telegram Bot:** @kirana_ai_sivadharani_bot

KiranaAI is deployed and accessible through Telegram.

## 🎯 Project Overview

Small retail stores commonly manage inventory, billing, customer credit, and sales records manually or across different systems.

KiranaAI provides a conversational interface where the shopkeeper can simply describe what they need.

Examples:

- Add 20 kg Basmati Rice to stock
- How much Basmati Rice is left?
- Create a bill for Ravi
- Check Ravi's khata balance
- Make a sales analysis deck for today

The AI agent understands the request, selects the appropriate business tool, executes the operation, and returns the result through Telegram.

## 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │      Shop Owner      │
                 │       Telegram       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     Telegram Bot     │
                 │  python-telegram-   │
                 │       bot            │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      AI Agent        │
                 │       Groq LLM       │
                 │   Tool Orchestration │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       ┌───────────┐  ┌───────────┐  ┌───────────┐
       │ Inventory │  │  Billing  │  │   Khata   │
       │   Tools   │  │   Tools   │  │   Tools   │
       └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                 ┌──────────────────────┐
                 │   Business Services  │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │     Repositories     │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │        SQLite        │
                 │    Source of Truth   │
                 └──────────────────────┘

             ┌─────────────────────────────┐
             │ PDF Invoice / PPTX Reports │
             └─────────────────────────────┘