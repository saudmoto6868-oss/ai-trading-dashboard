# Fetch https://stockanalysis.com/list/saudi-stock-exchange/ a

- المصدر: `subagents`
- معرف الجلسة: `0317f44a-0505-46d2-af0c-b2ac311f1f64`
- البداية: 2026-11-21T10:34:35.120Z — النهاية: 2026-11-21T10:35:10.010Z
- الرسائل: مستخدم 4 · مساعد 2 · أدوات 2
- تنظيف الخصوصية: أرقام التليفون وال api_id والـ hash والمفاتيح والإيميلات اتشالت بـ regex، وده مش مضمون ١٠٠٪.

## ملخص تلقائي (مش تلخيص AI)
- مبني على أول طلب وآخر رد وقايمة طلبات المستخدم. راجع المحادثة الكاملة للتفاصيل.
- **أول طلب:** Fetch https://stockanalysis.com/list/saudi-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one per line, the numeric code exactly as printed, with company name after a tab). No commentary. If the page is paginated or blocked, say so in one line and return what you got.
- **طلبات المستخدم (أول 15):**
  1. Fetch https://stockanalysis.com/list/saudi-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one per
  2. <system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full repo
- **آخر رد للمساعد:** —

---

## المحادثة الكاملة

### user · 2026-11-21T10:34:35.120Z

Fetch https://stockanalysis.com/list/saudi-stock-exchange/ and return ONLY a plain list of every listed stock ticker symbol shown on the page (one per line, the numeric code exactly as printed, with company name after a tab). No commentary. If the page is paginated or blocked, say so in one line and return what you got.

### user · 2026-11-21T10:34:35.308Z

<system-reminder>
Your final report is delivered through SubagentHandback: when your work is complete, call SubagentHandback({message: <your full report>}). The call ends your run, so make it your last step. Only a SubagentHandback call reaches your caller as your result; plain text you write at the end is not delivered.
</system-reminder>

### assistant · 2026-11-21T10:34:37.853Z

**أداة:** `WebFetch`

```json
{
 "url": "https://stockanalysis.com/list/saudi-stock-exchange/",
 "prompt": "List every listed stock ticker symbol shown on the page. Output ONLY one per line: the numeric code exactly as printed, then a tab, then the company name. No commentary. If the page is paginated or blocked, state that in one line first, then return what was obtained."
}
```

### user · 2026-11-21T10:34:47.223Z

<details><summary>نتيجة أداة (46677 حرف)</summary>

```
Fetched https://stockanalysis.com/list/saudi-stock-exchange/ from a non-preapproved source (HTTP 200 OK, text/html, 46499 characters).
<fetched-web-content>
                   List of Stocks on the Saudi Arabia Stock Exchange            

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

Saudi Stock Exchange Stocks
===========================

Full Width

A list of actively traded stock ticker symbols on the Saudi Stock Exchange in Saudi Arabia. The stocks are sorted by market cap and the list is updated daily. Values are in Saudi riyal (SAR).

383 Stocks
----------

Filter results 

Indicators

Watchlist Screener

Download

OverviewPerformanceDividendsPriceProfile Add View Edit View

| No. | Symbol | Company Name | Market Cap | Stock Price | % Change | Revenue |

| 1 | [2222](/quote/tadawul/2222/) | Saudi Arabian Oil Company | 6.41T | 26.48 | 0.15% | 1.93T |
| 2 | [1120](/quote/tadawul/1120/) | Al Rajhi Banking and Investment Corporation | 375.90B | 62.65 | \-0.40% | 39.95B |
| 3 | [1180](/quote/tadawul/1180/) | The Saudi National Bank | 223.27B | 37.62 | \-1.47% | 39.58B |
| 4 | [1211](/quote/tadawul/1211/) | Saudi Arabian Mining Company (Maaden) | 217.38B | 56.00 | \-2.35% | 41.51B |
| 5 | [7010](/quote/tadawul/7010/) | Saudi Telecom Company | 206.26B | 41.38 | 0.34% | 79.99B |
| 6 | [2010](/quote/tadawul/2010/) | Saudi Basic Industries Corporation | 146.64B | 48.88 | 0.41% | 107.08B |
| 7 | [2082](/quote/tadawul/2082/) | ACWA Power Company | 124.89B | 163.00 | \-0.43% | 8.28B |
| 8 | [1010](/quote/tadawul/1010/) | Riyad Bank | 81.31B | 20.39 | \-0.20% | 17.60B |
| 9 | [4013](/quote/tadawul/4013/) | Dr. Sulaiman Al Habib Medical Services Group Company | 72.77B | 207.90 | \-0.62% | 15.25B |
| 10 | [1060](/quote/tadawul/1060/) | Saudi Awwal Bank | 67.27B | 32.74 | \-0.79% | 14.05B |
| 11 | [1150](/quote/tadawul/1150/) | Alinma Bank | 65.85B | 21.95 | \-0.05% | 11.19B |
| 12 | [5110](/quote/tadawul/5110/) | Saudi Energy Company | 64.08B | 15.38 | 0.00% | 111.19B |
| 13 | [2020](/quote/tadawul/2020/) | SABIC Agri-Nutrients Company | 53.98B | 113.40 | \-0.26% | 11.70B |
| 14 | [4280](/quote/tadawul/4280/) | Kingdom Holding Company | 49.29B | 13.30 | 0.00% | 2.76B |
| 15 | [1050](/quote/tadawul/1050/) | Banque Saudi Fransi | 48.73B | 19.71 | \-0.71% | 10.02B |
| 16 | [7203](/quote/tadawul/7203/) | Elm Company | 47.88B | 615.00 | 0.49% | 10.60B |
| 17 | [7020](/quote/tadawul/7020/) | Etihad Etisalat Company | 45.90B | 59.80 | 0.84% | 20.37B |
| 18 | [2280](/quote/tadawul/2280/) | Almarai Company | 43.70B | 43.70 | \-0.46% | 23.67B |
| 19 | [1080](/quote/tadawul/1080/) | Arab National Bank | 42.16B | 21.08 | \-0.85% | 9.70B |
| 20 | [4030](/quote/tadawul/4030/) | The National Shipping Company of Saudi Arabia | 32.26B | 34.96 | 0.58% | 29.36B |
| 21 | [2380](/quote/tadawul/2380/) | Rabigh Refining and Petrochemical Company | 31.97B | 14.55 | \-2.87% | 62.68B |
| 22 | [1140](/quote/tadawul/1140/) | Bank Albilad | 31.67B | 21.11 | \-0.57% | 6.15B |
| 23 | [4325](/quote/tadawul/4325/) | Umm Al Qura for Development and Construction Company | 23.29B | 16.19 | \-0.43% | 3.10B |
| 24 | [6015](/quote/tadawul/6015/) | Americana Restaurants International PLC | 23.17B | 2.690 | 0.75% | 10.31B |
| 25 | [4190](/quote/tadawul/4190/) | Jarir Marketing Company | 21.48B | 17.90 | 2.76% | 12.16B |
| 26 | [7202](/quote/tadawul/7202/) | Arabian Internet and Communication Services Company | 21.41B | 89.90 | 1.41% | 13.54B |
| 27 | [4300](/quote/tadawul/4300/) | Dar Al Arkan Real Estate Development Company | 20.95B | 19.40 | 0.05% | 4.57B |
| 28 | [8210](/quote/tadawul/8210/) | Bupa Arabia for Cooperative Insurance Company | 20.39B | 137.60 | \-1.15% | 22.21B |
| 29 | [8010](/quote/tadawul/8010/) | The Company for Cooperative Insurance | 19.85B | 88.50 | \-0.56% | 22.31B |
| 30 | [4250](/quote/tadawul/4250/) | Jabal Omar Development Company | 19.15B | 16.23 | \-0.55% | 2.36B |
| 31 | [2382](/quote/tadawul/2382/) | ADES Holding Company | 17.89B | 8.10 | \-3.57% | 8.76B |
| 32 | [2290](/quote/tadawul/2290/) | Yanbu National Petrochemical Company | 17.78B | 31.60 | 1.15% | 6.26B |
| 33 | [1030](/quote/tadawul/1030/) | The Saudi Investment Bank | 17.45B | 11.65 | 0.78% | 4.49B |
| 34 | [2223](/quote/tadawul/2223/) | Saudi Aramco Base Oil Company - Luberef | 17.23B | 102.40 | \-3.40% | 9.92B |
| 35 | [4142](/quote/tadawul/4142/) | Riyadh Cables Group Company | 15.51B | 103.40 | 1.37% | 11.66B |
| 36 | [1020](/quote/tadawul/1020/) | aljazira bank | 13.87B | 10.87 | \-0.91% | 4.43B |
| 37 | [4263](/quote/tadawul/4263/) | SAL Saudi Logistics Services Company | 13.71B | 171.40 | 0.23% | 2.05B |
| 38 | [1111](/quote/tadawul/1111/) | Saudi Tadawul Group Holding Company | 13.21B | 110.10 | 1.01% | 1.21B |
| 39 | [4100](/quote/tadawul/4100/) | Makkah Construction and Development Company | 12.92B | 64.60 | \-2.12% | 1.27B |
| 40 | [4164](/quote/tadawul/4164/) | Nahdi Medical Company | 12.23B | 94.05 | \-1.26% | 10.75B |
| 41 | [1303](/quote/tadawul/1303/) | Electrical Industries Company | 11.70B | 10.52 | \-1.13% | 2.70B |
| 42 | [2083](/quote/tadawul/2083/) | Power and Water Utility Company for Jubail and Yanbu | 11.50B | 46.00 | \-0.39% | 7.32B |
| 43 | [4002](/quote/tadawul/4002/) | Mouwasat Medical Services Company | 11.49B | 57.45 | 0.09% | 3.45B |
| 44 | [4200](/quote/tadawul/4200/) | Aldrees Petroleum and Transport Services Company | 10.92B | 109.20 | \-1.71% | 29.01B |
| 45 | [8313](/quote/tadawul/8313/) | Rasan Information Technology Company | 10.58B | 136.50 | \-2.36% | 972.29M |
| 46 | [1212](/quote/tadawul/1212/) | Astra Industrial Group Company | 9.52B | 119.00 | 1.10% | 2.94B |
| 47 | [8230](/quote/tadawul/8230/) | Al Rajhi Company for Cooperative Insurance | 9.50B | 47.64 | \-0.67% | 5.84B |
| 48 | [2381](/quote/tadawul/2381/) | Arabian Drilling Company | 8.88B | 99.80 | \-2.92% | 3.22B |
| 49 | [2310](/quote/tadawul/2310/) | Sahara International Petrochemical Company | 8.66B | 11.95 | \-0.25% | 5.09B |
| 50 | [2250](/quote/tadawul/2250/) | Saudi Industrial Investment Group | 8.33B | 12.46 | 1.47% | \- |
| 51 | [4090](/quote/tadawul/4090/) | Taiba Investment Company | 8.21B | 16.42 | 1.17% | 1.43B |
| 52 | [4015](/quote/tadawul/4015/) | Jamjoom Pharmaceuticals Factory Company | 8.20B | 117.10 | 0.09% | 1.59B |
| 53 | [7030](/quote/tadawul/7030/) | Mobile Telecommunications Company Saudi Arabia | 7.92B | 8.81 | \-0.23% | 11.03B |
| 54 | [7200](/quote/tadawul/7200/) | Al Moammar Information Systems Company | 7.54B | 251.40 | \-1.26% | 2.14B |
| 55 | [2350](/quote/tadawul/2350/) | Saudi Kayan Petrochemical Company | 7.53B | 5.02 | 0.00% | 7.70B |
| 56 | [2050](/quote/tadawul/2050/) | Savola Group Company | 7.02B | 23.44 | 0.13% | 26.69B |
| 57 | [4264](/quote/tadawul/4264/) | Flynas Company | 6.92B | 40.50 | \-1.36% | 8.23B |
| 58 | [4017](/quote/tadawul/4017/) | Dr. Soliman Abdel Kader Fakeeh Hospital Company | 6.87B | 29.88 | 0.95% | 3.25B |
| 59 | [4004](/quote/tadawul/4004/) | Dallah Healthcare Company | 6.77B | 56.10 | \-4.35% | 4.32B |
| 60 | [4321](/quote/tadawul/4321/) | Arabian Centres Company | 6.65B | 12.92 | 0.86% | 2.32B |
| 61 | [4310](/quote/tadawul/4310/) | Knowledge Economic City Company | 6.64B | 19.56 | 0.05% | 413.68M |
| 62 | [4220](/quote/tadawul/4220/) | Emaar The Economic City | 6.44B | 7.29 | 0.83% | 886.63M |
| 63 | [2330](/quote/tadawul/2330/) | Advanced Petrochemical Company | 6.09B | 23.55 | 2.30% | 4.05B |
| 64 | [2270](/quote/tadawul/2270/) | Saudia Dairy & Foodstuff Company | 6.01B | 188.10 | \-0.32% | 2.96B |
| 65 | [1322](/quote/tadawul/1322/) | Al Masane Al Kobra Mining Company | 5.38B | 59.80 | 0.93% | 1.02B |
| 66 | [4020](/quote/tadawul/4020/) | Saudi Real Estate Company | 5.34B | 14.25 | \-1.04% | 1.49B |
| 67 | [4072](/quote/tadawul/4072/) | MBC Group | 5.33B | 16.02 | \-1.72% | 4.50B |
| 68 | [2230](/quote/tadawul/2230/) | Saudi Chemical Holding Company | 5.21B | 6.18 | \-1.44% | 6.95B |
| 69 | [4005](/quote/tadawul/4005/) | National Medical Care Company | 5.01B | 112.00 | \-0.53% | 1.72B |
| 70 | [4084](/quote/tadawul/4084/) | Derayah Financial Company | 4.96B | 20.28 | 0.10% | 955.22M |
| 71 | [4161](/quote/tadawul/4161/) | BinDawood Holding Company | 4.89B | 4.290 | 0.00% | 6.84B |
| 72 | [4003](/quote/tadawul/4003/) | United Electronics Company | 4.87B | 66.00 | 0.76% | 7.75B |
| 73 | [1810](/quote/tadawul/1810/) | Seera Holding Group | 4.84B | 17.78 | \-0.61% | 4.47B |
| 74 | [1321](/quote/tadawul/1321/) | East Pipes Integrated Company for Industry | 4.78B | 151.70 | \-3.13% | 2.21B |
| 75 | [4018](/quote/tadawul/4018/) | Almoosa Health Company | 4.74B | 107.10 | 0.47% | 1.55B |
| 76 | [3040](/quote/tadawul/3040/) | Qassim Cement Company | 4.74B | 43.14 | 0.56% | 1.04B |
| 77 | [8200](/quote/tadawul/8200/) | Saudi Reinsurance Company | 4.68B | 28.00 | \-5.08% | 2.66B |
| 78 | [2060](/quote/tadawul/2060/) | National Industrialization Company | 4.65B | 7.05 | \-0.70% | 1.93B |
| 79 | [4291](/quote/tadawul/4291/) | National Company for Learning and Education | 4.62B | 107.40 | \-0.83% | 749.93M |
| 80 | [2080](/quote/tadawul/2080/) | National Gas and Industrialization Company | 4.59B | 61.20 | \-1.13% | 4.02B |
| 81 | [6004](/quote/tadawul/6004/) | CATRION Catering Holding Company | 4.47B | 54.50 | \-1.00% | 2.76B |
| 82 | [1830](/quote/tadawul/1830/) | Leejam Sports Company | 4.28B | 82.00 | \-1.20% | 1.66B |
| 83 | [3020](/quote/tadawul/3020/) | YAMAMA Cement Company | 3.91B | 19.30 | 0.78% | 1.46B |
| 84 | [4031](/quote/tadawul/4031/) | Saudi Ground Services Company | 3.86B | 20.55 | \-0.72% | 2.58B |
| 85 | [4210](/quote/tadawul/4210/) | Saudi Research and Media Group | 3.75B | 46.90 | \-3.46% | 2.85B |
| 86 | [3030](/quote/tadawul/3030/) | Saudi Cement Company | 3.73B | 24.38 | 0.04% | 1.65B |
| 87 | [4150](/quote/tadawul/4150/) | Arriyadh Development Co. | 3.60B | 15.40 | \-1.47% | 329.23M |
| 88 | [4322](/quote/tadawul/4322/) | Retal Urban Development Company | 3.49B | 6.99 | \-3.98% | 2.68B |
| 89 | [4007](/quote/tadawul/4007/) | Al Hammadi Holding Company | 3.47B | 21.70 | \-0.09% | 1.29B |
| 90 | [4001](/quote/tadawul/4001/) | Abdullah Al-Othaim Markets Company | 3.42B | 3.800 | 0.00% | 10.82B |
| 91 | [6010](/quote/tadawul/6010/) | The National Agricultural Development Company | 3.36B | 11.99 | \-0.75% | 3.55B |
| 92 | [2283](/quote/tadawul/2283/) | The First Milling Company | 3.32B | 59.90 | 1.01% | 1.32B |
| 93 | [2320](/quote/tadawul/2320/) | Al-Babtain Power and Telecommunications Company | 3.25B | 50.85 | \-3.69% | 3.11B |
| 94 | [4163](/quote/tadawul/4163/) | Al-Dawaa Medical Services Company | 3.19B | 37.56 | \-1.42% | 6.50B |
| 95 | [4165](/quote/tadawul/4165/) | Al Majed for Oud Company | 3.19B | 127.70 | 0.39% | 1.20B |
| 96 | [4019](/quote/tadawul/4019/) | Specialized Medical Company | 3.14B | 12.55 | \-0.40% | 1.59B |
| 97 | [2070](/quote/tadawul/2070/) | Saudi Pharmaceutical Industries and Medical Appliances Corporation | 3.03B | 25.42 | \-0.78% | 1.71B |
| 98 | [4162](/quote/tadawul/4162/) | Almunajem Foods Company | 3.00B | 50.00 | 0.64% | 3.29B |
| 99 | [2190](/quote/tadawul/2190/) | Sustained Infrastructure Holding Company | 2.99B | 36.74 | 0.11% | 2.48B |
| 100 | [4260](/quote/tadawul/4260/) | United International Transportation Company | 2.86B | 27.32 | \-1.51% | 2.61B |
| 101 | [2081](/quote/tadawul/2081/) | Alkhorayef Water and Power Technologies Company | 2.80B | 80.10 | 0.50% | 2.15B |
| 102 | [7040](/quote/tadawul/7040/) | Etihad GO Telecom Co. | 2.59B | 76.30 | \-1.80% | 2.12B |
| 103 | [4071](/quote/tadawul/4071/) | Arabian Contracting Services Company | 2.46B | 44.68 | \-1.37% | 1.61B |
| 104 | [4050](/quote/tadawul/4050/) | Saudi Automotive Services Company | 2.43B | 34.74 | \-2.03% | 12.74B |
| 105 | [4327](/quote/tadawul/4327/) | Al Ramz Real Estate Company | 2.33B | 54.35 | \-1.09% | 1.51B |
| 106 | [4009](/quote/tadawul/4009/) | Middle East Healthcare Company | 2.32B | 25.24 | \-0.63% | 3.30B |
| 107 | [4016](/quote/tadawul/4016/) | Middle East Pharmaceutical Industries Company | 2.28B | 65.20 | \-0.91% | 528.49M |
| 108 | [1320](/quote/tadawul/1320/) | Saudi Steel Pipes Company | 2.27B | 44.92 | \-1.40% | 1.34B |
| 109 | [3050](/quote/tadawul/3050/) | Southern Province Cement Company | 2.26B | 16.14 | 0.81% | 874.65M |
| 110 | [3092](/quote/tadawul/3092/) | Riyadh Cement Company | 2.24B | 18.65 | 1.14% | 784.66M |
| 111 | [2284](/quote/tadawul/2284/) | Modern Mills Company | 2.21B | 27.26 | 0.15% | 1.18B |
| 112 | [6019](/quote/tadawul/6019/) | Almasar Alshamil Education Company JSC | 2.19B | 21.40 | \-0.47% | 603.36M |
| 113 | [4146](/quote/tadawul/4146/) | Gas Arabian Services Company | 2.19B | 13.85 | 2.29% | 1.54B |
| 114 | [4340](/quote/tadawul/4340/) | Al Rajhi REIT Fund | 2.16B | 7.83 | 0.26% | 235.75M |
| 115 | [2286](/quote/tadawul/2286/) | Fourth Milling Company | 2.05B | 3.800 | 0.53% | 719.33M |
| 116 | [2285](/quote/tadawul/2285/) | Arabian Mills for Food Products Company | 2.03B | 39.50 | 0.77% | 1.03B |
| 117 | [3080](/quote/tadawul/3080/) | Eastern Province Cement Company | 2.02B | 23.50 | \-0.34% | 1.36B |
| 118 | [2040](/quote/tadawul/2040/) | Saudi Ceramic Company | 2.02B | 20.27 | \-0.64% | 1.63B |
| 119 | [3060](/quote/tadawul/3060/) | Yanbu Cement Company | 2.01B | 12.74 | 0.24% | 911.55M |
| 120 | [4192](/quote/tadawul/4192/) | Al-Saif Stores for Development & Investment Company | 1.98B | 5.66 | \-2.08% | 792.56M |
| 121 | [7211](/quote/tadawul/7211/) | Saudi Azm for Communication and Information Technology Company | 1.98B | 33.98 | \-2.07% | 341.82M |
| 122 | [1831](/quote/tadawul/1831/) | Maharah for Human Resources Company | 1.88B | 3.300 | 0.00% | 3.66B |
| 123 | [9557](/quote/tadawul/9557/) | Edarat Communication and Information Technology Co. | 1.87B | 247.50 | 1.02% | 208.85M |
| 124 | [6017](/quote/tadawul/6017/) | Jahez International Company for Information Systems Technology | 1.83B | 9.02 | \-1.64% | 2.93B |
| 125 | [1834](/quote/tadawul/1834/) | Saudi Manpower Solutions Company | 1.80B | 4.490 | \-0.66% | 2.21B |
| 126 | [6022](/quote/tadawul/6022/) | Armah Sports Company | 1.79B | 54.35 | \-1.36% | 242.12M |
| 127 | [8030](/quote/tadawul/8030/) | The Mediterranean and Gulf Cooperative Insurance and Reinsurance Company | 1.77B | 12.80 | \-0.16% | 5.37B |
| 128 | [3010](/quote/tadawul/3010/) | Arabian Cement Company | 1.76B | 17.57 | \-0.34% | 1.01B |
| 129 | [2300](/quote/tadawul/2300/) | Saudi Paper Manufacturing Company | 1.64B | 44.44 | \-0.63% | 972.91M |
| 130 | [1833](/quote/tadawul/1833/) | Almawarid Manpower Company | 1.64B | 82.00 | \-2.03% | 3.04B |
| 131 | [2170](/quote/tadawul/2170/) | Alujain Corporation | 1.59B | 22.93 | \-0.26% | 1.69B |
| 132 | [1304](/quote/tadawul/1304/) | Al Yamamah Steel Industries Company | 1.58B | 31.18 | \-1.20% | 1.98B |
| 133 | [9540](/quote/tadawul/9540/) | National Environmental Recycling Company | 1.57B | 6.90 | \-1.99% | 2.41B |
| 134 | [4083](/quote/tadawul/4083/) | United International Holding Company | 1.52B | 20.20 | \-0.93% | 511.57M |
| 135 | [7204](/quote/tadawul/7204/) | Perfect Presentation for Commercial Services Company | 1.49B | 4.520 | 2.26% | 1.31B |
| 136 | [4326](/quote/tadawul/4326/) | Dar Al Majed Real Estate Company | 1.49B | 4.950 | \-3.32% | 1.01B |
| 137 | [8250](/quote/tadawul/8250/) | Gulf Insurance Group | 1.48B | 28.14 | 1.15% | 1.92B |
| 138 | [9523](/quote/tadawul/9523/) | Group Five Pipe Saudi Company | 1.46B | 52.05 | \-1.98% | 2.05B |
| 139 | [1302](/quote/tadawul/1302/) | Bawan Company | 1.40B | 23.34 | \-1.64% | 3.98B |
| 140 | [2084](/quote/tadawul/2084/) | Miahona Company Limited | 1.38B | 8.57 | \-1.38% | 497.22M |
| 141 | [3003](/quote/tadawul/3003/) | City Cement Company | 1.37B | 9.81 | \-0.20% | 445.61M |
| 142 | [4323](/quote/tadawul/4323/) | Sumou Real Estate Company | 1.36B | 27.20 | \-1.59% | 667.94M |
| 143 | [8060](/quote/tadawul/8060/) | Walaa Cooperative Insurance Company | 1.32B | 10.38 | \-1.24% | 1.21B |
| 144 | [4320](/quote/tadawul/4320/) | Alandalus Property Company | 1.32B | 14.12 | \-0.35% | 267.26M |
| 145 | [2110](/quote/tadawul/2110/) | Saudi Cable Company | 1.32B | 197.40 | \-0.95% | 110.96M |
| 146 | [2240](/quote/tadawul/2240/) | Advanced Building Industries Co. | 1.31B | 21.79 | \-0.50% | 5.99B |
| 147 | [4240](/quote/tadawul/4240/) | AFG International Company | 1.26B | 10.95 | \-1.88% | 5.34B |
| 148 | [4012](/quote/tadawul/4012/) | Thob Al Aseel Company | 1.26B | 3.140 | 0.32% | 570.59M |
| 149 | [4040](/quote/tadawul/4040/) | Saudi Public Transport Company | 1.22B | 9.78 | \-1.21% | 1.99B |
| 150 | [2370](/quote/tadawul/2370/) | Middle East Specialized Cables Company | 1.22B | 30.54 | \-0.91% | 1.73B |
| 151 | [2282](/quote/tadawul/2282/) | Naqi Water Company | 1.22B | 60.85 | \-0.16% | 217.38M |
| 152 | [4344](/quote/tadawul/4344/) | SEDCO Capital REIT Fund | 1.21B | 6.48 | 0.00% | 295.50M |
| 153 | [1183](/quote/tadawul/1183/) | SHL Finance Company | 1.19B | 11.90 | \-0.42% | 229.31M |
| 154 | [4292](/quote/tadawul/4292/) | Ataa Educational Company | 1.19B | 28.20 | \-1.40% | 668.94M |
| 155 | [2150](/quote/tadawul/2150/) | The National Company for Glass Industries | 1.18B | 35.96 | \-0.94% | 134.66M |
| 156 | [4143](/quote/tadawul/4143/) | Al Taiseer Group TALCO Industrial Company | 1.18B | 29.56 | \-1.60% | 862.54M |
| 157 | [1202](/quote/tadawul/1202/) | Middle East Company for Manufacturing and Producing Paper | 1.18B | 13.61 | \-2.92% | 1.07B |
| 158 | [6014](/quote/tadawul/6014/) | Alamar Foods Company | 1.18B | 46.50 | 0.04% | 1.07B |
| 159 | [4261](/quote/tadawul/4261/) | Theeb Rent A Car Company | 1.18B | 17.82 | \-1.98% | 1.67B |
| 160 | [1323](/quote/tadawul/1323/) | United Carton Industries Company | 1.14B | 28.54 | \-1.59% | 1.49B |
| 161 | [3004](/quote/tadawul/3004/) | Northern Region Cement Company | 1.14B | 6.32 | \-0.32% | 879.36M |
| 162 | [4262](/quote/tadawul/4262/) | Lumi Rental Company | 1.12B | 20.44 | \-2.34% | 1.65B |
| 163 | [2200](/quote/tadawul/2200/) | Arabian Pipes Company | 1.11B | 4.400 | \-2.44% | 633.86M |
| 164 | [1820](/quote/tadawul/1820/) | BAAN Holding Group Company | 1.05B | 1.700 | 0.00% | 599.93M |
| 165 | [4193](/quote/tadawul/4193/) | Nice One Beauty Digital Marketing Company | 1.04B | 9.00 | \-0.88% | 990.31M |
| 166 | [9601](/quote/tadawul/9601/) | Mohammed Hadi Al-Rasheed Company | 1.04B | 57.70 | 3.04% | 429.28M |
| 167 | [6070](/quote/tadawul/6070/) | Al-Jouf Agricultural Development Co. | 1.02B | 34.06 | \-0.41% | 730.67M |
| 168 | [6018](/quote/tadawul/6018/) | Sport Clubs Company | 1.00B | 8.77 | \-0.23% | 423.01M |
| 169 | [2281](/quote/tadawul/2281/) | Tanmiah Food Company | 996.40M | 49.82 | \-2.22% | 3.01B |
| 170 | [4081](/quote/tadawul/4081/) | Nayifat Finance Company | 982.94M | 8.43 | \-0.82% | 64.37M |
| 171 | [4110](/quote/tadawul/4110/) | Batic Investments and Logistics Company | 954.00M | 1.590 | 0.00% | 526.97M |
| 172 | [1835](/quote/tadawul/1835/) | Tamkeen Human Resources Company | 939.69M | 35.46 | \-1.45% | 1.09B |
| 173 | [4144](/quote/tadawul/4144/) | Raoom trading Company | 912.50M | 73.00 | \-5.13% | 100.91M |
| 174 | [9541](/quote/tadawul/9541/) | Academy of Learning Company | 904.50M | 6.70 | \-2.90% | 283.50M |
| 175 | [4230](/quote/tadawul/4230/) | Red Sea International Company | 897.29M | 18.59 | \-1.64% | 2.52B |
| 176 | [9618](/quote/tadawul/9618/) | Al-Fakhera Men's Tailoring Company | 892.80M | 24.80 | \-0.40% | 164.79M |
| 177 | [8070](/quote/tadawul/8070/) | Arabian Shield Cooperative Insurance Company | 867.59M | 10.87 | 0.00% | 1.54B |
| 178 | [4328](/quote/tadawul/4328/) | Ladun Investment Company | 860.00M | 1.720 | 0.58% | 670.06M |
| 179 | [4080](/quote/tadawul/4080/) | Sinad Holding Company | 855.65M | 6.77 | \-3.15% | 1.82B |
| 180 | [6001](/quote/tadawul/6001/) | Halwani Bros. Co. Ltd. | 854.94M | 24.18 | 0.25% | 926.45M |
| 181 | [6002](/quote/tadawul/6002/) | Herfy Food Services Company | 854.42M | 13.21 | \-0.08% | 1.05B |
| 182 | [9517](/quote/tadawul/9517/) | MOBI Industry Co. | 845.00M | 16.90 | 0.90% | 280.95M |
| 183 | [3002](/quote/tadawul/3002/) | Najran Cement Company | 835.33M | 5.07 | \-0.39% | 491.02M |
| 184 | [4014](/quote/tadawul/4014/) | Scientific and Medical Equipment House Company | 828.60M | 27.62 | 1.02% | 784.46M |
| 185 | [9521](/quote/tadawul/9521/) | INMAR Company | 828.00M | 20.70 | \-1.43% | 168.53M |
| 186 | [1182](/quote/tadawul/1182/) | Amlak International Finance Company | 788.90M | 7.74 | \-0.39% | 313.28M |
| 187 | [9559](/quote/tadawul/9559/) | Balady Poultry Company | 788.40M | 120.00 | 0.00% | 808.41M |
| 188 | [9510](/quote/tadawul/9510/) | National Building and Marketing Co. | 786.60M | 65.55 | 0.00% | 874.94M |
| 189 | [4145](/quote/tadawul/4145/) | Al Obeikan Glass Company | 771.52M | 24.11 | 0.12% | 401.42M |
| 190 | [9583](/quote/tadawul/9583/) | United Mining Industries Company | 756.00M | 54.00 | 3.45% | 220.91M |
| 191 | [2140](/quote/tadawul/2140/) | Ayyan Investment Company | 736.66M | 7.32 | \-1.35% | \-238.59M |
| 192 | [2120](/quote/tadawul/2120/) | Saudi Advanced Industries Company | 716.26M | 12.14 | \-1.46% | \-13.12M |
| 193 | [4147](/quote/tadawul/4147/) | Consolidated Grunenfelder Saady Holding Company | 716.00M | 7.16 | \-0.69% | 519.86M |
| 194 | [7205](/quote/tadawul/7205/) | Dar AlBalad for Business Solutions Company | 696.40M | 10.10 | 0.50% | 332.94M |
| 195 | [9649](/quote/tadawul/9649/) | Jamjoom Fashion Trading Company | 694.64M | 87.40 | 0.00% | 777.88M |
| 196 | [2030](/quote/tadawul/2030/) | Saudi Arabian Refineries Company | 693.00M | 46.20 | \-0.65% | \-47.55M |
| 197 | [4330](/quote/tadawul/4330/) | Riyad REIT Fund | 678.20M | 3.950 | \-1.00% | 270.80M |
| 198 | [4290](/quote/tadawul/4290/) | Al Khaleej Training and Education Company | 667.55M | 10.27 | \-1.34% | 1.11B |
| 199 | [2340](/quote/tadawul/2340/) | Artex Industrial Investment Company | 662.19M | 8.15 | \-2.74% | 530.03M |
| 200 | [1324](/quote/tadawul/1324/) | Saleh Abdulaziz Al Rashed & Sons Co. | 657.70M | 35.36 | 1.03% | 727.78M |
| 201 | [1210](/quote/tadawul/1210/) | Basic Chemical Industries Company | 646.25M | 23.50 | \-0.63% | 784.32M |
| 202 | [9544](/quote/tadawul/9544/) | Future Care Trading Co. | 605.00M | 1.210 | \-0.82% | 92.50M |
| 203 | [4148](/quote/tadawul/4148/) | Alwasail Industrial Company | 602.50M | 2.410 | \-1.23% | 424.27M |
| 204 | [2288](/quote/tadawul/2288/) | Nofoth Food Products Company | 596.60M | 6.30 | \-0.16% | 436.21M |
| 205 | [4191](/quote/tadawul/4191/) | Abdullah Saad Mohammed Abo Moati for Bookstores Company | 596.00M | 29.80 | \-2.23% | 258.45M |
| 206 | [4170](/quote/tadawul/4170/) | Tourism Enterprise Company (Shams) | 595.58M | 10.30 | \-1.90% | 9.70M |
| 207 | [4180](/quote/tadawul/4180/) | Fitaihi Holding Group | 580.25M | 2.110 | \-0.47% | 46.16M |
| 208 | [8012](/quote/tadawul/8012/) | Aljazira Takaful Taawuni Company | 578.16M | 8.76 | 0.23% | 367.23M |
| 209 | [4265](/quote/tadawul/4265/) | Cherry Trading Company | 577.80M | 19.26 | \-0.87% | 656.67M |
| 210 | [4194](/quote/tadawul/4194/) | Marketing Home Group Company for Trading Company | 575.36M | 35.96 | \-0.94% | 381.55M |
| 211 | [1214](/quote/tadawul/1214/) | Al Hassan Ghazi Ibrahim Shaker Company | 563.44M | 8.46 | \-0.47% | 1.38B |
| 212 | [8120](/quote/tadawul/8120/) | Gulf Union Alahlia Cooperative Insurance Company | 561.29M | 12.23 | \-0.41% | 839.45M |
| 213 | [4324](/quote/tadawul/4324/) | Banan Real Estate Company | 560.00M | 2.800 | \-1.06% | 76.36M |
| 214 | [9640](/quote/tadawul/9640/) | ASAS Makeen Real Estate Development and Investment Company | 558.60M | 18.62 | 0.00% | 484.39M |
| 215 | [9655](/quote/tadawul/9655/) | MSGA Investment Company | 557.78M | 5.02 | \-5.64% | 160.46M |
| 216 | [2287](/quote/tadawul/2287/) | Arabian Company for Agricultural and Industrial Investment | 552.00M | 18.40 | \-0.92% | 1.62B |
| 217 | [3007](/quote/tadawul/3007/) | Zahrat Al Waha For Trading Company | 546.75M | 2.430 | \-1.22% | 591.51M |
| 218 | [8240](/quote/tadawul/8240/) | Chubb Arabia Cooperative Insurance Company | 546.40M | 13.66 | \-0.80% | 458.96M |
| 219 | [8300](/quote/tadawul/8300/) | Wataniya Insurance Company | 537.20M | 13.43 | 1.05% | 2.65B |
| 220 | [4082](/quote/tadawul/4082/) | Morabaha Marina Financing Company | 534.84M | 7.66 | 0.00% | 66.25M |
| 221 | [8280](/quote/tadawul/8280/) | Liva Insurance Company | 513.60M | 12.84 | 0.39% | 901.00M |
| 222 | [9527](/quote/tadawul/9527/) | Alf Meem Yaa for Medical Supplies and Equipment Company | 513.45M | 73.35 | 2.88% | 314.29M |
| 223 | [8040](/quote/tadawul/8040/) | Mutakamela Insurance Company | 511.60M | 8.60 | \-1.71% | 621.81M |
| 224 | [4333](/quote/tadawul/4333/) | Taleem REIT Fund | 510.51M | 10.01 | 0.50% | 67.64M |
| 225 | [4008](/quote/tadawul/4008/) | Saudi Company for Hardware SACO | 509.54M | 14.28 | \-0.14% | 979.42M |
| 226 | [9637](/quote/tadawul/9637/) | Axelerated Solutions for Information and Communication Technology Company | 506.80M | 9.05 | 0.56% | 470.87M |
| 227 | [3005](/quote/tadawul/3005/) | Umm Al-Qura Cement Company | 506.00M | 9.20 | \-0.54% | 309.55M |
| 228 | [3090](/quote/tadawul/3090/) | Tabuk Cement Company | 496.80M | 5.52 | \-1.60% | 263.14M |
| 229 | [9610](/quote/tadawul/9610/) | First Avenue Real Estate Development Company | 494.06M | 1.730 | 0.00% | 231.38M |
| 230 | [1325](/quote/tadawul/1325/) | Watani Iron Steel Company | 490.46M | 2.700 | \-0.74% | 586.20M |
| 231 | [9546](/quote/tadawul/9546/) | Naba Al Saha Medical Services Company | 489.30M | 23.30 | 0.00% | 206.15M |
| 232 | [4051](/quote/tadawul/4051/) | Baazeem Trading Company | 488.03M | 4.820 | 0.42% | 286.79M |
| 233 | [9634](/quote/tadawul/9634/) | Adeer Real Estate Company | 477.25M | 95.45 | \-0.57% | 151.25M |
| 234 | [9628](/quote/tadawul/9628/) | Lamasat Company | 477.09M | 5.89 | 0.00% | 148.77M |
| 235 | [1301](/quote/tadawul/1301/) | United Wire Factories Company | 468.94M | 16.70 | \-1.76% | 747.08M |
| 236 | [4011](/quote/tadawul/4011/) | L'azurde Company for Jewelry | 465.18M | 8.09 | \-0.12% | 3.57B |
| 237 | [9596](/quote/tadawul/9596/) | Quara Finance Company | 465.00M | 15.50 | 3.33% | 157.19M |
| 238 | [2130](/quote/tadawul/2130/) | Saudi Industrial Development Co. | 461.10M | 15.37 | \-3.33% | 84.46M |
| 239 | [9552](/quote/tadawul/9552/) | Saudi Top for Trading Company | 456.00M | 11.40 | \-0.87% | 153.93M |
| 240 | [9543](/quote/tadawul/9543/) | Saudi Networkers Services Company | 455.25M | 60.70 | \-0.41% | 587.21M |
| 241 | [3091](/quote/tadawul/3091/) | Al Jouf Cement Company | 453.28M | 4.170 | \-0.24% | 177.28M |
| 242 | [2210](/quote/tadawul/2210/) | Nama Chemicals Company | 440.76M | 18.74 | 0.00% | 235.83M |
| 243 | [8020](/quote/tadawul/8020/) | Malath Cooperative Insurance Company | 436.50M | 8.73 | \-2.02% | 1.16B |
| 244 | [4006](/quote/tadawul/4006/) | Saudi Marketing Company | 430.20M | 9.56 | 0.42% | 1.70B |
| 245 | [9514](/quote/tadawul/9514/) | Mohammed Hasan AlNaqool Sons Co. | 425.72M | 73.40 | 0.14% | 80.65M |
| 246 | [9560](/quote/tadawul/9560/) | Waja Company | 422.80M | 6.04 | 0.00% | 135.47M |
| 247 | [9568](/quote/tadawul/9568/) | Mayar Holding Company | 419.89M | 3.500 | 0.00% | 380.83M |
| 248 | [9575](/quote/tadawul/9575/) | Marble Design Factory Company | 412.50M | 5.50 | 0.00% | 39.49M |
| 249 | [4336](/quote/tadawul/4336/) | Mulkia Gulf Real Estate REIT | 409.88M | 3.950 | \-1.25% | 123.14M |
| 250 | [2160](/quote/tadawul/2160/) | The Saudi Arabian Amiantit Company | 402.84M | 9.05 | \-1.63% | 405.66M |
| 251 | [2180](/quote/tadawul/2180/) | Filling and Packing Materials Manufacturing Company | 401.35M | 34.90 | \-0.29% | 295.64M |
| 252 | [9611](/quote/tadawul/9611/) | Arabian United Float Glass Company | 401.29M | 23.60 | 0.43% | 295.41M |
| 253 | [2100](/quote/tadawul/2100/) | Wafrah for Industry and Development Company | 394.49M | 17.04 | 0.35% | 112.72M |
| 254 | [4130](/quote/tadawul/4130/) | Darb Saudi Investment Company | 382.02M | 1.750 | \-0.57% | 16.35M |
| 255 | [9607](/quote/tadawul/9607/) | ASG Plastic Factory Company | 366.60M | 26.00 | 0.00% | 232.89M |
| 256 | [1832](/quote/tadawul/1832/) | Sadr Logistics Company | 365.75M | 2.090 | \-0.95% | 162.53M |
| 257 | [9639](/quote/tadawul/9639/) | Anmat Technology for Trading Co. | 365.50M | 8.50 | 0.00% | 380.22M |
| 258 | [4140](/quote/tadawul/4140/) | Saudi Industrial Export Company | 365.47M | 1.880 | 0.00% | 249.56K |
| 259 | [7201](/quote/tadawul/7201/) | Arab Sea Information Systems Company | 365.00M | 3.650 | 1.11% | 57.83M |
| 260 | [9580](/quote/tadawul/9580/) | Al Rashid Industrial Co., | 364.80M | 30.40 | \-0.39% | 188.26M |
| 261 | [6050](/quote/tadawul/6050/) | Saudi Fisheries Company | 355.03M | 53.00 | \-0.09% | 862.81K |
| 262 | [4061](/quote/tadawul/4061/) | Anaam International Holding Group Company | 343.35M | 10.90 | \-1.00% | 34.51M |
| 263 | [9627](/quote/tadawul/9627/) | Twareat Medical Care Company | 340.00M | 8.50 | 0.00% | 242.15M |
| 264 | [4070](/quote/tadawul/4070/) | Tihama for Advertising, Public Relations and Marketing Company | 338.55M | 14.77 | \-5.92% | 32.96M |
| 265 | [9530](/quote/tadawul/9530/) | Arabian International Healthcare Holding Company | 336.43M | 17.00 | 0.00% | 840.73M |
| 266 | [9614](/quote/tadawul/9614/) | Purity for Information Technology Company | 335.60M | 16.78 | \-0.12% | 98.55M |
| 267 | [6060](/quote/tadawul/6060/) | Ash-Sharqiyah Development Co. | 335.40M | 11.18 | \-1.24% | 218.91M |
| 268 | [4021](/quote/tadawul/4021/) | Canadian General Medical Center Complex Company | 325.18M | 4.230 | \-1.17% | 142.93M |
| 269 | [9613](/quote/tadawul/9613/) | Shalfa Facilities Management Company | 323.40M | 77.00 | 5.41% | 615.24M |
| 270 | [2090](/quote/tadawul/2090/) | National Gypsum Company | 318.57M | 10.06 | \-1.85% | 86.14M |
| 271 | [8160](/quote/tadawul/8160/) | Arabia Insurance Cooperative Company | 316.94M | 5.98 | \-0.83% | 821.39M |
| 272 | [2220](/quote/tadawul/2220/) | National Metal Manufacturing and Casting Co. | 316.12M | 8.93 | \-1.11% | 200.82M |
| 273 | [9625](/quote/tadawul/9625/) | Itmam Consultancy Company | 314.79M | 14.99 | 3.38% | 70.66M |
| 274 | [6016](/quote/tadawul/6016/) | Shatirah House Restaurant Co. | 313.60M | 5.60 | \-1.41% | 437.93M |
| 275 | [9548](/quote/tadawul/9548/) | Arabian Plastic Industrial Company Limited | 313.60M | 31.36 | 2.82% | 212.43M |
| 276 | [6090](/quote/tadawul/6090/) | Jazan Development and Investment Company | 311.00M | 6.22 | \-0.64% | 112.22M |
| 277 | [6020](/quote/tadawul/6020/) | Al Gassim Investment Holding Company | 309.00M | 10.30 | \-1.62% | 7.88M |
| 278 | [2001](/quote/tadawul/2001/) | Methanol Chemicals Company | 304.50M | 20.30 | \-1.93% | 583.97M |
| 279 | [9594](/quote/tadawul/9594/) | Al-Modawat Specialized Medical Company | 285.00M | 4.000 | 0.00% | 138.96M |
| 280 | [9564](/quote/tadawul/9564/) | Horizon Food Company Limited | 279.68M | 34.96 | 0.00% | 91.92M |
| 281 | [1213](/quote/tadawul/1213/) | Naseej International Trading Company | 279.24M | 10.25 | \-2.47% | 20.11M |
| 282 | [9550](/quote/tadawul/9550/) | Sure Global Tech Co. | 278.48M | 37.00 | 0.00% | 262.15M |
| 283 | [9574](/quote/tadawul/9574/) | Professional Medical Expertise Company | 274.05M | 78.30 | 0.00% | 441.45M |
| 284 | [8100](/quote/tadawul/8100/) | Saudi Arabian Cooperative Insurance Company | 269.10M | 8.97 | \-0.33% | 1.10B |
| 285 | [4270](/quote/tadawul/4270/) | Saudi Printing and Packaging Co. | 267.82M | 38.82 | \-2.71% | 451.16M |
| 286 | [4335](/quote/tadawul/4335/) | Musharaka REIT Fund | 267.52M | 3.040 | 1.00% | 95.39M |
| 287 | [9600](/quote/tadawul/9600/) | Qomel Company Limited | 262.50M | 37.50 | 7.14% | 121.66M |
| 288 | [9641](/quote/tadawul/9641/) | Hawyia Auctions Company | 260.00M | 13.00 | 0.00% | 47.80M |
| 289 | [9566](/quote/tadawul/9566/) | Saudi Lime Industries Company | 258.72M | 11.20 | 6.67% | 232.03M |
| 290 | [9631](/quote/tadawul/9631/) | Hedab Alkhaleej Trading Co. | 255.00M | 34.00 | 0.00% | 583.74M |
| 291 | [1201](/quote/tadawul/1201/) | Takween Advanced Industries | 252.33M | 3.300 | 0.61% | 805.99M |
| 292 | [8180](/quote/tadawul/8180/) | Al Sagr Cooperative Insurance Company | 252.00M | 8.40 | \-1.52% | 651.94M |
| 293 | [6040](/quote/tadawul/6040/) | Tabuk Agricultural Development Company | 247.94M | 32.40 | 1.19% | 7.11M |
| 294 | [8170](/quote/tadawul/8170/) | Al-Etihad Cooperative Insurance Company | 238.00M | 4.760 | \-1.86% | 1.13B |
| 295 | [9585](/quote/tadawul/9585/) | Mulkia Investment Company | 234.00M | 30.00 | \-8.76% | 38.70M |
| 296 | [4141](/quote/tadawul/4141/) | Al-Omran Industrial Trading Company | 229.20M | 19.10 | \-1.90% | 107.95M |
| 297 | [9576](/quote/tadawul/9576/) | Paper Home Company | 220.20M | 36.70 | \-8.66% | 111.05M |
| 298 | [3008](/quote/tadawul/3008/) | Al Kathiri Holding Company | 217.50M | 11.27 | \-4.73% | 159.07M |
| 299 | [9602](/quote/tadawul/9602/) | Yaqeen Capital Company | 217.01M | 8.51 | 0.12% | 62.52M |
| 300 | [9650](/quote/tadawul/9650/) | Sahat Almajd Trading Company | 216.56M | 5.50 | \-8.33% | \- |
| 301 | [9569](/quote/tadawul/9569/) | AlMuneef Company for Trade, Industry, Agriculture and Contracting | 216.03M | 3.790 | \-1.56% | 218.16M |
| 302 | [9598](/quote/tadawul/9598/) | Al Mohafaza Company for Education | 213.76M | 26.72 | 0.00% | 39.18M |
| 303 | [8310](/quote/tadawul/8310/) | Amana Cooperative Insurance Company | 206.40M | 4.800 | \-4.00% | 350.54M |
| 304 | [6013](/quote/tadawul/6013/) | Development Works Food Company | 201.60M | 67.20 | 1.66% | 91.32M |
| 305 | [9545](/quote/tadawul/9545/) | International Human Resources Company | 200.00M | 4.000 | 2.04% | 409.70M |
| 306 | [9603](/quote/tadawul/9603/) | Horizon Educational Company | 196.25M | 78.50 | 0.00% | 67.90M |
| 307 | [9563](/quote/tadawul/9563/) | BENA Steel Industries | 191.40M | 31.90 | 0.00% | 444.51M |
| 308 | [9592](/quote/tadawul/9592/) | Almujtama Alraida Medical Co. | 188.77M | 19.87 | \-0.65% | \- |
| 309 | [8311](/quote/tadawul/8311/) | Saudi Enaya Cooperative Insurance Company | 188.37M | 8.19 | 2.38% | 162.99M |
| 310 | [9648](/quote/tadawul/9648/) | Hamad Mohammed Bin Saedan Real Estate Company | 187.76M | 6.65 | \-2.64% | 47.88M |
| 311 | [2360](/quote/tadawul/2360/) | Saudi Vitrified Clay Pipe Company | 181.99M | 40.06 | \-1.33% | 66.89M |
| 312 | [9604](/quote/tadawul/9604/) | Miral Dental Company | 180.70M | 90.35 | 0.00% | \- |
| 313 | [8050](/quote/tadawul/8050/) | Salama Cooperative Insurance Company | 179.70M | 5.99 | \-0.33% | 718.29M |
| 314 | [4160](/quote/tadawul/4160/) | Thimar Development Holding Company | 175.37M | 26.98 | \-1.17% | 1.95M |
| 315 | [9570](/quote/tadawul/9570/) | Tam Development Company | 175.05M | 52.65 | \-1.59% | 153.05M |
| 316 | [9516](/quote/tadawul/9516/) | Natural Gas Distribution Company | 173.50M | 34.70 | 0.64% | 153.58M |
| 317 | [8150](/quote/tadawul/8150/) | Allied Cooperative Insurance Group | 167.91M | 5.77 | \-1.03% | 1.19B |
| 318 | [9593](/quote/tadawul/9593/) | Pan Gulf Marketing Company | 165.00M | 22.00 | 0.00% | 342.36M |
| 319 | [9532](/quote/tadawul/9532/) | Aljouf Mineral Water Bottling Co. | 160.31M | 1.710 | \-1.72% | 71.09M |
| 320 | [9636](/quote/tadawul/9636/) | Al Kuzama Trading Co | 156.20M | 39.62 | 0.00% | 313.28M |
| 321 | [9591](/quote/tadawul/9591/) | View United Real Estate Development Co. | 151.14M | 2.290 | 11.71% | 44.72M |
| 322 | [9558](/quote/tadawul/9558/) | Alqemam for Computer Systems Co. | 147.00M | 49.00 | 6.52% | 64.28M |
| 323 | [9615](/quote/tadawul/9615/) | Mufeed Company | 145.20M | 22.00 | 0.00% | 115.82M |
| 324 | [9551](/quote/tadawul/9551/) | Knowledge Tower Trading Company | 143.50M | 8.20 | \-8.28% | 24.87M |
| 325 | [9547](/quote/tadawul/9547/) | Rawasi Albina Investment Co. | 137.50M | 2.500 | \-11.66% | 129.26M |
| 326 | [8190](/quote/tadawul/8190/) | United Cooperative Assurance Company | 135.20M | 3.380 | 0.90% | 618.35M |
| 327 | [9624](/quote/tadawul/9624/) | Alshehili Company for metal industries | 128.63M | 51.45 | \-1.06% | 72.28M |
| 328 | [9612](/quote/tadawul/9612/) | SAMA Healthy Water Factory company | 126.50M | 2.530 | 0.00% | 86.69M |
| 329 | [9626](/quote/tadawul/9626/) | Basma Adeem Medical company | 123.28M | 6.70 | 0.00% | 54.93M |
| 330 | [9542](/quote/tadawul/9542/) | Keir International Co. | 121.20M | 1.010 | 0.00% | 181.00M |
| 331 | [9538](/quote/tadawul/9538/) | Naseej for Technology Co. | 119.80M | 16.04 | \-1.78% | 226.86M |
| 332 | [9581](/quote/tadawul/9581/) | Clean Life Company | 119.25M | 79.50 | 0.00% | 66.70M |
| 333 | [4331](/quote/tadawul/4331/) | Aljazira Mawten REIT Fund | 118.12M | 10.01 | \-0.50% | 7.13M |
| 334 | [9588](/quote/tadawul/9588/) | Riyadh Steel Company | 112.00M | 1.600 | 3.23% | 138.80M |
| 335 | [9606](/quote/tadawul/9606/) | Altharwah Albashariyyah Co. | 105.88M | 22.50 | 0.00% | 123.95M |
| 336 | [9549](/quote/tadawul/9549/) | Abdulaziz and Mansour Ibrahim Albabtin Co. | 101.93M | 29.98 | 0.00% | 250.56M |
| 337 | [9644](/quote/tadawul/9644/) | Naf Company for Feed for Industry | 100.00M | 5.00 | 0.00% | 138.96M |
| 338 | [9555](/quote/tadawul/9555/) | Leen Alkhair Trading Company | 98.73M | 12.10 | 0.00% | 236.21M |
| 339 | [6012](/quote/tadawul/6012/) | Raydan Food Company | 98.51M | 13.47 | \-2.53% | 60.80M |
| 340 | [9635](/quote/tadawul/9635/) | Dkhoun National Trading Company | 97.04M | 48.52 | \-7.05% | 87.97M |
| 341 | [9522](/quote/tadawul/9522/) | Alhasoob Co. | 94.36M | 33.70 | 0.66% | 329.31M |
| 342 | [9584](/quote/tadawul/9584/) | Riyal Investment and Development Company | 92.16M | 11.52 | \-10.00% | 145.28M |
| 343 | [8260](/quote/tadawul/8260/) | Gulf General Cooperative Insurance Company | 90.00M | 3.000 | \-0.33% | 361.80M |
| 344 | [9619](/quote/tadawul/9619/) | Multi Business Group Company for Projects | 88.65M | 1.970 | 0.00% | 152.42M |
| 345 | [9608](/quote/tadawul/9608/) | Al Ashghal Al Moysra Co. | 87.65M | 18.26 | 0.00% | 51.24M |
| 346 | [9587](/quote/tadawul/9587/) | Lana Medical Company | 86.40M | 1.600 | 3.90% | 107.78M |
| 347 | [9651](/quote/tadawul/9651/) | Abdul Aziz Al-Tuwaijri Trading Company | 83.24M | 16.68 | \-3.02% | 122.35M |
| 348 | [9609](/quote/tadawul/9609/) | Nass Petrol Factory Company | 81.30M | 27.10 | 0.00% | 65.96M |
| 349 | [9524](/quote/tadawul/9524/) | Advance International Company for Communication and Information Technology | 81.28M | 1.270 | 8.55% | 42.04M |
| 350 | [9645](/quote/tadawul/9645/) | National Signage Industrial Company | 80.85M | 10.78 | 0.00% | 96.68M |
| 351 | [9537](/quote/tadawul/9537/) | Amwaj International Company | 79.20M | 13.20 | 0.00% | 217.21M |
| 352 | [9589](/quote/tadawul/9589/) | Fad International Company | 76.80M | 64.00 | 4.92% | 150.79M |
| 353 | [9622](/quote/tadawul/9622/) | Shmoh Almadi Company | 76.80M | 8.17 | 0.00% | 130.74M |
| 354 | [9515](/quote/tadawul/9515/) | Fesh Fash Snack Food Production Company | 73.17M | 3.700 | \-2.37% | 37.51M |
| 355 | [9579](/quote/tadawul/9579/) | Rimath Hospitality Company | 72.11M | 36.98 | 5.96% | 30.00M |
| 356 | [9578](/quote/tadawul/9578/) | Atlas Elevators General Trading & Contracting Company | 70.63M | 8.05 | \-0.74% | 79.56M |
| 357 | [9562](/quote/tadawul/9562/) | Foods Gate Trading Co. | 70.56M | 22.40 | 0.00% | 59.51M |
| 358 | [9623](/quote/tadawul/9623/) | Al Battal Factory for Chemical Industries Company | 63.37M | 19.00 | 0.00% | 33.98M |
| 359 | [9586](/quote/tadawul/9586/) | Osool & Bakheet Investment Company | 63.18M | 8.10 | \-4.14% | \-18.73M |
| 360 | [9597](/quote/tadawul/9597/) | Leaf Global Environmental Services Company | 62.50M | 12.50 | \-5.30% | 35.26M |
| 361 | [9539](/quote/tadawul/9539/) | Aqaseem Factory for Chemicals and Plastics Co. | 58.75M | 2.350 | 0.00% | 154.52M |
| 362 | [9599](/quote/tadawul/9599/) | Taqat Mineral Trading Company | 57.86M | 4.750 | \-0.84% | 174.62M |
| 363 | [9632](/quote/tadawul/9632/) | Future Vision for Health Training Company | 56.34M | 2.850 | \-1.72% | 21.87M |
| 364 | [9571](/quote/tadawul/9571/) | Munawla Cargo Co. Ltd. | 54.00M | 18.00 | 0.00% | 51.84M |
| 365 | [9647](/quote/tadawul/9647/) | Wajd life trading Company | 53.75M | 4.300 | 0.00% | 91.67M |
| 366 | [9605](/quote/tadawul/9605/) | Neft Alsharq For Chemical Industry Company | 53.25M | 2.130 | 0.95% | 70.12M |
| 367 | [9620](/quote/tadawul/9620/) | Balsm Alofoq Medical Company | 53.05M | 21.22 | \-3.55% | 22.04M |
| 368 | [9630](/quote/tadawul/9630/) | Ratio Speciality Company for Trading | 52.00M | 2.600 | 1.17% | 56.14M |
| 369 | [9567](/quote/tadawul/9567/) | Ghida Al-Sultan Company | 49.60M | 15.50 | 6.90% | 205.28M |
| 370 | [9536](/quote/tadawul/9536/) | Arabian Food and Dairy Factories Company | 48.65M | 34.50 | 0.00% | 65.76M |
| 371 | [9595](/quote/tadawul/9595/) | WSM For Information Technology | 45.76M | 16.00 | 0.00% | 42.66M |
| 372 | [9621](/quote/tadawul/9621/) | Digital Research Company | 43.43M | 16.00 | 0.00% | 36.52M |
| 373 | [9616](/quote/tadawul/9616/) | Jana Medical Company | 43.37M | 13.50 | 0.00% | 36.71M |
| 374 | [9633](/quote/tadawul/9633/) | Service Equipment Co. | 42.77M | 17.82 | \-1.00% | 52.31M |
| 375 | [9561](/quote/tadawul/9561/) | Knowledge Net Computer Company | 42.53M | 8.10 | 0.00% | 28.70M |
| 376 | [9572](/quote/tadawul/9572/) | Al-Razi Medical Company | 39.49M | 25.98 | 1.48% | 76.40M |
| 377 | [9533](/quote/tadawul/9533/) | Saudi Parts Center Company | 39.00M | 13.00 | \-7.01% | 85.41M |
| 378 | [9617](/quote/tadawul/9617/) | Arabica Star Company | 33.28M | 24.20 | 0.00% | 52.34M |
| 379 | [9653](/quote/tadawul/9653/) | Khaled Dhafer & Brothers Logistics Services Company | 30.10M | 8.60 | 0.00% | 60.03M |
| 380 | [9565](/quote/tadawul/9565/) | Meyar Company | 26.54M | 20.00 | 0.00% | 73.82M |
| 381 | [9577](/quote/tadawul/9577/) | DAR ALMARKABAH For Renting Cars Company | 21.50M | 8.60 | \-2.05% | 49.64M |
| 382 | [9642](/quote/tadawul/9642/) | Time Entertainment Company | 19.00M | 19.00 | 0.00% | 33.48M |
| 383 | [9553](/quote/tadawul/9553/) | Molan Steel Company | 18.62M | 7.00 | 0.00% | 37.00M |

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

### assistant · 2026-11-21T10:35:09.095Z

**أداة:** `SubagentHandback`

```json
{
 "message": "Page is not paginated: it shows all 383 stocks in one table (https://stockanalysis.com/list/saudi-stock-exchange/, HTTP 200). Output below, one per line, code then tab then company name.\n2222\tSaudi Arabian Oil Company\n1120\tAl Rajhi Banking and Investment Corporation\n1180\tThe Saudi National Bank\n1211\tSaudi Arabian Mining Company (Maaden)\n7010\tSaudi Telecom Company\n2010\tSaudi Basic Industries Corporation\n2082\tACWA Power Company\n1010\tRiyad Bank\n4013\tDr. Sulaiman Al Habib Medical Services Group Company\n1060\tSaudi Awwal Bank\n1150\tAlinma Bank\n5110\tSaudi Energy Company\n2020\tSABIC Agri-Nutrients Company\n4280\tKingdom Holding Company\n1050\tBanque Saudi Fransi\n7203\tElm Company\n7020\tEtihad Etisalat Company\n2280\tAlmarai Company\n1080\tArab National Bank\n4030\tThe National Shipping Company of Saudi Arabia\n2380\tRabigh Refining and Petrochemical Company\n1140\tBank Albilad\n4325\tUmm Al Qura for Development and Construction Company\n6015\tAmericana Restaurants International PLC\n4190\tJarir Marketing Company\n7202\tArabian Internet and Communication Services Company\n4300\tDar Al Arkan Real Estate Development Company\n8210\tBupa Arabia for Cooperative Insurance Company\n8010\tThe Company for Cooperative Insurance\n4250\tJabal Omar Development Company\n2382\tADES Holding Company\n2290\tYanbu National Petrochemical Company\n1030\tThe Saudi Investment Bank\n2223\tSaudi Aramco Base Oil Company - Luberef\n4142\tRiyadh Cables Group Company\n1020\taljazira bank\n4263\tSAL Saudi Logistics Services Company\n1111\tSaudi Tadawul Group Holding Company\n4100\tMakkah Construction and Development Company\n4164\tNahdi Medical Company\n1303\tElectrical Industries Company\n2083\tPower and Water Utility Company for Jubail and Yanbu\n4002\tMouwasat Medical Services Company\n4200\tAldrees Petroleum and Transport Services Company\n8313\tRasan Information Technology Company\n1212\tAstra Industrial Group Company\n8230\tAl Rajhi Company for Cooperative Insurance\n2381\tArabian Drilling Company\n2310\tSahara International Petrochemical Company\n2250\tSaudi Industrial Investment Group\n4090\tTaiba Investment Company\n4015\tJamjoom Pharmaceuticals Factory Company\n7030\tMobile Telecommunications Company Saudi Arabia\n7200\tAl Moammar Information Systems Company\n2350\tSaudi Kayan Petrochemical Company\n2050\tSavola Group Company\n4264\tFlynas Company\n4017\tDr. Soliman Abdel Kader Fakeeh Hospital Company\n4004\tDallah Healthcare Company\n4321\tArabian Centres Company\n4310\tKnowledge Economic City Company\n4220\tEmaar The Economic City\n2330\tAdvanced Petrochemical Company\n2270\tSaudia Dairy & Foodstuff Company\n1322\tAl Masane Al Kobra Mining Company\n4020\tSaudi Real Estate Company\n4072\tMBC Group\n2230\tSaudi Chemical Holding Company\n4005\tNational Medical Care Company\n4084\tDerayah Financial Company\n4161\tBinDawood Holding Company\n4003\tUnited Electronics Company\n1810\tSeera Holding Group\n1321\tEast Pipes Integrated Company for Industry\n4018\tAlmoosa Health Company\n3040\tQassim Cement Company\n8200\tSaudi Reinsurance Company\n2060\tNational Industrialization Company\n4291\tNational Company for Learning and Education\n2080\tNational Gas and Industrialization Company\n6004\tCATRION Catering Holding Company\n1830\tLeejam Sports Company\n3020\tYAMAMA Cement Company\n4031\tSaudi Ground Services Company\n4210\tSaudi Research and Media Group\n3030\tSaudi Cement Company\n4150\tArriyadh Development Co.\n4322\tRetal Urban Development Company\n4007\tAl Hammadi Holding Company\n4001\tAbdullah Al-Othaim Markets Company\n6010\tThe National Agricultural Development Company\n2283\tThe First Milling Company\n2320\tAl-Babtain Power and Telecommunications Company\n4163\tAl-Dawaa Medical Services Company\n4165\tAl Majed for Oud Company\n4019\tSpecialized Medical Company\n2070\tSaudi Pharmaceutical Industries and Medical Appliances Corporation\n4162\tAlmunajem Foods Company\n2190\tSustained Infrastructure Holding Company\n4260\tUnited International Transportation Company\n2081\tAlkhorayef Water and Power Technologies Company\n7040\tEtihad GO Telecom Co.\n4071\tArabian Contracting Services Company\n4050\tSaudi Automotive Services Company\n4327\tAl Ramz Real Estate Company\n4009\tMiddle East Healthcare Company\n4016\tMiddle East Pharmaceutical Industries Company\n1320\tSaudi Steel Pipes Company\n3050\tSouthern Province Cement Company\n3092\tRiyadh Cement Company\n2284\tModern Mills Company\n6019\tAlmasar Alshamil Education Company JSC\n4146\tGas Arabian Services Company\n4340\tAl Rajhi REIT Fund\n2286\tFourth Milling Company\n2285\tArabian Mills for Food Products Company\n3080\tEastern Province Cement Company\n2040\tSaudi Ceramic Company\n3060\tYanbu Cement Company\n4192\tAl-Saif Stores for Development & Investment Company\n7211\tSaudi Azm for Communication and Information Technology Company\n1831\tMaharah for Human Resources Company\n9557\tEdarat Communication and Information Technology Co.\n6017\tJahez International Company for Information Systems Technology\n1834\tSaudi Manpower Solutions Company\n6022\tArmah Sports Company\n8030\tThe Mediterranean and Gulf Cooperative Insurance and Reinsurance Company\n3010\tArabian Cement Company\n2300\tSaudi Paper Manufacturing Company\n1833\tAlmawarid Manpower Company\n2170\tAlujain Corporation\n1304\tAl Yamamah Steel Industries Company\n9540\tNational Environmental Recycling Company\n4083\tUnited International Holding Company\n7204\tPerfect Presentation for Commercial Services Company\n4326\tDar Al Majed Real Estate Company\n8250\tGulf Insurance Group\n9523\tGroup Five Pipe Saudi Company\n1302\tBawan Company\n2084\tMiahona Company Limited\n3003\tCity Cement Company\n4323\tSumou Real Estate Company\n8060\tWalaa Cooperative Insurance Company\n4320\tAlandalus Property Company\n2110\tSaudi Cable Company\n2240\tAdvanced Building Industries Co.\n4240\tAFG International Company\n4012\tThob Al Aseel Company\n4040\tSaudi Public Transport Company\n2370\tMiddle East Specialized Cables Company\n2282\tNaqi Water Company\n4344\tSEDCO Capital REIT Fund\n1183\tSHL Finance Company\n4292\tAtaa Educational Company\n2150\tThe National Company for Glass Industries\n4143\tAl Taiseer Group TALCO Industrial Company\n1202\tMiddle East Company for Manufacturing and Producing Paper\n6014\tAlamar Foods Company\n4261\tTheeb Rent A Car Company\n1323\tUnited Carton Industries Company\n3004\tNorthern Region Cement Company\n4262\tLumi Rental Company\n2200\tArabian Pipes Company\n1820\tBAAN Holding Group Company\n4193\tNice One Beauty Digital Marketing Company\n9601\tMohammed Hadi Al-Rasheed Company\n6070\tAl-Jouf Agricultural Development Co.\n6018\tSport Clubs Company\n2281\tTanmiah Food Company\n4081\tNayifat Finance Company\n4110\tBatic Investments and Logistics Company\n1835\tTamkeen Human Resources Company\n4144\tRaoom trading Company\n9541\tAcademy of Learning Company\n4230\tRed Sea International Company\n9618\tAl-Fakhera Men's Tailoring Company\n8070\tArabian Shield Cooperative Insurance Company\n4328\tLadun Investment Company\n4080\tSinad Holding Company\n6001\tHalwani Bros. Co. Ltd.\n6002\tHerfy Food Services Company\n9517\tMOBI Industry Co.\n3002\tNajran Cement Company\n4014\tScientific and Medical Equipment House Company\n9521\tINMAR Company\n1182\tAmlak International Finance Company\n9559\tBalady Poultry Company\n9510\tNational Building and Marketing Co.\n4145\tAl Obeikan Glass Company\n9583\tUnited Mining Industries Company\n2140\tAyyan Investment Company\n2120\tSaudi Advanced Industries Company\n4147\tConsolidated Grunenfelder Saady Holding Company\n7205\tDar AlBalad for Business Solutions Company\n9649\tJamjoom Fashion Trading Company\n2030\tSaudi Arabian Refineries Company\n4330\tRiyad REIT Fund\n4290\tAl Khaleej Training and Education Company\n2340\tArtex Industrial Investment Company\n1324\tSaleh Abdulaziz Al Rashed & Sons Co.\n1210\tBasic Chemical Industries Company\n9544\tFuture Care Trading Co.\n4148\tAlwasail Industrial Company\n2288\tNofoth Food Products Company\n4191\tAbdullah Saad Mohammed Abo Moati for Bookstores Company\n4170\tTourism Enterprise Company (Shams)\n4180\tFitaihi Holding Group\n8012\tAljazira Takaful Taawuni Company\n4265\tCherry Trading Company\n4194\tMarketing Home Group Company for Trading Company\n1214\tAl Hassan Ghazi Ibrahim Shaker Company\n8120\tGulf Union Alahlia Cooperative Insurance Company\n4324\tBanan Real Estate Company\n9640\tASAS Makeen Real Estate Development and Investment Company\n9655\tMSGA Investment Company\n2287\tArabian Company for Agricultural and Industrial Investment\n3007\tZahrat Al Waha For Trading Company\n8240\tChubb Arabia Cooperative Insurance Company\n8300\tWataniya Insurance Company\n4082\tMorabaha Marina Financing Company\n8280\tLiva Insurance Company\n9527\tAlf Meem Yaa for Medical Supplies and Equipment Company\n8040\tMutakamela Insurance Company\n4333\tTaleem REIT Fund\n4008\tSaudi Company for Hardware SACO\n9637\tAxelerated Solutions for Information and Communication Technology Company\n3005\tUmm Al-Qura Cement Company\n3090\tTabuk Cement Company\n9610\tFirst Avenue Real Estate Development Company\n1325\tWatani Iron Steel Company\n9546\tNaba Al Saha Medical Services Company\n4051\tBaazeem Trading Company\n9634\tAdeer Real Estate Company\n9628\tLamasat Company\n1301\tUnited Wire Factories Company\n4011\tL'azurde Company for Jewelry\n9596\tQuara Finance Company\n2130\tSaudi Industrial Development Co.\n9552\tSaudi Top for Trading Company\n9543\tSaudi Networkers Services Company\n3091\tAl Jouf Cement Company\n2210\tNama Chemicals Company\n8020\tMalath Cooperative Insurance Company\n4006\tSaudi Marketing Company\n9514\tMohammed Hasan AlNaqool Sons Co.\n9560\tWaja Company\n9568\tMayar Holding Company\n9575\tMarble Design Factory Company\n4336\tMulkia Gulf Real Estate REIT\n2160\tThe Saudi Arabian Amiantit Company\n2180\tFilling and Packing Materials Manufacturing Company\n9611\tArabian United Float Glass Company\n2100\tWafrah for Industry and Development Company\n4130\tDarb Saudi Investment Company\n9607\tASG Plastic Factory Company\n1832\tSadr Logistics Company\n9639\tAnmat Technology for Trading Co.\n4140\tSaudi Industrial Export Company\n7201\tArab Sea Information Systems Company\n9580\tAl Rashid Industrial Co.,\n6050\tSaudi Fisheries Company\n4061\tAnaam International Holding Group Company\n9627\tTwareat Medical Care Company\n4070\tTihama for Advertising, Public Relations and Marketing Company\n9530\tArabian International Healthcare Holding Company\n9614\tPurity for Information Technology Company\n6060\tAsh-Sharqiyah Development Co.\n4021\tCanadian General Medical Center Complex Company\n9613\tShalfa Facilities Management Company\n2090\tNational Gypsum Company\n8160\tArabia Insurance Cooperative Company\n2220\tNational Metal Manufacturing and Casting Co.\n9625\tItmam Consultancy Company\n6016\tShatirah House Restaurant Co.\n9548\tArabian Plastic Industrial Company Limited\n6090\tJazan Development and Investment Company\n6020\tAl Gassim Investment Holding Company\n2001\tMethanol Chemicals Company\n9594\tAl-Modawat Specialized Medical Company\n9564\tHorizon Food Company Limited\n1213\tNaseej International Trading Company\n9550\tSure Global Tech Co.\n9574\tProfessional Medical Expertise Company\n8100\tSaudi Arabian Cooperative Insurance Company\n4270\tSaudi Printing and Packaging Co.\n4335\tMusharaka REIT Fund\n9600\tQomel Company Limited\n9641\tHawyia Auctions Company\n9566\tSaudi Lime Industries Company\n9631\tHedab Alkhaleej Trading Co.\n1201\tTakween Advanced Industries\n8180\tAl Sagr Cooperative Insurance Company\n6040\tTabuk Agricultural Development Company\n8170\tAl-Etihad Cooperative Insurance Company\n9585\tMulkia Investment Company\n4141\tAl-Omran Industrial Trading Company\n9576\tPaper Home Company\n3008\tAl Kathiri Holding Company\n9602\tYaqeen Capital Company\n9650\tSahat Almajd Trading Company\n9569\tAlMuneef Company for Trade, Industry, Agriculture and Contracting\n9598\tAl Mohafaza Company for Education\n8310\tAmana Cooperative Insurance Company\n6013\tDevelopment Works Food Company\n9545\tInternational Human Resources Company\n9603\tHorizon Educational Company\n9563\tBENA Steel Industries\n9592\tAlmujtama Alraida Medical Co.\n8311\tSaudi Enaya Cooperative Insurance Company\n9648\tHamad Mohammed Bin Saedan Real Estate Company\n2360\tSaudi Vitrified Clay Pipe Company\n9604\tMiral Dental Company\n8050\tSalama Cooperative Insurance Company\n4160\tThimar Development Holding Company\n9570\tTam Development Company\n9516\tNatural Gas Distribution Company\n8150\tAllied Cooperative Insurance Group\n9593\tPan Gulf Marketing Company\n9532\tAljouf Mineral Water Bottling Co.\n9636\tAl Kuzama Trading Co\n9591\tView United Real Estate Development Co.\n9558\tAlqemam for Computer Systems Co.\n9615\tMufeed Company\n9551\tKnowledge Tower Trading Company\n9547\tRawasi Albina Investment Co.\n8190\tUnited Cooperative Assurance Company\n9624\tAlshehili Company for metal industries\n9612\tSAMA Healthy Water Factory company\n9626\tBasma Adeem Medical company\n9542\tKeir International Co.\n9538\tNaseej for Technology Co.\n9581\tClean Life Company\n4331\tAljazira Mawten REIT Fund\n9588\tRiyadh Steel Company\n9606\tAltharwah Albashariyyah Co.\n9549\tAbdulaziz and Mansour Ibrahim Albabtin Co.\n9644\tNaf Company for Feed for Industry\n9555\tLeen Alkhair Trading Company\n6012\tRaydan Food Company\n9635\tDkhoun National Trading Company\n9522\tAlhasoob Co.\n9584\tRiyal Investment and Development Company\n8260\tGulf General Cooperative Insurance Company\n9619\tMulti Business Group Company for Projects\n9608\tAl Ashghal Al Moysra Co.\n9587\tLana Medical Company\n9651\tAbdul Aziz Al-Tuwaijri Trading Company\n9609\tNass Petrol Factory Company\n9524\tAdvance International Company for Communication and Information Technology\n9645\tNational Signage Industrial Company\n9537\tAmwaj International Company\n9589\tFad International Company\n9622\tShmoh Almadi Company\n9515\tFesh Fash Snack Food Production Company\n9579\tRimath Hospitality Company\n9578\tAtlas Elevators General Trading & Contracting Company\n9562\tFoods Gate Trading Co.\n9623\tAl Battal Factory for Chemical Industries Company\n9586\tOsool & Bakheet Investment Company\n9597\tLeaf Global Environmental Services Company\n9539\tAqaseem Factory for Chemicals and Plastics Co.\n9599\tTaqat Mineral Trading Company\n9632\tFuture Vision for Health Training Company\n9571\tMunawla Cargo Co. Ltd.\n9647\tWajd life trading Company\n9605\tNeft Alsharq For Chemical Industry Company\n9620\tBalsm Alofoq Medical Company\n9630\tRatio Speciality Company for Trading\n9567\tGhida Al-Sultan Company\n9536\tArabian Food and Dairy Factories Company\n9595\tWSM For Information Technology\n9621\tDigital Research Company\n9616\tJana Medical Company\n9633\tService Equipment Co.\n9561\tKnowledge Net Computer Company\n9572\tAl-Razi Medical Company\n9533\tSaudi Parts Center Company\n9617\tArabica Star Company\n9653\tKhaled Dhafer & Brothers Logistics Services Company\n9565\tMeyar Company\n9577\tDAR ALMARKABAH For Renting Cars Company\n9642\tTime Entertainment Company\n9553\tMolan Steel Company"
}
```

### user · 2026-11-21T10:35:10.010Z

**نتيجة أداة:**
```
{"success":true,"message":"Report delivered to your caller."}
```
