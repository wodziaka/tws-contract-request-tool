# Importing necessary modules from the Interactive Brokers (IB) API
from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import *
import time
import threading

class ContractRequest(EClient, EWrapper):
  def __init__(self):
    EClient.__init__(self, self)
    self.pendingReqIds = set()      # Tracks sent but not completed request IDs 
    self.completedRequests = 0      # Tracks completed contract detail requests
    self.totalRequests = 0          # Total contract detail requests to make
  
  # Called when API is connected and provides next valid order/request ID
  def nextValidId(self, orderId):
    self.orderId = orderId
  
  # Increment and return next available ID for new requests
  def nextId(self):
    self.orderId += 1
    return self.orderId

  # Handles and prints errors from the API
  def error(self, reqId, errorCode, errorString, advancedOrderReject= ""):
    print(f"reqId: {reqId}, errorCode: {errorCode}, errorString: {errorString}, orderReject: {advancedOrderReject}")

  # Callback when contract details are received
  def contractDetails(self, reqId, contractDetails):
    c = contractDetails.contract
    print(f"\n[Contract Info] reqId: {reqId}")
    print(f"Symbol: {c.symbol}")
    print(f"Security Type: {c.secType}")
    print(f"Exchange: {c.exchange}") 
    print(f"Currency: {c.currency}")
    print(f"Last Trade Date: {c.lastTradeDateOrContractMonth}")
    print(f"Strike: {c.strike}")
    print(f"Right: {c.right}")
    print(f"Trading Class: {c.tradingClass}")

  # Called after contract details for a given request ID have been sent
  def contractDetailsEnd(self, reqId):
    print(f"\n[Info] Finished fetching details for reqId: {reqId}")
    self.completedRequests += 1
    if self.completedRequests >= self.totalRequests:
      self.disconnect()

# Function to create contract objects
def create_contract(info):
  c = Contract()
  c.symbol = info["symbol"]
  c.secType = info["type"]
  c.currency = "USD"
    
   # Define contract attributes
  if info["type"] == "STK":
    c.exchange = "SMART"
    c.primaryExchange = "NASDAQ"
  elif info["type"] == "FUT":
    c.exchange = "CME"
    c.lastTradeDateOrContractMonth = info.get("expiry")
  elif info["type"] == "OPT":
    c.exchange = "SMART"
    c.lastTradeDateOrContractMonth = info.get("expiry")
    c.strike = info.get("strike")
    c.right = info.get("right")
    c.tradingClass = info.get("class", "SPXW")
  return c

# Sample contracts to explore
contracts = [
  {"symbol": "AAPL", "type": "STK"},
  {"symbol": "ES", "type": "FUT", "expiry": "202506"},
  {"symbol": "SPX", "type": "OPT", "expiry": "202506", "strike": 5300, "right": "P", "class": "SPX"}
]

# Initialize and start app
app = ContractRequest()
app.connect("127.0.0.1", 7497, 0)
threading.Thread(target=app.run).start()
time.sleep(1)

app.totalRequests = len(contracts)  # Track number of requested contracts
# Request contract details
for i, info in enumerate(contracts):
  c = create_contract(info)
  app.pendingReqIds.add(app.nextId())
  app.reqContractDetails(app.nextId(), c)
  time.sleep(1)