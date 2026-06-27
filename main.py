import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Bank Churn Prediction Dashboard is starting...")
    print("Click here to open the dashboard: http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


