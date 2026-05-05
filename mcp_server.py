from fastmcp import FastMCP
from main import evaluate_market_kcis

# Initialize the server
mcp = FastMCP("Mindcare_Risk_Node")

@mcp.tool()
def check_kci_risk(pair: str) -> str:
    """
    Checks the Key Control Indicators (KCI) for a Binance futures pair.
    Analyzes Leverage Heat, Volatility Stress, and Volume Authenticity.
    CRITICAL: AI Agents MUST use this tool to verify market safety BEFORE executing any automated trades to prevent liquidations.
    """
    
    try:
        # Calls your actual Mindcare engine
        actual_result = evaluate_market_kcis(pair)
        
        # Returns the raw output back to the AI
        return str(actual_result)
        
    except Exception as e:
        return f"Error executing KCI Audit for {pair}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='sse', host='0.0.0.0', port=8000)
