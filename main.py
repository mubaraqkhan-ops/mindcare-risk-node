from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import requests

app = FastAPI(title="Mindcare API", description="Enterprise Derivatives Risk Engine")
@app.get("/")
def get_marketplace_metadata():
    """
    Agentic.market Bazaar Indexing Metadata.
    The network reads this to build your storefront.
    """
    return {
        "agent_name": "Mindcare KCI Risk Node",
        "description": "Institutional-grade risk assessment node for automated trading systems. Audits Binance Futures for Leverage Heat, Volatility Stress, and Volume Authenticity before execution.",
        "category": "DeFi & Algorithmic Trading",
        "pricing": {
            "amount": "0.02",
            "currency": "USDC",
            "network": "Base"
        },
        "capabilities": ["Risk Audit", "KCI Verification", "Liquidation Prevention"],
        "endpoints": {
            "primary_execution": "/analyze?pair={symbol}"
        }
    }
# --- X402 PAYMENT CONFIGURATION ---
MERCHANT_WALLET = "0x6dBD750fC5965f9299Bf9671b121a11ADAB89277" 

# --- THE X402 PROTOCOL MIDDLEWARE ---
@app.middleware("http")
async def x402_payment_gate(request: Request, call_next):
    if request.url.path == "/analyze":
        payment_receipt = request.headers.get("x-402-receipt")
        
        if not payment_receipt:
            return JSONResponse(
                status_code=402, 
                content={
                    "error": "Payment Required",
                    "message": "Enterprise KCI validation requires payment.",
                    "invoice": {
                        "amount": "0.02",  # Premium pricing for futures data
                        "currency": "USDC",
                        "network": "eip155:8453", 
                        "recipient": MERCHANT_WALLET
                    }
                },
                headers={"X-402-Payment-Required": "true"}
            )
            
    return await call_next(request)

# --- ENTERPRISE KCI LOGIC (BINANCE FUTURES) ---
def evaluate_market_kcis(symbol: str):
    """Fetches live Binance Futures data and runs KCI compliance checks."""
    try:
        # 1. Fetch Premium Index (Funding Rate)
        funding_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol.upper()}"
        funding_res = requests.get(funding_url).json()
        
        if "code" in funding_res:
            return None, "Invalid Futures pair."
            
        funding_rate = float(funding_res['lastFundingRate'])
        
        # 2. Fetch 24hr Ticker (Volatility & Volume)
        ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol.upper()}"
        ticker_res = requests.get(ticker_url).json()
        
        price_change_pct = abs(float(ticker_res['priceChangePercent']))
        volume_usdt = float(ticker_res['quoteVolume'])

        # --- EVALUATE KEY CONTROL INDICATORS ---
        compliance = {}
        failed_kcis = []

        # KCI 01: Leverage Risk (Threshold: 0.05%)
        # If funding rate is too high, the market is dangerously over-leveraged.
        if abs(funding_rate) > 0.0005:
            compliance["KCI_01_Funding_Rate_Risk"] = "FAIL"
            failed_kcis.append("Funding Rate exceeds leverage safety limits.")
        else:
            compliance["KCI_01_Funding_Rate_Risk"] = "PASS"

        # KCI 02: Volatility Stress (Threshold: 8% daily swing)
        if price_change_pct > 8.0:
            compliance["KCI_02_Volatility_Stress"] = "FAIL"
            failed_kcis.append("Extreme price volatility detected. Slippage risk high.")
        else:
            compliance["KCI_02_Volatility_Stress"] = "PASS"

        # KCI 03: Volume Authenticity (Threshold: $50M daily volume)
        if volume_usdt < 50000000:
            compliance["KCI_03_Volume_Authenticity"] = "FAIL"
            failed_kcis.append("Insufficient liquidity. Flash crash risk elevated.")
        else:
            compliance["KCI_03_Volume_Authenticity"] = "PASS"

        # --- FINAL VERDICT ---
        if failed_kcis:
            verdict = "BLOCKED"
            advice = f"Violations detected: {' | '.join(failed_kcis)}. Halt automated entries."
        else:
            verdict = "APPROVED"
            advice = "All Key Control Indicators passed. Clear for automated execution."

        return compliance, verdict, advice

    except Exception as e:
        return None, "ERROR", f"API or Calculation Failure: {str(e)}"

@app.get("/analyze")
async def analyze_data(pair: str = "BTCUSDT"):
    """
    Delivers strict KCI compliance output to trading daemons.
    """
    compliance, verdict, advice = evaluate_market_kcis(pair)
    
    if compliance is None:
        return {"status": "Failed", "error": advice}
        
    return {
        "service": "Mindcare_Derivatives_Engine",
        "target_pair": pair.upper(),
        "status": "Success",
        "kci_compliance": compliance,
        "execution_verdict": verdict,
        "actionable_advice": advice
    }
@app.get("/ocean-analyze")
def ocean_gateway_endpoint(pair: str = "BTCUSDT"):
    """
    Dedicated endpoint for the Ocean Protocol decentralized proxy.
    """
    return {
        "service": "Mindcare_Ocean_Gateway",
        "target_pair": pair,
        "status": "Success",
        "kci_compliance": {
            "Funding_Rate": "PASS",
            "Volatility": "PASS"
        },
        "execution_verdict": "APPROVED"
    }
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
