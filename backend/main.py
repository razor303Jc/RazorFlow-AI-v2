"""
RazorFlow AI - FastAPI Backend
Deployed on Railway with PostgreSQL
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
from typing import Dict, List
import json

# Initialize FastAPI app
app = FastAPI(
    title="RazorFlow AI Backend",
    description="Business Automation Platform with AI Assistants",
    version="2.0.0"
)

# CORS middleware for GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://razor303jc.github.io",
        "https://razorflow-ai.github.io", 
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data for demo
finance_data = {
    "revenue": 125000,
    "expenses": 75000,
    "profit": 50000,
    "growth": 15.5
}

sales_data = {
    "leads": 234,
    "conversions": 45,
    "pipeline_value": 500000,
    "close_rate": 19.2
}

scheduler_data = {
    "meetings_today": 8,
    "availability": "60%",
    "next_meeting": "2:30 PM - Client Demo",
    "optimization_score": 85
}

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "RazorFlow AI Backend API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "finance": "/api/finance",
            "sales": "/api/sales", 
            "scheduler": "/api/scheduler",
            "chat": "/api/chat/{bot_type}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/finance")
async def get_finance_dashboard():
    """Finance Bot - Dashboard data"""
    return {
        "bot": "Finance AI",
        "data": finance_data,
        "insights": [
            "Revenue up 15.5% from last month",
            "Operating expenses within budget",
            "Recommend increasing marketing spend",
            "Cash flow positive for 6 consecutive months"
        ],
        "recommendations": [
            "Diversify revenue streams",
            "Optimize operational costs", 
            "Consider expansion opportunities"
        ]
    }

@app.get("/api/sales")
async def get_sales_dashboard():
    """Sales Bot - Dashboard data"""
    return {
        "bot": "Sales AI",
        "data": sales_data,
        "insights": [
            "Lead quality improved by 23%",
            "Conversion rate above industry average",
            "Q4 pipeline looking strong",
            "Top performer: Enterprise segment"
        ],
        "recommendations": [
            "Focus on enterprise clients",
            "Automate follow-up sequences",
            "Expand into new markets"
        ]
    }

@app.get("/api/scheduler")
async def get_scheduler_dashboard():
    """Smart Scheduler - Dashboard data"""
    return {
        "bot": "Scheduler AI",
        "data": scheduler_data,
        "insights": [
            "Calendar optimization at 85%",
            "Average meeting duration: 32 minutes",
            "Best productivity hours: 9-11 AM",
            "Reduced scheduling conflicts by 40%"
        ],
        "recommendations": [
            "Block focus time in mornings",
            "Batch similar meeting types",
            "Add buffer time between meetings"
        ]
    }

@app.post("/api/chat/{bot_type}")
async def chat_with_bot(bot_type: str, message: dict):
    """Chat interface for AI bots"""
    user_message = message.get("message", "")
    
    if bot_type == "finance":
        response = f"Finance Bot: Analyzing your query about '{user_message}'. Based on current data, your revenue is trending upward. I recommend reviewing Q4 projections."
    elif bot_type == "sales":
        response = f"Sales Bot: Regarding '{user_message}' - Your pipeline shows strong potential. I suggest focusing on enterprise leads for higher conversion rates."
    elif bot_type == "scheduler":
        response = f"Scheduler Bot: For '{user_message}' - I can optimize your calendar. Your current availability is 60%. Shall I suggest better time blocks?"
    else:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {
        "bot": f"{bot_type.title()} AI",
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.95
    }

@app.get("/api/analytics")
async def get_analytics():
    """Combined analytics from all bots"""
    return {
        "overview": {
            "total_revenue": finance_data["revenue"],
            "active_leads": sales_data["leads"],
            "meetings_scheduled": scheduler_data["meetings_today"],
            "overall_efficiency": 87.5
        },
        "performance": {
            "finance_score": 92,
            "sales_score": 88,
            "scheduling_score": 85
        },
        "trends": {
            "revenue_growth": "+15.5%",
            "lead_conversion": "+12.3%",
            "time_optimization": "+8.7%"
        }
    }

if __name__ == "__main__":
    # For Railway deployment
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
