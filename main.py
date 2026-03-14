from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, transactions, report, anomaly, chat

app = FastAPI(
    title="Finance Autopilot API",
    description="AI-powered personal finance analysis. Upload any bank statement and get instant insights.",
    version="2.0.0",
)

# CORS — allows React Native Web + future mobile app to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(report.router, prefix="/api/v1", tags=["Report"])
app.include_router(anomaly.router, prefix="/api/v1", tags=["Anomaly"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])


@app.get("/")
def root():
    return {
        "name": "Finance Autopilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
