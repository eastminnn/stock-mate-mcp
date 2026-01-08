from fastmcp import FastMCP
import yfinance as yf

# 서버 초기화
mcp = FastMCP("StockMate")

def get_usd_krw_rate():
    """실시간 USD/KRW 환율을 가져오는 헬퍼 함수"""
    try:
        data = yf.Ticker("USDKRW=X").history(period="1d")
        if data.empty: return 1350.0
        return data['Close'].iloc[-1]
    except:
        return 1350.0
    
@mcp.tool()
def get_stock_report(symbol: str) -> str:
    """특정 종목의 현재가와 등락 정보를 조회합니다. (미국 주식 원화 환산 및 보합 처리)"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        if df.empty or len(df) < 2: 
            return f"❌ '{symbol}' 종목의 데이터를 찾을 수 없습니다."

        price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = ((price - prev_price) / prev_price) * 100

        # 보합(0%) 상태를 포함한 등락 아이콘 처리
        if change > 0:
            direction = "🔺"
        elif change < 0:
            direction = "🔻"
        else:
            direction = "➖" # 변동 없음

        # 미국 주식일 경우 원화로 표시
        is_us_stock = not (symbol.endswith(".KS") or symbol.endswith(".KQ"))
        display_price = price
        currency_label = "원"
        currency_note = ""

        if is_us_stock:
            rate = get_usd_krw_rate()
            display_price = price * rate
            currency_note = f" (실시간 환율 {rate:,.2f}원 적용)"

        return (f"[ StockMate 실시간 시황 ]\n\n"
                f"📌 종목: {symbol}\n"
                f"💰 현재가: {display_price:,.0f}{currency_label}\n"
                f"📈 등락률: {direction} {change:+.2f}%\n"
                f"{currency_note}\n"
                f"--------------------------\n"
                f"💡 '나챗방으로 보내줘'라고 말해보세요!")
    except Exception as e:
        return f"⚠️ 시황 조회 중 오류 발생: {str(e)}"
    
@mcp.tool()
def get_exchange_rate() -> str:
    """주요 국가(미국, 일본, 유럽, 중국)의 실시간 환율 정보를 브리핑합니다."""
    # 조회할 주요 환율 리스트
    pairs = {
        "미국 (USD)": "USDKRW=X",
        "일본 (JPY)": "JPYKRW=X",
        "유럽 (EUR)": "EURKRW=X",
        "중국 (CNY)": "CNYKRW=X"
    }
    
    try:
        report = ["[ 💰 주요 국가 실시간 환율 ]\n"]
        
        for name, symbol in pairs.items():
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                rate = data['Close'].iloc[-1]
                # 일본 엔화는 보통 100엔 단위이므로 별도 처리
                if "JPY" in symbol:
                    report.append(f"🇯🇵 {name}: {rate:,.2f}원 (100엔 기준)")
                elif "USD" in symbol:
                    report.append(f"🇺🇸 {name}: {rate:,.2f}원")
                elif "EUR" in symbol:
                    report.append(f"🇪🇺 {name}: {rate:,.2f}원")
                elif "CNY" in symbol:
                    report.append(f"🇨🇳 {name}: {rate:,.2f}원")
        
        report.append("\n--------------------------")
        report.append("*(yfinance 실시간 데이터 기준)*")
        return "\n".join(report)
    except Exception as e:
        return f"⚠️ 환율 브리핑 중 오류 발생: {str(e)}"
    
@mcp.tool()
def analyze_investment_card(current_price: float, buy_price: float, quantity: int = 1) -> str:
    """매수가 대비 수익률을 계산하여 상세 카드 리포트 형태로 반환합니다."""
    profit = (current_price - buy_price) * quantity
    roi = ((current_price - buy_price) / buy_price) * 100
    status = "🔥 수익 중" if roi > 0 else "🧊 손실 중"
    if roi == 0: status = "➖ 보합 상태"

    return (f"[ 📊 투자 수익률 분석 보고서 ]\n\n"
            f"✅ 분석 결과: {status}\n"
            f"--------------------------\n"
            f"🔹 매수단가: {buy_price:,.0f}원\n"
            f"🔹 현재주가: {current_price:,.0f}원\n"
            f"🔸 보유수량: {quantity}주\n\n"
            f"💰 예상손익: {profit:,.0f}원\n"
            f"📈 최종수익률: {roi:+.2f}%\n"
            f"--------------------------\n"
            f"✨ StockMate와 함께 성투하세요!")

# Vercel 배포용 ASGI 앱
app = mcp.http_app()