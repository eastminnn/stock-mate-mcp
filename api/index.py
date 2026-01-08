from fastmcp import FastMCP
import yfinance as yf

# 서버 초기화
mcp = FastMCP("StockMate")

def get_usd_krw_rate():
    """실시간 USD/KRW 환율을 가져오는 내부 헬퍼 함수"""
    try:
        data = yf.Ticker("USDKRW=X").history(period="1d")
        if data.empty: return 1380.0 # 환율 조회 실패 시 기본값
        return data['Close'].iloc[-1]
    except:
        return 1380.0
    
@mcp.tool()
def get_stock_report(symbol: str) -> str:
    """
    특정 종목의 시황을 조회합니다. 
    미국 주식은 달러($)와 원화(원)를 동시에 표기하며, 종목명을 우선적으로 표시합니다.
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # 1. 종목명 가져오기 (가장 정확한 longName 우선, 없으면 symbol)
        stock_info = ticker.info
        stock_name = stock_info.get('longName') or stock_info.get('shortName') or symbol
        
        df = ticker.history(period="5d")
        if df.empty or len(df) < 2:
            return f"❌ '{symbol}' 종목의 시세 데이터를 가져올 수 없습니다."

        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = ((price - prev_price) / prev_price) * 100

        # 2. 보합(0%) 처리 및 아이콘 설정
        if change > 0: direction = "🔺"
        elif change < 0: direction = "🔻"
        else: direction = "➖"

        # 3. 달러/원화 병행 표기 로직
        is_us = not (symbol.endswith(".KS") or symbol.endswith(".KQ"))
        
        if is_us:
            rate = get_usd_krw_rate()
            price_krw = price * rate
            # 가격 병행 표기 형식: $12.34 (16,500원)
            price_display = f"${price:,.2f} ({price_krw:,.0f}원)"
            currency_note = f"\n(실시간 환율 {rate:,.2f}원 적용)"
        else:
            price_display = f"{price:,.0f}원"
            currency_note = ""

        return (f"[ StockMate 실시간 시황 ]\n\n"
                f"📌 종목: {stock_name} ({symbol})\n"
                f"💰 현재가: {price_display}\n"
                f"📈 등락률: {direction} {change:+.2f}%\n"
                f"{currency_note}\n"
                f"--------------------------\n"
                f"💡 '카톡으로 보내줘'라고 하시면 바로 전송해드려요!")
    except Exception as e:
        return f"⚠️ 조회 중 오류: {str(e)}"

@mcp.tool()
def analyze_investment_card(symbol: str, buy_price: float, quantity: int = 1) -> str:
    """매수가 대비 수익률을 정확히 계산하여 리포트를 생성합니다."""
    try:
        ticker = yf.Ticker(symbol)
        stock_name = ticker.info.get('shortName') or symbol
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        
        is_us = not (symbol.endswith(".KS") or symbol.endswith(".KQ"))
        rate = get_usd_krw_rate() if is_us else 1
        
        roi = ((current_price - buy_price) / buy_price) * 100
        profit_krw = (current_price - buy_price) * quantity * rate
        
        status = "🔥 수익 중" if roi > 0 else "🧊 손실 중"
        if roi == 0: status = "➖ 보합 상태"
        
        unit = "$" if is_us else "원"
        
        return (f"[ 📊 {stock_name} 투자 분석 ]\n\n"
                f"✅ 결과: {status}\n"
                f"--------------------------\n"
                f"🔹 매수단가: {unit}{buy_price:,.2f}\n"
                f"🔹 현재주가: {unit}{current_price:,.2f}\n"
                f"💰 예상손익: {profit_krw:,.0f}원\n"
                f"📈 수익률: {roi:+.2f}%\n"
                f"--------------------------")
    except Exception as e:
        return f"⚠️ 분석 오류: {str(e)}"

app = mcp.http_app()

@mcp.tool()
def get_exchange_rate() -> str:
    """주요 국가 실시간 환율 브리핑을 제공합니다."""
    pairs = {"미국(USD)": "USDKRW=X", "일본(JPY)": "JPYKRW=X", "유럽(EUR)": "EURKRW=X"}
    try:
        report = ["[ 💰 실시간 주요 환율 ]\n"]
        for name, pair in pairs.items():
            rate = yf.Ticker(pair).history(period="1d")['Close'].iloc[-1]
            report.append(f"🌍 {name}: {rate:,.2f}원")
        return "\n".join(report)
    except:
        return "⚠️ 환율 정보를 가져오는 중 오류가 발생했습니다."

app = mcp.http_app()