from fastmcp import FastMCP
import yfinance as yf

# 서버 초기화
mcp = FastMCP("StockMate")

@mcp.tool()
def get_stock_report(symbol: str) -> str:
    """
    특정 종목의 현재가와 전일 대비 등락 정보를 조회합니다.
    :param symbol: 종목코드 (예: 삼성전자는 '005930.KS', 애플은 'AAPL')
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2d")
        if df.empty: return f"❌ '{symbol}' 종목을 찾을 수 없습니다."

        price = df['Close'].iloc[-1]
        # 수익률 공식: $$ROI = \frac{Current - Previous}{Previous} \times 100$$
        change = ((price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        direction = "🔺" if change > 0 else "🔻"

        # 카카오톡 최적화 포맷
        return (f"[[ StockMate 실시간 시황 ]]\n\n"
                f"📌 종목: {symbol}\n"
                f"💰 현재가: {price:,.2f}원\n"
                f"📈 등락률: {direction} {change:+.2f}%\n"
                f"--------------------------\n"
                f"💡 '수익률 분석해줘'라고 말하면\n"
                f"내 투자 성적을 바로 계산해드려요!")
    except Exception as e:
        return f"⚠️ 시황 조회 중 오류 발생: {str(e)}"
    
@mcp.tool()
def get_exchange_rate(from_currency: str = "USD", to_currency: str = "KRW") -> str:
    """
    실시간 환율 정보를 조회합니다. (예: USD/KRW, USDT/USD 등)
    :param from_currency: 기준 통화 (기본값 USD)
    :param to_currency: 대상 통화 (기본값 KRW)
    """
    try:
        pair = f"{from_currency}{to_currency}=X"
        ticker = yf.Ticker(pair)
        data = ticker.history(period="1d")
        if data.empty:
            return f"❌ {from_currency}/{to_currency} 환율 정보를 가져올 수 없습니다."
            
        rate = data['Close'].iloc[-1]
        return (f"[[ 💱 실시간 환율 정보 ]]\n\n"
                f"💵 {from_currency} 1 = {rate:,.2f} {to_currency}\n"
                f"--------------------------\n"
                f"*(yfinance 실시간 데이터 기준)*")
    except Exception as e:
        return f"⚠️ 환율 조회 중 오류 발생: {str(e)}"

@mcp.tool()
def get_stock_news(symbol: str) -> str:
    """
    해당 종목의 최신 주요 뉴스 3건을 요약하여 제공합니다.
    :param symbol: 종목코드 (예: 'AAPL', '005930.KS')
    """
    try:
        ticker = yf.Ticker(symbol)
        news_list = ticker.news[:3] # 24k 응답 제한 준수를 위해 3건으로 제한
        
        if not news_list:
            return f"📰 {symbol} 관련 최신 뉴스가 없습니다."
            
        report = [f"[[ 📰 {symbol} 최신 주요 뉴스 ]]\n"]
        for news in news_list:
            title = news.get('title')
            link = news.get('link')
            report.append(f"🔹 {title}\n🔗 {link}\n")
            
        return "\n".join(report)
    except Exception as e:
        return f"⚠️ 뉴스 조회 중 오류 발생: {str(e)}"
    
@mcp.tool()
def analyze_investment_card(current_price: float, buy_price: float, quantity: int = 1) -> str:
    """매수가 대비 수익률을 계산하여 상세 카드 리포트 형태로 반환합니다."""
    profit = (current_price - buy_price) * quantity
    roi = ((current_price - buy_price) / buy_price) * 100
    status = "🔥 수익 중" if roi > 0 else "🧊 손실 중"

    # 알림톡 스타일의 시각화 레이아웃
    return (f"[[ 📊 투자 수익률 분석 보고서 ]]\n\n"
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