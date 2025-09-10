"""
RazorFlow AI - FastAPI Backend
Deployed on Railway with PostgreSQL
Enhanced with comprehensive logging and error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import sys
from datetime import datetime
from typing import Dict, List
import json
import traceback
import asyncio
import signal
import psutil


# Configure comprehensive logging
def setup_logging():
    """Configure logging with file and console output"""
    log_level = (
        logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

    # Create logs directory if it doesn't exist
    log_dir = "/app/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    # Add file handler if possible
    try:
        file_handler = logging.FileHandler(f"{log_dir}/razorflow_backend.log")
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")

    logging.basicConfig(level=log_level, format=log_format, handlers=handlers)

    return logging.getLogger("razorflow-ai")


logger = setup_logging()


# Enhanced startup checks
async def check_dependencies():
    """Check all external dependencies on startup"""
    logger.info("🔍 Checking dependencies...")

    dependencies_status = {"database": False, "redis": False, "chromadb": False}

    # Check PostgreSQL connection
    try:
        import psycopg2

        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conn = psycopg2.connect(database_url)
            conn.close()
            dependencies_status["database"] = True
            logger.info("✅ PostgreSQL connection successful")
        else:
            logger.warning("⚠️ DATABASE_URL not configured")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")

    # Check Redis connection
    try:
        import redis

        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            r = redis.from_url(redis_url)
            r.ping()
            dependencies_status["redis"] = True
            logger.info("✅ Redis connection successful")
        else:
            logger.warning("⚠️ REDIS_URL not configured")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")

    # Check ChromaDB connection
    try:
        import requests

        chroma_url = os.getenv("CHROMA_URL", "http://chromadb:8000")
        response = requests.get(f"{chroma_url}/api/v1", timeout=5)
        if response.status_code < 500:
            dependencies_status["chromadb"] = True
            logger.info("✅ ChromaDB connection successful")
    except Exception as e:
        logger.error(f"❌ ChromaDB connection failed: {e}")

    return dependencies_status


# Log startup information
logger.info("🚀 Starting RazorFlow AI Backend")
logger.info(f"Python version: {sys.version}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
logger.info(f"Debug mode: {os.getenv('DEBUG', 'false')}")
logger.info(f"Log level: {logger.level}")
logger.info(f"Process ID: {os.getpid()}")
logger.info(f"Working directory: {os.getcwd()}")

# Log system information
try:
    memory = psutil.virtual_memory()
    logger.info(
        f"System memory: {memory.total // 1024 // 1024}MB total, {memory.available // 1024 // 1024}MB available"
    )
    logger.info(f"CPU count: {psutil.cpu_count()}")
except:
    logger.warning("Could not get system information")

# Initialize FastAPI app
app = FastAPI(
    title="RazorFlow AI Backend",
    description="Business Automation Platform with AI Assistants",
    version="2.0.0",
)


# Enhanced error handling middleware
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    try:
        logger.debug(f"Processing request: {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": (
                    str(e)
                    if os.getenv("DEBUG", "false").lower() == "true"
                    else "An error occurred"
                ),
                "timestamp": datetime.now().isoformat(),
            },
        )


# CORS middleware configuration with enhanced logging
try:
    # Temporarily allow all origins for debugging
    cors_origins = ["*"]  # Allow all origins for debugging
    logger.info(f"CORS origins configured: {cors_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware configured successfully")
except Exception as e:
    logger.error(f"❌ Failed to configure CORS: {str(e)}")
    raise


# Application startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("🚀 Application startup initiated")

    try:
        # Check all dependencies
        dependencies = await check_dependencies()

        # Log dependency status
        for service, status in dependencies.items():
            status_emoji = "✅" if status else "❌"
            logger.info(
                f"{status_emoji} {service.title()}: {'Connected' if status else 'Failed'}"
            )

        # Log environment configuration
        logger.info("📋 Environment Configuration:")
        env_vars = [
            "ENVIRONMENT",
            "DEBUG",
            "PORT",
            "LOG_LEVEL",
            "DATABASE_URL",
            "REDIS_URL",
            "CHROMA_URL",
        ]

        for var in env_vars:
            value = os.getenv(var, "Not Set")
            # Mask sensitive information
            if "URL" in var and value != "Not Set":
                if "://" in value:
                    masked_value = value.split("://")[0] + "://***masked***"
                else:
                    masked_value = "***masked***"
                logger.info(f"  {var}: {masked_value}")
            else:
                logger.info(f"  {var}: {value}")

        logger.info("✅ Application startup completed successfully")

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger.info("🛑 Application shutdown initiated")

    try:
        # Add any cleanup logic here
        logger.info("🧹 Performing cleanup tasks...")

        # Log final statistics
        try:
            memory = psutil.virtual_memory()
            logger.info(f"Final memory usage: {memory.percent}%")
        except:
            pass

        logger.info("✅ Application shutdown completed")

    except Exception as e:
        logger.error(f"❌ Shutdown error: {str(e)}")


# Sample data for demo
finance_data = {"revenue": 125000, "expenses": 75000, "profit": 50000, "growth": 15.5}

sales_data = {
    "leads": 234,
    "conversions": 45,
    "pipeline_value": 500000,
    "close_rate": 19.2,
}

scheduler_data = {
    "meetings_today": 8,
    "availability": "60%",
    "next_meeting": "2:30 PM - Client Demo",
    "optimization_score": 85,
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
            "chat": "/api/chat/{bot_type}",
        },
    }


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with detailed diagnostics"""
    try:
        start_time = datetime.now()

        # Basic health status
        health_status = {
            "status": "healthy",
            "timestamp": start_time.isoformat(),
            "version": "2.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        }

        # Check dependencies if in debug mode
        if os.getenv("DEBUG", "false").lower() == "true":
            try:
                dependencies = await check_dependencies()
                health_status["dependencies"] = dependencies

                # System information
                try:
                    memory = psutil.virtual_memory()
                    health_status["system"] = {
                        "memory_percent": memory.percent,
                        "memory_available_mb": memory.available // 1024 // 1024,
                        "cpu_count": psutil.cpu_count(),
                        "process_id": os.getpid(),
                    }
                except Exception:
                    health_status["system"] = "unavailable"

            except Exception as e:
                health_status["dependencies_error"] = str(e)

        # Calculate response time
        end_time = datetime.now()
        health_status["response_time_ms"] = int(
            (end_time - start_time).total_seconds() * 1000
        )

        logger.debug(f"Health check completed in {health_status['response_time_ms']}ms")
        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@app.get("/debug")
async def debug_info():
    """Debug endpoint - only available in debug mode"""
    if not os.getenv("DEBUG", "false").lower() == "true":
        raise HTTPException(status_code=404, detail="Not found")

    try:
        # Comprehensive debug information
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "process_info": {
                "pid": os.getpid(),
                "working_directory": os.getcwd(),
                "python_version": sys.version,
                "python_executable": sys.executable,
            },
            "environment_variables": {
                key: value
                for key, value in os.environ.items()
                if key.startswith(
                    (
                        "RAZORFLOW",
                        "DATABASE",
                        "REDIS",
                        "CHROMA",
                        "DEBUG",
                        "LOG",
                        "PORT",
                        "CORS",
                    )
                )
            },
            "dependencies": await check_dependencies(),
        }

        # System information if available
        try:
            memory = psutil.virtual_memory()
            debug_data["system"] = {
                "memory": {
                    "total_mb": memory.total // 1024 // 1024,
                    "available_mb": memory.available // 1024 // 1024,
                    "percent_used": memory.percent,
                },
                "cpu_count": psutil.cpu_count(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            }
        except Exception as e:
            debug_data["system_error"] = str(e)

        return debug_data

    except Exception as e:
        logger.error(f"Debug endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")


@app.get("/logs")
async def get_recent_logs():
    """Get recent application logs - only available in debug mode"""
    if not os.getenv("DEBUG", "false").lower() == "true":
        raise HTTPException(status_code=404, detail="Not found")

    try:
        log_file = "/app/logs/razorflow_backend.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
                # Return last 50 lines
                recent_logs = lines[-50:] if len(lines) > 50 else lines
                return {
                    "log_file": log_file,
                    "total_lines": len(lines),
                    "recent_lines": len(recent_logs),
                    "logs": [line.strip() for line in recent_logs],
                }
        else:
            return {"message": "Log file not found", "log_file": log_file}
    except Exception as e:
        logger.error(f"Failed to read logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


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
            "Cash flow positive for 6 consecutive months",
        ],
        "recommendations": [
            "Diversify revenue streams",
            "Optimize operational costs",
            "Consider expansion opportunities",
        ],
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
            "Top performer: Enterprise segment",
        ],
        "recommendations": [
            "Focus on enterprise clients",
            "Automate follow-up sequences",
            "Expand into new markets",
        ],
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
            "Reduced scheduling conflicts by 40%",
        ],
        "recommendations": [
            "Block focus time in mornings",
            "Batch similar meeting types",
            "Add buffer time between meetings",
        ],
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
        "confidence": 0.95,
    }


@app.get("/api/analytics")
async def get_analytics():
    """Combined analytics from all bots"""
    return {
        "overview": {
            "total_revenue": finance_data["revenue"],
            "active_leads": sales_data["leads"],
            "meetings_scheduled": scheduler_data["meetings_today"],
            "overall_efficiency": 87.5,
        },
        "performance": {"finance_score": 92, "sales_score": 88, "scheduling_score": 85},
        "trends": {
            "revenue_growth": "+15.5%",
            "lead_conversion": "+12.3%",
            "time_optimization": "+8.7%",
        },
    }


# Portfolio and Services Endpoints
@app.get("/api/portfolio/stats")
async def get_portfolio_stats():
    """Get portfolio statistics for the freelancer showcase"""
    logger.info("Fetching portfolio statistics")
    return {
        "projects_completed": 156,
        "active_systems": 47,
        "client_satisfaction": 99.2,
        "uptime_guarantee": 99.9,
        "ai_models_deployed": 89,
        "languages_supported": 12,
        "integrations_completed": 234,
        "years_experience": 5,
        "certifications": [
            "AWS Machine Learning Specialty",
            "Google Cloud AI/ML Engineer",
            "Microsoft Azure AI Engineer",
            "Certified Kubernetes Application Developer",
        ],
        "technologies": [
            "Python",
            "FastAPI",
            "React",
            "Docker",
            "Kubernetes",
            "TensorFlow",
            "PyTorch",
            "OpenAI",
            "Anthropic",
            "PostgreSQL",
            "Redis",
            "ChromaDB",
            "AWS",
            "GCP",
            "Azure",
        ],
    }


@app.get("/api/services/capabilities")
async def get_service_capabilities():
    """Get detailed service capabilities"""
    logger.info("Fetching service capabilities")
    return {
        "ai_chatbots": {
            "description": "Custom AI chatbots for customer service, sales, and support",
            "technologies": [
                "OpenAI GPT",
                "Anthropic Claude",
                "Custom Fine-tuned Models",
            ],
            "features": [
                "24/7 Customer Support",
                "Multi-language Support",
                "Custom Training on Your Data",
                "Integration with CRM/ERP Systems",
                "Real-time Analytics",
                "Voice & Text Support",
            ],
            "recent_projects": [
                {
                    "name": "E-commerce Support Bot",
                    "industry": "Retail",
                    "improvement": "40% reduction in support tickets",
                },
                {
                    "name": "Lead Qualification Assistant",
                    "industry": "SaaS",
                    "improvement": "60% increase in qualified leads",
                },
                {
                    "name": "Medical Appointment Bot",
                    "industry": "Healthcare",
                    "improvement": "80% automation of appointment scheduling",
                },
            ],
        },
        "automation_systems": {
            "description": "End-to-end business process automation",
            "technologies": [
                "Python",
                "FastAPI",
                "Celery",
                "RPA Tools",
                "Workflow Engines",
            ],
            "features": [
                "Process Analysis & Optimization",
                "Custom Workflow Development",
                "Integration with Existing Systems",
                "Real-time Monitoring & Alerts",
                "Error Handling & Recovery",
                "Scalable Architecture",
            ],
            "recent_projects": [
                {
                    "name": "Invoice Processing System",
                    "industry": "Finance",
                    "improvement": "90% reduction in processing time",
                },
                {
                    "name": "Inventory Management Automation",
                    "industry": "Manufacturing",
                    "improvement": "50% reduction in stockouts",
                },
                {
                    "name": "Customer Onboarding Pipeline",
                    "industry": "SaaS",
                    "improvement": "70% faster onboarding",
                },
            ],
        },
        "ai_integration": {
            "description": "Seamless AI integration into existing business systems",
            "technologies": [
                "REST APIs",
                "GraphQL",
                "Microservices",
                "Event-driven Architecture",
            ],
            "features": [
                "Legacy System Integration",
                "API Development & Management",
                "Data Pipeline Architecture",
                "Real-time Synchronization",
                "Security & Compliance",
                "Performance Optimization",
            ],
            "recent_projects": [
                {
                    "name": "CRM AI Enhancement",
                    "industry": "Sales",
                    "improvement": "35% increase in sales efficiency",
                },
                {
                    "name": "ERP Intelligent Automation",
                    "industry": "Manufacturing",
                    "improvement": "45% reduction in manual processes",
                },
                {
                    "name": "Healthcare AI Assistant",
                    "industry": "Healthcare",
                    "improvement": "60% faster diagnosis support",
                },
            ],
        },
    }


@app.get("/api/portfolio/projects")
async def get_recent_projects():
    """Get showcase of recent AI projects"""
    logger.info("Fetching recent projects showcase")
    return {
        "featured_projects": [
            {
                "id": 1,
                "title": "Enterprise AI Customer Service Platform",
                "description": "Complete AI-powered customer service solution for Fortune 500 company",
                "technology_stack": [
                    "Python",
                    "FastAPI",
                    "React",
                    "OpenAI GPT-4",
                    "PostgreSQL",
                    "Redis",
                    "Docker",
                    "Kubernetes",
                ],
                "features": [
                    "Multi-language support (12 languages)",
                    "Real-time sentiment analysis",
                    "Automated ticket routing",
                    "Integration with Salesforce CRM",
                    "Voice and text support",
                    "Advanced analytics dashboard",
                ],
                "results": {
                    "response_time_improvement": "85%",
                    "customer_satisfaction": "96%",
                    "cost_reduction": "60%",
                    "ticket_volume_handled": "10,000+ daily",
                },
                "industry": "Technology",
                "duration": "6 months",
                "team_size": 1,
                "status": "Deployed & Maintained",
            },
            {
                "id": 2,
                "title": "Healthcare AI Diagnostic Assistant",
                "description": "AI system to assist medical professionals with patient diagnosis and treatment recommendations",
                "technology_stack": [
                    "Python",
                    "TensorFlow",
                    "FastAPI",
                    "React",
                    "PostgreSQL",
                    "Redis",
                    "Docker",
                    "AWS",
                ],
                "features": [
                    "Medical image analysis",
                    "Symptom pattern recognition",
                    "Drug interaction checking",
                    "Treatment recommendation engine",
                    "HIPAA compliant architecture",
                    "Integration with hospital systems",
                ],
                "results": {
                    "diagnostic_accuracy": "94%",
                    "time_to_diagnosis": "50% faster",
                    "medical_errors_reduction": "30%",
                    "patient_throughput": "40% increase",
                },
                "industry": "Healthcare",
                "duration": "8 months",
                "team_size": 1,
                "status": "In Production",
            },
            {
                "id": 3,
                "title": "Financial Trading AI Bot",
                "description": "Automated trading system with risk management and portfolio optimization",
                "technology_stack": [
                    "Python",
                    "PyTorch",
                    "FastAPI",
                    "React",
                    "TimescaleDB",
                    "Redis",
                    "Docker",
                    "AWS",
                ],
                "features": [
                    "Real-time market analysis",
                    "Risk assessment algorithms",
                    "Portfolio optimization",
                    "Automated trade execution",
                    "Performance analytics",
                    "Multi-asset support",
                ],
                "results": {
                    "roi_improvement": "180%",
                    "risk_reduction": "45%",
                    "trade_execution_speed": "milliseconds",
                    "assets_managed": "$50M+",
                },
                "industry": "Finance",
                "duration": "4 months",
                "team_size": 1,
                "status": "Active Trading",
            },
        ],
        "technologies_used": {
            "backend": [
                "Python",
                "FastAPI",
                "Django",
                "Node.js",
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "Celery",
            ],
            "frontend": [
                "React",
                "Vue.js",
                "TypeScript",
                "Tailwind CSS",
                "D3.js",
                "Chart.js",
            ],
            "ai_ml": [
                "OpenAI GPT",
                "Anthropic Claude",
                "TensorFlow",
                "PyTorch",
                "Scikit-learn",
                "Transformers",
            ],
            "infrastructure": [
                "Docker",
                "Kubernetes",
                "AWS",
                "GCP",
                "Azure",
                "Terraform",
                "Jenkins",
            ],
            "databases": [
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "ChromaDB",
                "Elasticsearch",
                "TimescaleDB",
            ],
        },
        "client_testimonials": [
            {
                "client": "Tech Startup CEO",
                "quote": "RazorFlow AI transformed our customer service. The AI chatbot handles 90% of inquiries automatically.",
                "rating": 5,
            },
            {
                "client": "Healthcare Director",
                "quote": "The diagnostic assistant has significantly improved our accuracy and speed. Highly recommended!",
                "rating": 5,
            },
            {
                "client": "Finance Manager",
                "quote": "The trading bot exceeded expectations. ROI improved dramatically with much lower risk.",
                "rating": 5,
            },
        ],
    }


@app.get("/api/booking/availability")
async def get_availability():
    """Get consultant availability for booking system demo"""
    logger.info("Fetching consultant availability")
    return {
        "available_slots": [
            {"date": "2025-09-11", "times": ["09:00", "11:00", "14:00", "16:00"]},
            {"date": "2025-09-12", "times": ["10:00", "13:00", "15:00"]},
            {"date": "2025-09-13", "times": ["09:00", "12:00", "14:00", "17:00"]},
            {"date": "2025-09-16", "times": ["08:00", "10:00", "15:00", "16:00"]},
            {"date": "2025-09-17", "times": ["11:00", "13:00", "16:00"]},
        ],
        "booking_types": [
            {
                "type": "consultation",
                "duration": 60,
                "description": "Free initial consultation",
            },
            {
                "type": "project_planning",
                "duration": 120,
                "description": "Detailed project planning session",
            },
            {
                "type": "technical_review",
                "duration": 90,
                "description": "Technical architecture review",
            },
            {
                "type": "demo",
                "duration": 30,
                "description": "AI solution demonstration",
            },
        ],
        "timezone": "UTC",
        "booking_window": "14 days",
        "auto_confirmation": True,
    }


@app.post("/api/booking/schedule")
async def schedule_appointment(booking_data: dict):
    """Schedule a consultation appointment"""
    logger.info(f"Scheduling appointment: {booking_data}")
    return {
        "booking_id": "RZ-2025-001234",
        "status": "confirmed",
        "date": booking_data.get("date"),
        "time": booking_data.get("time"),
        "type": booking_data.get("type"),
        "duration": booking_data.get("duration", 60),
        "client_email": booking_data.get("email"),
        "calendar_link": "https://calendar.google.com/event?eid=...",
        "meeting_link": "https://meet.google.com/abc-defg-hij",
        "confirmation_sent": True,
        "reminder_scheduled": True,
    }


@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get AI development pipeline status"""
    logger.info("Fetching AI pipeline status")
    return {
        "current_projects": [
            {
                "project": "E-commerce Recommendation Engine",
                "stage": "Model Training",
                "progress": 75,
                "eta": "3 days",
                "client": "RetailCorp",
            },
            {
                "project": "Customer Support Chatbot",
                "stage": "Integration Testing",
                "progress": 90,
                "eta": "1 day",
                "client": "TechStart",
            },
            {
                "project": "Financial Risk Assessment AI",
                "stage": "Deployment",
                "progress": 95,
                "eta": "< 1 day",
                "client": "FinanceGroup",
            },
        ],
        "pipeline_metrics": {
            "average_delivery_time": "6 weeks",
            "success_rate": "98.5%",
            "client_satisfaction": "4.9/5",
            "post_deployment_support": "99.2% uptime",
        },
        "methodology": [
            "Agile development with 2-week sprints",
            "Continuous integration and deployment",
            "Automated testing and quality assurance",
            "Client feedback integration at each milestone",
            "Comprehensive documentation and handover",
        ],
    }


if __name__ == "__main__":
    # For Railway deployment
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
