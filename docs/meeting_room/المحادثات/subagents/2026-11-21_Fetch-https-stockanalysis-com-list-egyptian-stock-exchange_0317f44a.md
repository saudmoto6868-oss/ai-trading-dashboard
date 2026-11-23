# Fetch https://stockanalysis.com/list/egyptian-stock-exchange

- المصدر: `subagents`
- معرف الجلسة: `0317f44a-0505-46d2-af0c-b2ac311f1f64`
- البداية: 2026-11-21T10:34:34.677Z — النهاية: 2026-11-21T10:35:05.840Z
- الرسائل: مستخدم 4 · مساعد 2 · أدوات 2
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** Fetch https://stockanalysis.com/list/egyptian-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one per line, the symbol exactly as printed, with company name after a tab). No commentary. If the page is paginated or blocked, say so in one line and return what you got.
- **طلبات المستخدم (أول 15):**
  1. Fetch https://stockanalysis.com/list/egyptian-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one 
  2. <system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full repo
- **آخر رد للمساعد:** —

---

## المحادثة الكاملة

### user · 2026-11-21T10:34:34.677Z

Fetch https://stockanalysis.com/list/egyptian-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one per line, the symbol exactly as printed, with company name after a tab). No commentary. If the page is paginated or blocked, say so in one line and return what you got.

### user · 2026-11-21T10:34:34.844Z

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered.
</system-reminder>

### assistant · 2026-11-21T10:34:38.093Z

**أداة:** `WebFetch`

```json
{
 "url": "https://stockanalysis.com/list/egyptian-stock-exchange/",
 "prompt": "List every stock ticker symbol shown in the main table on this page, one per line, formatted as: SYMBOL<TAB>Company Name. Output only the list. Also state in one line whether the page is paginated (has multiple pages or a next-page control) or appears blocked, and if so, what portion of the list was shown."
}
```

### user · 2026-11-21T10:34:44.305Z

<details><summary>نتيجة أداة (30426 حرف)</summary>

```
Fetched https://stockanalysis.com/list/egyptian-stock-exchange/ from a non-preapproved source (HTTP 200 OK, text/html, 30245 characters).
<fetched-web-content>
                   List of Stocks on the Egyptian Stock Exchange (EGX)            

[Skip to main content](#main)

[

![logo](/logo.svg)

](/)

 

[Help](/help/) [Log In](/login/) [Sign Up](/pro/)

🎁 Black Friday: 50% off Unlimited and 30% off Pro annual plans

Claim Offer Dismiss

🎁 Black Friday: 50% off Unlimited and 30% off Pro annual plans Claim Offer

[Home](/ "Home")

[Watchlist](/watchlist/ "Watchlist")

[Stocks](/stocks/ "Stocks")

*   [Stock Screener](/stocks/screener/ "Stock Screener")
*   [Stock Exchanges](/list/exchanges/ "Stock Exchanges")
*   [By Country](/list/countries/ "By Country")
*   [Comparison Tool](/stocks/compare/ "Comparison Tool")
*   [Earnings Calendar](/stocks/earnings-calendar/ "Earnings Calendar")
*   [Earnings CallsNew](/earnings-call-transcripts/ "Earnings Calls")
*   [By Industry](/stocks/industry/ "By Industry")
*   [Stock Lists](/list/ "Stock Lists")
*   [Top Stocks](/analysts/top-stocks/ "Top Stocks")
*   [Corporate Actions](/actions/ "Corporate Actions")

[IPOs](/ipos/ "IPOs")

*   [Recent IPOs](/ipos/ "Recent IPOs")
*   [IPO Calendar](/ipos/calendar/ "IPO Calendar")
*   [IPO Lockups](/ipos/lockups/ "IPO Lockups")
*   [IPO Statistics](/ipos/statistics/ "IPO Statistics")
*   [IPO News](/ipos/news/ "IPO News")
*   [IPO Screener](/ipos/screener/ "IPO Screener")

[ETFs](/etf/ "ETFs")

*   [ETF Screener](/etf/screener/ "ETF Screener")
*   [Comparison Tool](/etf/compare/ "Comparison Tool")
*   [New Launches](/etf/list/new/ "New Launches")
*   [ETF Providers](/etf/provider/ "ETF Providers")

[Analysts](/analysts/ "Analysts")

[News](/news/ "News")

[Trending](/trending/ "Trending")

[Private Companies](/private/ "Private Companies")

[Technical Chart](/chart/ "Technical Chart")

[Fundamental Chart](/fundamental-chart/ "Fundamental Chart")

[Market Movers](/markets/gainers/ "Market Movers")

*   [Top Gainers](/markets/gainers/ "Top Gainers")
*   [Top Losers](/markets/losers/ "Top Losers")
*   [Most Active](/markets/active/ "Most Active")
*   [Premarket](/markets/premarket/ "Premarket")
*   [After Hours](/markets/afterhours/ "After Hours")
*   [Market Heatmap](/markets/heatmap/ "Market Heatmap")

[Market Newsletter](/subscribe/ "Market Newsletter")

[Stock Analysis Pro Black Friday](/pro/ "Stock Analysis Pro")

[Tools](/tools/ "Tools")

Collapse

[Sign Up](/pro/) [Log In](/login/) [Help](/help/)

1.  [Home](/)
2.  » [Lists](/list/)
3.  » [Stock Exchanges](/list/exchanges/)

Egyptian Stock Exchange Stocks
==============================

Full Width

A list of actively traded stock ticker symbols on the Egyptian Stock Exchange (EGX). The stocks are sorted by market cap and the list is updated daily. Values are in Egyptian pound (EGP).

231 Stocks
----------

Filter results 

Indicators

Watchlist Screener

Download

OverviewPerformanceDividendsPriceProfile Add View Edit View

| No. | Symbol | Company Name | Market Cap | Stock Price | % Change | Revenue |

| 1 | [COMI](/quote/egx/COMI/) | Commercial International Bank Egypt (CIB) S.A.E. | 434.16B | 127.50 | \-0.39% | 140.33B |
| 2 | [SWDY](/quote/egx/SWDY/) | El Sewedy Electric Company | 251.37B | 117.50 | \-0.40% | 344.37B |
| 3 | [ETEL](/quote/egx/ETEL/) | Telecom Egypt Company | 233.90B | 137.02 | \-3.47% | 121.92B |
| 4 | [TMGH](/quote/egx/TMGH/) | Talaat Moustafa Group Holding | 170.11B | 82.55 | 0.06% | 71.73B |
| 5 | [EGAL](/quote/egx/EGAL/) | Egypt Aluminum | 125.81B | 304.99 | \-0.74% | 53.14B |
| 6 | [QNBE](/quote/egx/QNBE/) | Qatar National Bank | 121.77B | 56.51 | 0.79% | 62.28B |
| 7 | [HDBK](/quote/egx/HDBK/) | Housing and Development Bank- Egypt (S.A.E) | 115.29B | 108.50 | \-0.16% | 34.05B |
| 8 | [MFPC](/quote/egx/MFPC/) | Misr Fertilizer Production Company | 109.62B | 38.22 | 0.13% | 33.72B |
| 9 | [EAST](/quote/egx/EAST/) | Eastern Company S.A.E | 102.24B | 34.08 | 0.00% | 41.49B |
| 10 | [ABUK](/quote/egx/ABUK/) | Abu Qir Fertilizers & Chemical Industries Company (S.A.E) | 96.36B | 76.36 | 0.20% | 25.80B |
| 11 | [ALCN](/quote/egx/ALCN/) | Alexandria Container&Cargo Handling Company | 96.27B | 32.31 | 0.28% | 7.96B |
| 12 | [ORAS](/quote/egx/ORAS/) | Orascom Construction PLC | 91.82B | 806.12 | \-1.93% | 332.60B |
| 13 | [EFIH](/quote/egx/EFIH/) | e-finance for Digital and Financial Investments S.A.E. | 88.00B | 25.53 | 2.12% | 8.09B |
| 14 | [BQDC](/quote/egx/BQDC/) | Banque Du Caire S.A.E. | 83.88B | 5.50 | 0.37% | 41.85B |
| 15 | [EMFD](/quote/egx/EMFD/) | Emaar Misr for Development Company (S.A.E.) | 69.72B | 12.80 | 2.32% | 21.46B |
| 16 | [ADIB](/quote/egx/ADIB/) | Abu Dhabi Islamic Bank - Egypt - S.A.E | 69.30B | 46.20 | \-0.86% | 27.73B |
| 17 | [FWRY](/quote/egx/FWRY/) | Fawry for Banking Technology and Electronic Payments S.A.E. | 58.93B | 17.30 | 2.31% | 10.94B |
| 18 | [CANA](/quote/egx/CANA/) | Suez Canal Bank (S.A.E) | 49.70B | 33.13 | 2.92% | 15.28B |
| 19 | [EFID](/quote/egx/EFID/) | Edita Food Industries Company (S.A.E) | 43.75B | 21.00 | 2.94% | 25.72B |
| 20 | [GPPL](/quote/egx/GPPL/) | Golden Pyramids Plaza S.A.E. | 43.46B | 1.400 | 0.00% | 4.30B |
| 21 | [SCTS](/quote/egx/SCTS/) | Suez Canal Company for Technology Settling (S.A.E) | 43.21B | 475.39 | \-0.96% | 3.15B |
| 22 | [VLMRA](/quote/egx/VLMRA/) | Valmore Holding S.A.E. | 41.18B | 24.00 | 0.38% | 38.14B |
| 23 | [VLMR](/quote/egx/VLMR/) | Valmore Holding S.A.E. | 41.13B | 0.650 | 0.00% | 38.14B |
| 24 | [ORHD](/quote/egx/ORHD/) | Orascom Development Egypt S.A.E. | 37.71B | 10.33 | 0.19% | 31.04B |
| 25 | [HRHO](/quote/egx/HRHO/) | EFG Holding Company S.A.E | 36.62B | 25.50 | 0.79% | 27.71B |
| 26 | [JUFO](/quote/egx/JUFO/) | Juhayna Food Industries S.A.E. | 34.07B | 23.16 | \-0.69% | 35.51B |
| 27 | [HALN](/quote/egx/HALN/) | MNT Tech Holding For Financial Investments | 33.57B | 20.98 | \-3.32% | 12.69B |
| 28 | [PHDC](/quote/egx/PHDC/) | Palm Hills Developments S.A.E. | 32.82B | 11.62 | 1.04% | 40.12B |
| 29 | [BIOC](/quote/egx/BIOC/) | GlaxoSmithKline S.A.E | 32.75B | 392.11 | \-3.66% | 3.62B |
| 30 | [FAIT](/quote/egx/FAIT/) | Faisal Islamic Bank of Egypt | 32.52B | 45.43 | \-0.35% | 15.23B |
| 31 | [FAITA](/quote/egx/FAITA/) | Faisal Islamic Bank of Egypt | 32.52B | 1.009 | 0.80% | 15.23B |
| 32 | [OCDI](/quote/egx/OCDI/) | Sixth of October for Development and Investment Company "SODIC" (S.A.E.) | 32.26B | 25.02 | \-2.27% | 21.46B |
| 33 | [CIEB](/quote/egx/CIEB/) | Credit Agricole - Egypt Bank (S.A.E.) | 28.79B | 23.03 | \-0.78% | 13.49B |
| 34 | [HELI](/quote/egx/HELI/) | Heliopolis Co. for Housing & Development | 26.43B | 6.60 | 0.00% | 5.18B |
| 35 | [EXPA](/quote/egx/EXPA/) | Export Development Bank of Egypt (S.A.E.) | 26.33B | 14.63 | \-0.34% | 15.56B |
| 36 | [FERC](/quote/egx/FERC/) | Ferchem Misr for fertilizers and chemicals S.A.E | 26.26B | 65.65 | 1.20% | 10.60B |
| 37 | [RAYA](/quote/egx/RAYA/) | Raya Holding Company for Financial Investments (S.A.E) | 25.56B | 5.98 | 4.36% | 68.15B |
| 38 | [SCEM](/quote/egx/SCEM/) | Sinai Cement Co. (S.A.E) | 25.43B | 97.52 | \-0.49% | 9.21B |
| 39 | [ARCC](/quote/egx/ARCC/) | Arabian Cement Company S.A.E. | 25.30B | 67.50 | \-1.39% | 13.03B |
| 40 | [GBCO](/quote/egx/GBCO/) | GB Corp | 24.32B | 22.40 | 0.36% | 98.00B |
| 41 | [CCAP](/quote/egx/CCAP/) | QALA For Financial Investments | 24.12B | 5.93 | \-2.15% | 195.41B |
| 42 | [BTFH](/quote/egx/BTFH/) | Beltone Holding S.A.E | 24.12B | 2.250 | \-1.32% | 15.95B |
| 43 | [IRON](/quote/egx/IRON/) | Egyptian Iron and Steel Company | 23.95B | 24.52 | 1.87% | 2.24B |
| 44 | [CIRA](/quote/egx/CIRA/) | Cairo For Investment And Real Estate Developments-CIRA Education | 22.36B | 38.36 | \-0.42% | 5.80B |
| 45 | [CLHO](/quote/egx/CLHO/) | Cleopatra Hospitals Group S.A.E. | 20.61B | 14.04 | 1.67% | 8.15B |
| 46 | [EGCH](/quote/egx/EGCH/) | Egyptian Chemical Industries | 20.26B | 10.20 | \-0.97% | 11.23B |
| 47 | [VALU](/quote/egx/VALU/) | U Consumer Finance S.A.E. | 19.34B | 9.18 | \-3.27% | 1.67B |
| 48 | [TAQA](/quote/egx/TAQA/) | TAQA Arabia S.A.E. | 18.47B | 13.84 | \-1.00% | 29.51B |
| 49 | [MBSC](/quote/egx/MBSC/) | Misr Beni Suef Cement Co. S.A.E | 18.40B | 350.00 | \-0.85% | 6.37B |
| 50 | [EGSA](/quote/egx/EGSA/) | The Egyptian Satellite Company Nilesat | 18.08B | 9.00 | 0.00% | 5.05B |
| 51 | [PHAR](/quote/egx/PHAR/) | Egyptian International Pharmaceutical Industries Company | 17.57B | 104.10 | \-1.80% | 9.88B |
| 52 | [MOIL](/quote/egx/MOIL/) | Maridive and Oil Services S.A.E. | 17.42B | 0.689 | \-0.29% | 12.97B |
| 53 | [MCQE](/quote/egx/MCQE/) | Misr Cement (Qena) Company (S.A.E) | 17.09B | 178.00 | 0.79% | 10.61B |
| 54 | [SAUD](/quote/egx/SAUD/) | alBaraka Bank Egypt S.A.E. | 17.06B | 23.46 | 2.00% | 8.92B |
| 55 | [AMOC](/quote/egx/AMOC/) | Alexandria Mineral Oils Company | 16.97B | 13.14 | \-0.91% | 39.98B |
| 56 | [ORWE](/quote/egx/ORWE/) | Oriental Weavers Carpets Company (S.A.E) | 16.69B | 25.09 | 0.04% | 28.54B |
| 57 | [SKPC](/quote/egx/SKPC/) | Sidi Kerir Petrochemicals Co. | 16.57B | 14.61 | \-0.75% | 18.21B |
| 58 | [UBEE](/quote/egx/UBEE/) | The United Bank | 16.45B | 14.95 | 0.00% | 6.41B |
| 59 | [EFIC](/quote/egx/EFIC/) | Egyptian Financial and Industrial SAE | 16.03B | 160.27 | \-1.07% | 12.02B |
| 60 | [NIPH](/quote/egx/NIPH/) | Nile Pharmaceuticals and Chemical Industries Company | 15.31B | 306.20 | \-4.61% | 2.13B |
| 61 | [MTIE](/quote/egx/MTIE/) | MM Group for Industry and International Trade S.A.E. | 14.84B | 6.55 | \-0.91% | 23.77B |
| 62 | [TALM](/quote/egx/TALM/) | Taaleem Management Services Company S.A.E. | 14.77B | 20.12 | \-0.05% | 2.51B |
| 63 | [EGBE](/quote/egx/EGBE/) | Egyptian Gulf Bank (S.A.E) | 14.00B | 0.500 | 0.40% | 11.48B |
| 64 | [MASR](/quote/egx/MASR/) | Madinet Masr For Housing and Development | 13.90B | 6.51 | \-0.76% | 12.47B |
| 65 | [POUL](/quote/egx/POUL/) | Cairo Poultry Company S.A.E. | 13.56B | 7.58 | \-1.56% | 15.95B |
| 66 | [EGTS](/quote/egx/EGTS/) | Egyptian Resorts Company (S.A.E) | 13.41B | 12.77 | \-0.62% | 1.07B |
| 67 | [ATQA](/quote/egx/ATQA/) | Misr National Steel - Ataqa | 12.14B | 10.12 | \-2.32% | 5.53B |
| 68 | [MHOT](/quote/egx/MHOT/) | Misr Hotels Company | 12.02B | 15.18 | \-4.83% | 2.00B |
| 69 | [BINV](/quote/egx/BINV/) | B Investments Holding S.A.E. | 11.09B | 50.80 | \-0.43% | 1.25B |
| 70 | [CSAG](/quote/egx/CSAG/) | Canal Shipping Agencies Company | 10.83B | 36.09 | 0.70% | 164.98M |
| 71 | [RMDA](/quote/egx/RMDA/) | Tenth of Ramadan for Pharmaceutical Industries and Diagnostic Reagents (Rameda) (S.A.E) | 10.49B | 5.16 | \-0.96% | 4.40B |
| 72 | [ISPH](/quote/egx/ISPH/) | Ibnsina Pharma | 10.48B | 10.40 | \-0.38% | 83.04B |
| 73 | [CICH](/quote/egx/CICH/) | CI Capital Holding For Financial Investments (S.A.E) | 10.20B | 10.20 | \-1.07% | 4.99B |
| 74 | [NAPR](/quote/egx/NAPR/) | National Printing Company S.A.E. | 9.71B | 45.10 | \-1.10% | 7.58B |
| 75 | [AMES](/quote/egx/AMES/) | Alexandria New Medical Center | 9.44B | 38.59 | \-2.30% | 494.02M |
| 76 | [MIPH](/quote/egx/MIPH/) | MINAPHARM Pharmaceuticals | 9.11B | 773.08 | \-0.88% | 7.19B |
| 77 | [AMIA](/quote/egx/AMIA/) | Arab Moltaqa Investments Company | 8.63B | 16.91 | \-0.53% | 2.48B |
| 78 | [MPRC](/quote/egx/MPRC/) | Egyptian Media Production City | 8.63B | 38.34 | \-0.78% | 1.40B |
| 79 | [CPCI](/quote/egx/CPCI/) | Kahira Pharmaceuticals & Chemical Industries Company | 8.59B | 575.30 | \-0.26% | 2.39B |
| 80 | [MOIN](/quote/egx/MOIN/) | Mohandes Insurance Company | 8.42B | 32.40 | 1.60% | 1.97B |
| 81 | [OIH](/quote/egx/OIH/) | Orascom Investment Holding S.A.E. | 8.39B | 1.600 | \-0.62% | 2.97B |
| 82 | [OLFI](/quote/egx/OLFI/) | Obour Land for Food Industries S.A.E. | 8.09B | 20.22 | \-0.35% | 12.93B |
| 83 | [IFAP](/quote/egx/IFAP/) | International Company for Agricultural Crops | 7.98B | 16.04 | 0.13% | 2.58B |
| 84 | [MPCI](/quote/egx/MPCI/) | Memphis Pharmaceuticals & Chemical Industries | 7.94B | 349.05 | \-2.47% | 1.71B |
| 85 | [BONY](/quote/egx/BONY/) | Bonyan for Development and Trade | 7.87B | 4.200 | \-1.41% | 968.37M |
| 86 | [PHTV](/quote/egx/PHTV/) | Pyramisa Hotels & Resorts | 7.79B | 328.78 | 0.00% | 3.24B |
| 87 | [SUGR](/quote/egx/SUGR/) | Delta Sugar Company | 7.41B | 52.08 | 0.93% | 12.00B |
| 88 | [AXPH](/quote/egx/AXPH/) | Alexandria Co. For Pharmaceuticals & Chemical Industries | 7.37B | 1,473.95 | 0.20% | 3.31B |
| 89 | [EGAS](/quote/egx/EGAS/) | Egypt Gas Company SAE | 7.31B | 50.67 | 4.28% | 10.10B |
| 90 | [DOMT](/quote/egx/DOMT/) | Arabian Food Industries Company (DOMTY) - S.A.E | 7.24B | 25.61 | 1.19% | 10.52B |
| 91 | [PRDC](/quote/egx/PRDC/) | Pioneers Properties For Urban Development - PRE Group | 6.79B | 6.50 | \-2.11% | 7.00B |
| 92 | [ISMQ](/quote/egx/ISMQ/) | Iron & Steel for Mines & Quarries | 6.73B | 6.89 | \-0.58% | 1.05B |
| 93 | [ZMID](/quote/egx/ZMID/) | Zahraa El Maadi Investment and Development Company SAE | 6.69B | 6.69 | \-0.30% | 1.10B |
| 94 | [SPHT](/quote/egx/SPHT/) | El Shams Pyramids Co. For Hotels & Touristic Projects S.A.E | 6.43B | 1.420 | 0.00% | \-482.78K |
| 95 | [ARAB](/quote/egx/ARAB/) | Arab Developers Holding | 6.07B | 0.254 | 0.00% | 1.59B |
| 96 | [GOUR](/quote/egx/GOUR/) | Gourmet Egypt.Com Foods | 5.82B | 14.56 | 2.10% | 3.40B |
| 97 | [ENGC](/quote/egx/ENGC/) | Industrial Engineering Company for Construction and Development (ICON) (S.A.E.) | 5.75B | 39.52 | 1.33% | 7.66B |
| 98 | [AJWA](/quote/egx/AJWA/) | AJWA For Food Industries Co. Egypt | 5.67B | 282.01 | 5.52% | 1.80B |
| 99 | [ELEC](/quote/egx/ELEC/) | Electro Cable Egypt | 5.40B | 1.630 | \-0.61% | 9.19B |
| 100 | [SPIN](/quote/egx/SPIN/) | Alexandria Spinning & Weaving Co. | 5.23B | 14.50 | \-3.20% | 676.94M |
| 101 | [ACAP](/quote/egx/ACAP/) | A Capital Holding | 5.07B | 6.94 | \-2.12% | 4.06B |
| 102 | [MICH](/quote/egx/MICH/) | Misr Chemical Industries Co. | 4.91B | 44.73 | \-1.69% | 1.10B |
| 103 | [OCPH](/quote/egx/OCPH/) | October Pharma S.A.E | 4.78B | 198.97 | \-1.76% | 1.46B |
| 104 | [GSSC](/quote/egx/GSSC/) | General Co. For Silos & Storage | 4.65B | 265.59 | 0.79% | 1.93B |
| 105 | [CNFN](/quote/egx/CNFN/) | Contact Financial Holding S.A.E. | 4.63B | 3.870 | \-2.03% | 5.89B |
| 106 | [MCRO](/quote/egx/MCRO/) | Macro Group Pharmaceuticals (Macro Capital) S.A.E | 4.58B | 1.340 | 0.75% | 1.16B |
| 107 | [AFMC](/quote/egx/AFMC/) | Alexandria Flour Mills | 4.57B | 139.00 | \-1.00% | 390.46M |
| 108 | [NINH](/quote/egx/NINH/) | Nozha International Hospital | 4.52B | 15.08 | \-4.74% | 563.75M |
| 109 | [SAIB](/quote/egx/SAIB/) | Société Arabe Internationale de Banque S.A.E | 4.50B | 2.530 | 0.00% | 6.99B |
| 110 | [KORA](/quote/egx/KORA/) | Korra for Energy and Investment Projects (S.A.E.) | 4.50B | 2.000 | \-0.50% | \- |
| 111 | [SDTI](/quote/egx/SDTI/) | SHARM DREAMS Co. for Touristic Investment S.A.E | 4.40B | 83.00 | 0.55% | 400.44M |
| 112 | [SVCE](/quote/egx/SVCE/) | South Valley Cement Company | 4.39B | 9.10 | \-2.26% | 2.76B |
| 113 | [KABO](/quote/egx/KABO/) | El-Nasr Clothing & Textiles Co. (KABO) | 3.99B | 7.07 | 2.76% | 1.12B |
| 114 | [DSCW](/quote/egx/DSCW/) | Dice For Ready-Made Garments (SAE) | 3.97B | 1.480 | \-2.63% | 7.41B |
| 115 | [WCDF](/quote/egx/WCDF/) | Middle & West Delta Flour Mills | 3.85B | 513.48 | 0.00% | 2.91B |
| 116 | [ACGC](/quote/egx/ACGC/) | Arabia Cotton Ginning Company | 3.85B | 13.61 | 0.44% | 3.02B |
| 117 | [AMER](/quote/egx/AMER/) | Amer Group Holding Company S.A.E. | 3.60B | 3.990 | \-4.77% | 1.70B |
| 118 | [UEFM](/quote/egx/UEFM/) | Upper Egypt Mills Company J.S.C | 3.52B | 502.74 | \-0.02% | 2.71B |
| 119 | [UNIT](/quote/egx/UNIT/) | United Co. for Housing & Development - S.A.E. | 3.48B | 15.22 | \-1.23% | 381.79M |
| 120 | [OFH](/quote/egx/OFH/) | O B Financial Holding S.A.E | 3.36B | 0.726 | 0.14% | \-13.97M |
| 121 | [MFSC](/quote/egx/MFSC/) | Egypt Free Shops Co. | 3.34B | 35.64 | 4.85% | 1.34B |
| 122 | [KZPC](/quote/egx/KZPC/) | Kafr El Zayat For Pesticides & Chemicals Co.(S.A.E) | 3.31B | 11.50 | \-4.09% | 2.30B |
| 123 | [INFI](/quote/egx/INFI/) | Ismailia National Co. for Food Industries | 3.26B | 160.11 | 1.66% | 421.03M |
| 124 | [LCSW](/quote/egx/LCSW/) | Lecico Egypt (S.A.E.) | 3.18B | 39.79 | 1.14% | 8.63B |
| 125 | [ADCI](/quote/egx/ADCI/) | The Arab Drug Company | 3.12B | 260.35 | \-0.82% | 1.39B |
| 126 | [ALRA](/quote/egx/ALRA/) | Atlas for Investment & Food Industries | 2.92B | 2.540 | 1.20% | 96.51M |
| 127 | [ICFC](/quote/egx/ICFC/) | International Company for Fertilizers and Chemicals S.A.E | 2.92B | 25.04 | \-5.04% | 4.05B |
| 128 | [GDWA](/quote/egx/GDWA/) | Gadwa for Industrial Development | 2.86B | 0.534 | \-1.11% | 13.63B |
| 129 | [ELKA](/quote/egx/ELKA/) | Cairo for Housing and Development Company (S.A.E) | 2.77B | 1.490 | 1.36% | 465.75M |
| 130 | [CFGH](/quote/egx/CFGH/) | Concrete Fashion Group For Commercial and Industrial investments S.A.E | 2.70B | 0.107 | 0.00% | 8.14B |
| 131 | [NAHO](/quote/egx/NAHO/) | Naeem Holding Company For Investments (S.A.E - Free Zone) | 2.62B | 0.129 | 0.00% | 493.96M |
| 132 | [GPIM](/quote/egx/GPIM/) | GPI for Urban Growth | 2.62B | 1.600 | 1.27% | 45.60M |
| 133 | [ZEOT](/quote/egx/ZEOT/) | Extracted Oil & Derivatives Co. | 2.58B | 12.92 | 17.78% | 4.68B |
| 134 | [ETRS](/quote/egx/ETRS/) | Egyptian Transport & Commercial Services Co. -EGYTRANS NOSCO | 2.53B | 11.23 | 4.66% | 1.73B |
| 135 | [ELSH](/quote/egx/ELSH/) | Al-Shams Company for Housing and Urban Development | 2.43B | 10.71 | \-1.74% | 446.16M |
| 136 | [ACTF](/quote/egx/ACTF/) | Act Financial | 2.41B | 2.110 | \-0.94% | \-23.70M |
| 137 | [ACAMD](/quote/egx/ACAMD/) | Arab Co.,for asset management and development | 2.33B | 1.930 | \-1.03% | 332.16M |
| 138 | [CRST](/quote/egx/CRST/) | Creast Mark For Contracting And Real Estate Development | 2.20B | 1.960 | 0.00% | 88.20M |
| 139 | [EDFM](/quote/egx/EDFM/) | East Delta Flour Mills | 2.18B | 362.76 | 0.00% | 885.16M |
| 140 | [ATLC](/quote/egx/ATLC/) | Al Tawfeek Leasing Company | 2.16B | 5.40 | \-1.28% | 1.93B |
| 141 | [ASCM](/quote/egx/ASCM/) | ASEC Company for Mining ASCOM, S.A.E | 2.15B | 44.20 | \-2.02% | 4.46B |
| 142 | [SMFR](/quote/egx/SMFR/) | Samad Misr EGYFERT.S.A.E | 2.08B | 216.65 | 0.80% | 604.30M |
| 143 | [DAPH](/quote/egx/DAPH/) | Development & Engineering Consultants | 2.03B | 86.25 | 0.41% | 624.24M |
| 144 | [MPCO](/quote/egx/MPCO/) | Mansoura Poultry co.S.A.E | 1.99B | 1.990 | \-0.50% | 651.39M |
| 145 | [GTWL](/quote/egx/GTWL/) | Golden Textiles & Clothes Wool | 1.92B | 134.51 | \-2.95% | 877.63M |
| 146 | [SNFC](/quote/egx/SNFC/) | Sharkia National Company for Food Security | 1.87B | 11.38 | 1.43% | 17.43M |
| 147 | [ISMA](/quote/egx/ISMA/) | Ismailia / Misr Poultry Company S.A.E | 1.85B | 20.63 | 0.63% | 56.50M |
| 148 | [PHGC](/quote/egx/PHGC/) | Premium Healthcare Group | 1.84B | 0.0780 | 1.30% | \- |
| 149 | [CEFM](/quote/egx/CEFM/) | Middle Egypt Flour Mills | 1.84B | 125.13 | \-0.75% | 919.64M |
| 150 | [MOSC](/quote/egx/MOSC/) | Misr Oils & Soap | 1.77B | 295.73 | 13.67% | 3.24B |
| 151 | [MENA](/quote/egx/MENA/) | Mena for Touristic & Real Estate Investment | 1.73B | 7.16 | \-3.24% | 27.63M |
| 152 | [ICID](/quote/egx/ICID/) | International Co. For Investment & Development | 1.73B | 17.28 | 2.98% | 13.76M |
| 153 | [NARE](/quote/egx/NARE/) | Naeem Real Estate Holding Group | 1.68B | 13.15 | \-3.17% | 275.04M |
| 154 | [EALR](/quote/egx/EALR/) | Arab Company For Land Reclamation | 1.58B | 303.46 | 2.59% | 126.34M |
| 155 | [IDRE](/quote/egx/IDRE/) | Ismailia Development and Real Estate Co | 1.54B | 41.78 | 0.53% | 2.52M |
| 156 | [RACC](/quote/egx/RACC/) | Raya Customer Experience | 1.53B | 7.88 | \-0.13% | 3.26B |
| 157 | [AALR](/quote/egx/AALR/) | General Company For Land Reclamation, Development & Reconstruction | 1.51B | 231.87 | 0.71% | 167.86M |
| 158 | [ECAP](/quote/egx/ECAP/) | Al Ezz Ceramics & Porcelain Co. | 1.50B | 28.12 | \-0.07% | 3.00B |
| 159 | [MILS](/quote/egx/MILS/) | North Cairo Flour Mills | 1.50B | 139.91 | \-0.13% | 1.12B |
| 160 | [WKOL](/quote/egx/WKOL/) | Wadi Kom Ombo For Land Reclamation Co. | 1.44B | 172.01 | 0.61% | 206.58M |
| 161 | [DEIN](/quote/egx/DEIN/) | Delta Insurance Company | 1.42B | 10.35 | 0.00% | 2.87B |
| 162 | [ADPC](/quote/egx/ADPC/) | The Arab Dairy Products Co. | 1.42B | 2.880 | \-2.04% | 2.80B |
| 163 | [NCCW](/quote/egx/NCCW/) | Nasr Company for Civil Works | 1.41B | 5.60 | \-1.24% | 283.13M |
| 164 | [EHDR](/quote/egx/EHDR/) | Egyptians for Housing & Development Co. | 1.40B | 2.090 | 0.97% | 257.88M |
| 165 | [GGRN](/quote/egx/GGRN/) | Go Green For Agricultural Investment And Development | 1.39B | 0.990 | \-1.00% | \- |
| 166 | [SCFM](/quote/egx/SCFM/) | South Cairo and Giza Flour Mills and Bakeries Company | 1.32B | 220.21 | \-0.02% | 362.92M |
| 167 | [KRDI](/quote/egx/KRDI/) | AlKhair River for Development Agricultural Investment and Environmental Services | 1.32B | 0.338 | \-0.88% | 416.03M |
| 168 | [MAAL](/quote/egx/MAAL/) | Marseille Almasreia Alkhalegeya For Holding Investment SAE | 1.30B | 6.24 | \-2.50% | \- |
| 169 | [DTPP](/quote/egx/DTPP/) | Delta Co. For Printing & Packaging S.A.E | 1.29B | 57.78 | \-3.70% | 1.02B |
| 170 | [SIPC](/quote/egx/SIPC/) | Sabaa International Company for Pharmaceutical and Chemical Industry | 1.28B | 5.11 | \-2.85% | 40.72M |
| 171 | [AIHC](/quote/egx/AIHC/) | Arabia Investments Holding | 1.27B | 0.816 | \-0.12% | 787.57M |
| 172 | [NDRL](/quote/egx/NDRL/) | National Drilling Company | 1.26B | 4.690 | 0.00% | 1.47B |
| 173 | [ASPI](/quote/egx/ASPI/) | Aspire Capital Holding for Financial Investments | 1.26B | 0.322 | 0.63% | 517.60M |
| 174 | [ODIN](/quote/egx/ODIN/) | ODIN Investments (S.A.E) | 1.21B | 2.020 | \-2.42% | 205.23M |
| 175 | [GGCC](/quote/egx/GGCC/) | Giza General - Contracting and Real Estate Investment S.A.E | 1.20B | 0.553 | \-1.60% | 1.63B |
| 176 | [CAED](/quote/egx/CAED/) | Cairo Educational Services SAE | 1.17B | 97.68 | \-3.34% | 155.60M |
| 177 | [SEIG](/quote/egx/SEIG/) | Saudi Egyptian Investment & Finance Co. S.A.E | 1.16B | 231.23 | \-0.25% | 63.46M |
| 178 | [SEIGA](/quote/egx/SEIGA/) | Saudi Egyptian Investment & Finance Co. S.A.E | 1.15B | 0.950 | 0.00% | 63.46M |
| 179 | [CERA](/quote/egx/CERA/) | The Arab Ceramic Co. | 1.12B | 1.040 | 0.00% | 2.37B |
| 180 | [UEGC](/quote/egx/UEGC/) | El-Saeed Company for Contracting and Real Estate Investment "SCCD" (S.A.E.) | 1.07B | 1.480 | \-1.99% | 2.22B |
| 181 | [MBEG](/quote/egx/MBEG/) | M.B Engineering | 1.04B | 5.13 | \-0.20% | 802.07M |
| 182 | [GTEX](/quote/egx/GTEX/) | GTEX for Commercial and Industrial Investments S.A.E | 1.04B | 0.0410 | 0.00% | \- |
| 183 | [POCO](/quote/egx/POCO/) | Port Said Containers And Cargo Handling Co. | 1.00B | 5.00 | 0.00% | \- |
| 184 | [IEEC](/quote/egx/IEEC/) | Industrial & Engineering Projects | 984.15M | 0.675 | \-2.32% | \- |
| 185 | [NHPS](/quote/egx/NHPS/) | National Company for Housing Professional Syndicates SAE | 955.84M | 59.74 | \-0.99% | \- |
| 186 | [PRCL](/quote/egx/PRCL/) | The General Company for Ceramic and Porcelain Products | 938.82M | 18.64 | \-1.53% | 119.07M |
| 187 | [OBRI](/quote/egx/OBRI/) | El-Ebour Co. for Real Estate Investment S.A.E. | 907.60M | 22.69 | \-0.57% | 1.91B |
| 188 | [LUTS](/quote/egx/LUTS/) | Lotus For Agricultural Investments And Development | 895.09M | 0.673 | \-2.61% | \- |
| 189 | [COSG](/quote/egx/COSG/) | Cairo Oil & Soap Company | 879.84M | 1.410 | 9.30% | 820.01M |
| 190 | [MEPA](/quote/egx/MEPA/) | Medical Packaging Company | 871.15M | 1.330 | 0.00% | 100.17M |
| 191 | [ALUM](/quote/egx/ALUM/) | Arab Aluminum Company (S.A.E) | 827.88M | 19.53 | \-0.51% | 584.81M |
| 192 | [RUBX](/quote/egx/RUBX/) | Rubex International for Plastic and Acrylic Manufacturing | 815.14M | 13.25 | 0.15% | 411.13M |
| 193 | [TANM](/quote/egx/TANM/) | Tanmiya For Real Estate Investment (S.A.E) | 798.80M | 5.49 | \-1.79% | \- |
| 194 | [PRMH](/quote/egx/PRMH/) | Prime Holding S.A.E | 791.00M | 2.260 | \-2.17% | 278.50M |
| 195 | [EBSC](/quote/egx/EBSC/) | Osool ESB Securities Brokerage | 789.22M | 1.510 | \-0.66% | 41.95M |
| 196 | [ICLE](/quote/egx/ICLE/) | International Company for Leasing S.A.E. | 788.00M | 15.76 | 0.00% | 403.71M |
| 197 | [MEGM](/quote/egx/MEGM/) | Middle East Glass Manufacturing Company S.A.E. | 785.36M | 12.54 | 0.00% | 6.14B |
| 198 | [AIDC](/quote/egx/AIDC/) | Arabia for Investment and Development S.A.E. | 771.27M | 0.495 | \-0.20% | \- |
| 199 | [AFDI](/quote/egx/AFDI/) | Al Ahly for Development & Investment | 767.88M | 42.66 | \-1.55% | 166.11M |
| 200 | [RTVC](/quote/egx/RTVC/) | Remco Tourism Villages Construction | 767.54M | 3.110 | 0.00% | 5.96B |
| 201 | [TWSA](/quote/egx/TWSA/) | Tawasoa For Factoring | 742.90M | 6.46 | \-1.37% | 47.49M |
| 202 | [UNIP](/quote/egx/UNIP/) | Universal For Paper and Packaging Materials | 705.76M | 0.308 | 0.00% | 1.40B |
| 203 | [APSW](/quote/egx/APSW/) | Unirab Polvara Spinning & Weaving Co. | 693.28M | 7.40 | 0.00% | 87.36M |
| 204 | [TYCN](/quote/egx/TYCN/) | Tycoon Holding Company For Financial Investments | 691.27M | 13.23 | \-0.30% | 10.04M |
| 205 | [RAKT](/quote/egx/RAKT/) | Rakta Paper Manufacturing Company | 674.10M | 22.47 | 0.00% | 320.98K |
| 206 | [AMII](/quote/egx/AMII/) | Arabian Metal Industries and Industrial Investments | 670.74M | 8.95 | 0.68% | 172.75M |
| 207 | [RREI](/quote/egx/RREI/) | Arab Real Estate Investment Co. | 652.96M | 2.650 | \-1.12% | 172.80M |
| 208 | [EASB](/quote/egx/EASB/) | Egyptian Arabian Company (Themar) for securities Brokerage EAC | 581.00M | 5.81 | \-3.81% | 61.16M |
| 209 | [KWIN](/quote/egx/KWIN/) | El Kahera El Watania Investment | 557.77M | 70.13 | \-1.31% | 31.03M |
| 210 | [ROTO](/quote/egx/ROTO/) | Rowad Tourism Company | 553.46M | 31.97 | 0.31% | 219.47M |
| 211 | [SPMD](/quote/egx/SPMD/) | Speed Medical Co | 544.04M | 0.327 | \-0.31% | 54.73M |
| 212 | [EEII](/quote/egx/EEII/) | Arab Engineering Industries | 541.36M | 2.020 | 1.00% | 186.85M |
| 213 | [FCMD](/quote/egx/FCMD/) | International Company For Medical Industries S.A.E. | 528.27M | 9.16 | 1.55% | 67.62M |
| 214 | [MOED](/quote/egx/MOED/) | The Egyptian Modern Education Systems, S.A.E. | 481.40M | 0.479 | \-0.62% | 56.14M |
| 215 | [CCRS](/quote/egx/CCRS/) | Gulf Canadian Company for Arab Real Estate Investment | 420.00M | 2.000 | \-0.50% | 6.56M |
| 216 | [AREH](/quote/egx/AREH/) | Real Estate Egyptian Consortium S.A.E | 416.00M | 1.040 | 1.96% | 18.78M |
| 217 | [EPCO](/quote/egx/EPCO/) | Egypt for Poultry | 363.12M | 8.53 | 0.71% | 37.14M |
| 218 | [GRCA](/quote/egx/GRCA/) | Grand Capital for Financial Investments | 327.08M | 31.45 | \-1.50% | 9.48M |
| 219 | [ELNA](/quote/egx/ELNA/) | El Nasr Manufacturing Agricultural Crops S.A.E | 324.68M | 41.28 | 0.00% | \- |
| 220 | [TRTO](/quote/egx/TRTO/) | Trans Oceans Tours | 322.86M | 0.0600 | 0.00% | 23.12M |
| 221 | [GIHD](/quote/egx/GIHD/) | Gharbia Islamic Housing Development Company | 284.74M | 50.62 | \-1.71% | 14.29M |
| 222 | [MMAT](/quote/egx/MMAT/) | Marsa Marsa Alam For Tourism Development SAE | 228.50M | 4.570 | 0.88% | \- |
| 223 | [ELWA](/quote/egx/ELWA/) | El Wadi for International and Investment Development SAE | 223.86M | 1.230 | 1.65% | 21.66M |
| 224 | [DGTZ](/quote/egx/DGTZ/) | Digitize for Investment And Technology | 223.56M | 2.070 | \-4.61% | \- |
| 225 | [DCCC](/quote/egx/DCCC/) | Damietta Container & Cargo Handling Co. | 200.00M | 1.818 | 0.00% | \- |
| 226 | [NEDA](/quote/egx/NEDA/) | Northern Upper Egypt For Development & Agricultural Production Co. | 156.20M | 2.460 | 0.00% | \-4.00M |
| 227 | [EPPK](/quote/egx/EPPK/) | El Ahram Co. For Printing And Packaging SAE | 81.37M | 9.78 | 0.00% | 18.04M |
| 228 | [GMCI](/quote/egx/GMCI/) | GMC Group For Industrial Commercial & Financial Investments | 70.33M | 1.690 | 0.00% | 543.25K |
| 229 | [EOSB](/quote/egx/EOSB/) | El Orouba Securities Brokerage | 47.50M | 1.610 | 0.00% | 3.40M |
| 230 | [CPME](/quote/egx/CPME/) | Catalyst Partners | 33.80M | 33.80 | \-5.48% | \- |
| 231 | [COPR](/quote/egx/COPR/) | Copper for Commercial Investment & Real Estate Development | 2.00M | 0.385 | \-1.03% | 36.21M |

Back to Top ↑

[

Stock Analysis Pro

Upgrade now for unlimited access to all data and tools.



](/pro/)

[

Market Newsletter

Get a daily email with the top market news in bullet point format.



](/subscribe/)

[

Stock Screener

Filter, sort and analyze all stocks to find your next investment.



](/stocks/screener/)

[

Watchlists

Keep track of your favorite stocks in real-time.



](/watchlist/)

#### Install The App

[![Download on the App Store](/app-store-download.svg)

4.9

7.9K

](https://apps.apple.com/us/app/stock-analysis-app/id6751272467)[![Get it on Google Play](/google-play-badge.svg)

4.8

8.8K

](https://play.google.com/store/apps/details?id=com.stockanalysis.app&referrer=utm_source%3Dstockanalysis%26utm_medium%3Dwebsite%26utm_content%3Dbadge)

#### Sections

*   [Stocks](/stocks/)
*   [IPOs](/ipos/)
*   [ETFs](/etf/)
*   [Private Companies](/private/)

#### Services

*   [Stock Analysis Pro](/pro/)
*   [Free Newsletter](/subscribe/)
*   [Get Support](/support/)
*   [Install The App](/app/)

#### Website

*   [Login](/login/)
*   [Create Account](/create-account/)
*   [Changelog](/changelog/)
*   [Data Sources](/data-sources/)
*   [Advertise](/advertise/)
*   [Help Center](/help/)

#### Company

*   [About](/about/)
*   [Contact Us](/contact/)
*   [Terms of Use](/terms-of-use/)
*   [Privacy Policy](/privacy-policy/)
*   [Affiliate Program](/affiliates/)

#### Market Newsletter

Daily market news in bullet point format.

Subscribe

#### Site Theme

Light Dark

[![Facebook](/img/icons/facebook.svg)](https://www.facebook.com/stockanalysisoff/) [![X (Twitter)](/img/icons/x.svg)](https://x.com/stock_analysisx) [![LinkedIn](/img/icons/linkedin.svg)](https://www.linkedin.com/company/stock-analysis/) [![Threads](/img/icons/threads.svg)](https://www.threads.com/@stockanalysis_com) [![Download on the App Store](/app-store-download.svg)](https://apps.apple.com/us/app/stock-analysis-app/id6751272467) [![Get it on Google Play](/google-play-badge.svg)](https://play.google.com/store/apps/details?id=com.stockanalysis.app&referrer=utm_source%3Dstockanalysis%26utm_medium%3Dwebsite%26utm_content%3Dfooter)

© 2026 StockAnalysis.com. All rights reserved.
</fetched-web-content>
```

</details>

### assistant · 2026-11-21T10:35:03.533Z

**أداة:** `SubagentHandback`

```json
{
 "message": "COMI\tCommercial International Bank Egypt (CIB) S.A.E.\nSWDY\tEl Sewedy Electric Company\nETEL\tTelecom Egypt Company\nTMGH\tTalaat Moustafa Group Holding\nEGAL\tEgypt Aluminum\nQNBE\tQatar National Bank\nHDBK\tHousing and Development Bank- Egypt (S.A.E)\nMFPC\tMisr Fertilizer Production Company\nEAST\tEastern Company S.A.E\nABUK\tAbu Qir Fertilizers & Chemical Industries Company (S.A.E)\nALCN\tAlexandria Container&Cargo Handling Company\nORAS\tOrascom Construction PLC\nEFIH\te-finance for Digital and Financial Investments S.A.E.\nBQDC\tBanque Du Caire S.A.E.\nEMFD\tEmaar Misr for Development Company (S.A.E.)\nADIB\tAbu Dhabi Islamic Bank - Egypt - S.A.E\nFWRY\tFawry for Banking Technology and Electronic Payments S.A.E.\nCANA\tSuez Canal Bank (S.A.E)\nEFID\tEdita Food Industries Company (S.A.E)\nGPPL\tGolden Pyramids Plaza S.A.E.\nSCTS\tSuez Canal Company for Technology Settling (S.A.E)\nVLMRA\tValmore Holding S.A.E.\nVLMR\tValmore Holding S.A.E.\nORHD\tOrascom Development Egypt S.A.E.\nHRHO\tEFG Holding Company S.A.E\nJUFO\tJuhayna Food Industries S.A.E.\nHALN\tMNT Tech Holding For Financial Investments\nPHDC\tPalm Hills Developments S.A.E.\nBIOC\tGlaxoSmithKline S.A.E\nFAIT\tFaisal Islamic Bank of Egypt\nFAITA\tFaisal Islamic Bank of Egypt\nOCDI\tSixth of October for Development and Investment Company \"SODIC\" (S.A.E.)\nCIEB\tCredit Agricole - Egypt Bank (S.A.E.)\nHELI\tHeliopolis Co. for Housing & Development\nEXPA\tExport Development Bank of Egypt (S.A.E.)\nFERC\tFerchem Misr for fertilizers and chemicals S.A.E\nRAYA\tRaya Holding Company for Financial Investments (S.A.E)\nSCEM\tSinai Cement Co. (S.A.E)\nARCC\tArabian Cement Company S.A.E.\nGBCO\tGB Corp\nCCAP\tQALA For Financial Investments\nBTFH\tBeltone Holding S.A.E\nIRON\tEgyptian Iron and Steel Company\nCIRA\tCairo For Investment And Real Estate Developments-CIRA Education\nCLHO\tCleopatra Hospitals Group S.A.E.\nEGCH\tEgyptian Chemical Industries\nVALU\tU Consumer Finance S.A.E.\nTAQA\tTAQA Arabia S.A.E.\nMBSC\tMisr Beni Suef Cement Co. S.A.E\nEGSA\tThe Egyptian Satellite Company Nilesat\nPHAR\tEgyptian International Pharmaceutical Industries Company\nMOIL\tMaridive and Oil Services S.A.E.\nMCQE\tMisr Cement (Qena) Company (S.A.E)\nSAUD\talBaraka Bank Egypt S.A.E.\nAMOC\tAlexandria Mineral Oils Company\nORWE\tOriental Weavers Carpets Company (S.A.E)\nSKPC\tSidi Kerir Petrochemicals Co.\nUBEE\tThe United Bank\nEFIC\tEgyptian Financial and Industrial SAE\nNIPH\tNile Pharmaceuticals and Chemical Industries Company\nMTIE\tMM Group for Industry and International Trade S.A.E.\nTALM\tTaaleem Management Services Company S.A.E.\nEGBE\tEgyptian Gulf Bank (S.A.E)\nMASR\tMadinet Masr For Housing and Development\nPOUL\tCairo Poultry Company S.A.E.\nEGTS\tEgyptian Resorts Company (S.A.E)\nATQA\tMisr National Steel - Ataqa\nMHOT\tMisr Hotels Company\nBINV\tB Investments Holding S.A.E.\nCSAG\tCanal Shipping Agencies Company\nRMDA\tTenth of Ramadan for Pharmaceutical Industries and Diagnostic Reagents (Rameda) (S.A.E)\nISPH\tIbnsina Pharma\nCICH\tCI Capital Holding For Financial Investments (S.A.E)\nNAPR\tNational Printing Company S.A.E.\nAMES\tAlexandria New Medical Center\nMIPH\tMINAPHARM Pharmaceuticals\nAMIA\tArab Moltaqa Investments Company\nMPRC\tEgyptian Media Production City\nCPCI\tKahira Pharmaceuticals & Chemical Industries Company\nMOIN\tMohandes Insurance Company\nOIH\tOrascom Investment Holding S.A.E.\nOLFI\tObour Land for Food Industries S.A.E.\nIFAP\tInternational Company for Agricultural Crops\nMPCI\tMemphis Pharmaceuticals & Chemical Industries\nBONY\tBonyan for Development and Trade\nPHTV\tPyramisa Hotels & Resorts\nSUGR\tDelta Sugar Company\nAXPH\tAlexandria Co. For Pharmaceuticals & Chemical Industries\nEGAS\tEgypt Gas Company SAE\nDOMT\tArabian Food Industries Company (DOMTY) - S.A.E\nPRDC\tPioneers Properties For Urban Development - PRE Group\nISMQ\tIron & Steel for Mines & Quarries\nZMID\tZahraa El Maadi Investment and Development Company SAE\nSPHT\tEl Shams Pyramids Co. For Hotels & Touristic Projects S.A.E\nARAB\tArab Developers Holding\nGOUR\tGourmet Egypt.Com Foods\nENGC\tIndustrial Engineering Company for Construction and Development (ICON) (S.A.E.)\nAJWA\tAJWA For Food Industries Co. Egypt\nELEC\tElectro Cable Egypt\nSPIN\tAlexandria Spinning & Weaving Co.\nACAP\tA Capital Holding\nMICH\tMisr Chemical Industries Co.\nOCPH\tOctober Pharma S.A.E\nGSSC\tGeneral Co. For Silos & Storage\nCNFN\tContact Financial Holding S.A.E.\nMCRO\tMacro Group Pharmaceuticals (Macro Capital) S.A.E\nAFMC\tAlexandria Flour Mills\nNINH\tNozha International Hospital\nSAIB\tSociété Arabe Internationale de Banque S.A.E\nKORA\tKorra for Energy and Investment Projects (S.A.E.)\nSDTI\tSHARM DREAMS Co. for Touristic Investment S.A.E\nSVCE\tSouth Valley Cement Company\nKABO\tEl-Nasr Clothing & Textiles Co. (KABO)\nDSCW\tDice For Ready-Made Garments (SAE)\nWCDF\tMiddle & West Delta Flour Mills\nACGC\tArabia Cotton Ginning Company\nAMER\tAmer Group Holding Company S.A.E.\nUEFM\tUpper Egypt Mills Company J.S.C\nUNIT\tUnited Co. for Housing & Development - S.A.E.\nOFH\tO B Financial Holding S.A.E\nMFSC\tEgypt Free Shops Co.\nKZPC\tKafr El Zayat For Pesticides & Chemicals Co.(S.A.E)\nINFI\tIsmailia National Co. for Food Industries\nLCSW\tLecico Egypt (S.A.E.)\nADCI\tThe Arab Drug Company\nALRA\tAtlas for Investment & Food Industries\nICFC\tInternational Company for Fertilizers and Chemicals S.A.E\nGDWA\tGadwa for Industrial Development\nELKA\tCairo for Housing and Development Company (S.A.E)\nCFGH\tConcrete Fashion Group For Commercial and Industrial investments S.A.E\nNAHO\tNaeem Holding Company For Investments (S.A.E - Free Zone)\nGPIM\tGPI for Urban Growth\nZEOT\tExtracted Oil & Derivatives Co.\nETRS\tEgyptian Transport & Commercial Services Co. -EGYTRANS NOSCO\nELSH\tAl-Shams Company for Housing and Urban Development\nACTF\tAct Financial\nACAMD\tArab Co.,for asset management and development\nCRST\tCreast Mark For Contracting And Real Estate Development\nEDFM\tEast Delta Flour Mills\nATLC\tAl Tawfeek Leasing Company\nASCM\tASEC Company for Mining ASCOM, S.A.E\nSMFR\tSamad Misr EGYFERT.S.A.E\nDAPH\tDevelopment & Engineering Consultants\nMPCO\tMansoura Poultry co.S.A.E\nGTWL\tGolden Textiles & Clothes Wool\nSNFC\tSharkia National Company for Food Security\nISMA\tIsmailia / Misr Poultry Company S.A.E\nPHGC\tPremium Healthcare Group\nCEFM\tMiddle Egypt Flour Mills\nMOSC\tMisr Oils & Soap\nMENA\tMena for Touristic & Real Estate Investment\nICID\tInternational Co. For Investment & Development\nNARE\tNaeem Real Estate Holding Group\nEALR\tArab Company For Land Reclamation\nIDRE\tIsmailia Development and Real Estate Co\nRACC\tRaya Customer Experience\nAALR\tGeneral Company For Land Reclamation, Development & Reconstruction\nECAP\tAl Ezz Ceramics & Porcelain Co.\nMILS\tNorth Cairo Flour Mills\nWKOL\tWadi Kom Ombo For Land Reclamation Co.\nDEIN\tDelta Insurance Company\nADPC\tThe Arab Dairy Products Co.\nNCCW\tNasr Company for Civil Works\nEHDR\tEgyptians for Housing & Development Co.\nGGRN\tGo Green For Agricultural Investment And Development\nSCFM\tSouth Cairo and Giza Flour Mills and Bakeries Company\nKRDI\tAlKhair River for Development Agricultural Investment and Environmental Services\nMAAL\tMarseille Almasreia Alkhalegeya For Holding Investment SAE\nDTPP\tDelta Co. For Printing & Packaging S.A.E\nSIPC\tSabaa International Company for Pharmaceutical and Chemical Industry\nAIHC\tArabia Investments Holding\nNDRL\tNational Drilling Company\nASPI\tAspire Capital Holding for Financial Investments\nODIN\tODIN Investments (S.A.E)\nGGCC\tGiza General - Contracting and Real Estate Investment S.A.E\nCAED\tCairo Educational Services SAE\nSEIG\tSaudi Egyptian Investment & Finance Co. S.A.E\nSEIGA\tSaudi Egyptian Investment & Finance Co. S.A.E\nCERA\tThe Arab Ceramic Co.\nUEGC\tEl-Saeed Company for Contracting and Real Estate Investment \"SCCD\" (S.A.E.)\nMBEG\tM.B Engineering\nGTEX\tGTEX for Commercial and Industrial Investments S.A.E\nPOCO\tPort Said Containers And Cargo Handling Co.\nIEEC\tIndustrial & Engineering Projects\nNHPS\tNational Company for Housing Professional Syndicates SAE\nPRCL\tThe General Company for Ceramic and Porcelain Products\nOBRI\tEl-Ebour Co. for Real Estate Investment S.A.E.\nLUTS\tLotus For Agricultural Investments And Development\nCOSG\tCairo Oil & Soap Company\nMEPA\tMedical Packaging Company\nALUM\tArab Aluminum Company (S.A.E)\nRUBX\tRubex International for Plastic and Acrylic Manufacturing\nTANM\tTanmiya For Real Estate Investment (S.A.E)\nPRMH\tPrime Holding S.A.E\nEBSC\tOsool ESB Securities Brokerage\nICLE\tInternational Company for Leasing S.A.E.\nMEGM\tMiddle East Glass Manufacturing Company S.A.E.\nAIDC\tArabia for Investment and Development S.A.E.\nAFDI\tAl Ahly for Development & Investment\nRTVC\tRemco Tourism Villages Construction\nTWSA\tTawasoa For Factoring\nUNIP\tUniversal For Paper and Packaging Materials\nAPSW\tUnirab Polvara Spinning & Weaving Co.\nTYCN\tTycoon Holding Company For Financial Investments\nRAKT\tRakta Paper Manufacturing Company\nAMII\tArabian Metal Industries and Industrial Investments\nRREI\tArab Real Estate Investment Co.\nEASB\tEgyptian Arabian Company (Themar) for securities Brokerage EAC\nKWIN\tEl Kahera El Watania Investment\nROTO\tRowad Tourism Company\nSPMD\tSpeed Medical Co\nEEII\tArab Engineering Industries\nFCMD\tInternational Company For Medical Industries S.A.E.\nMOED\tThe Egyptian Modern Education Systems, S.A.E.\nCCRS\tGulf Canadian Company for Arab Real Estate Investment\nAREH\tReal Estate Egyptian Consortium S.A.E\nEPCO\tEgypt for Poultry\nGRCA\tGrand Capital for Financial Investments\nELNA\tEl Nasr Manufacturing Agricultural Crops S.A.E\nTRTO\tTrans Oceans Tours\nGIHD\tGharbia Islamic Housing Development Company\nMMAT\tMarsa Marsa Alam For Tourism Development SAE\nELWA\tEl Wadi for International and Investment Development SAE\nDGTZ\tDigitize for Investment And Technology\nDCCC\tDamietta Container & Cargo Handling Co.\nNEDA\tNorthern Upper Egypt For Development & Agricultural Production Co.\nEPPK\tEl Ahram Co. For Printing And Packaging SAE\nGMCI\tGMC Group For Industrial Commercial & Financial Investments\nEOSB\tEl Orouba Securities Brokerage\nCPME\tCatalyst Partners\nCOPR\tCopper for Commercial Investment & Real Estate Development"
}
```

### user · 2026-11-21T10:35:05.840Z

**نتيجة أداة:**
```
{"success":true,"message":"Report delivered to your caller."}
```
