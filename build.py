#!/usr/bin/env python3
"""Static SEO site generator for WhiskyPick KR (국내 위스키 특가·신상 데일리 보드).
Reads data/deals.json and data/gear.json and generates index.html, sitemap.xml, and feed.xml.
"""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://kelpshake04.github.io/whisky-deals-kr"


def esc(val: str) -> str:
    return html.escape(str(val or ""), quote=True)


def render_deal_card(deal: dict) -> str:
    badge = deal.get("badge", "")
    urgent_cls = " urgent" if any(k in badge for k in ("마감", "한정")) else ""
    highlights_html = "\n".join(
        f"          <li>{esc(item)}</li>" for item in deal.get("highlights", [])
    )
    return f"""      <article class="card deal-card" data-category="{esc(deal.get('category', 'etc'))}">
        <div class="card-top">
          <span class="channel">{esc(deal.get('channel', ''))}</span>
          <span class="badge{urgent_cls}">{esc(badge)}</span>
        </div>
        <h2>{esc(deal.get('title', ''))}</h2>
        <div class="meta">
          <span>📅 기간: {esc(deal.get('period', ''))}</span>
          <span>📍 채널: {esc(deal.get('location', ''))}</span>
        </div>
        <ul class="highlights">
{highlights_html}
        </ul>
        <p class="tip">💡 {esc(deal.get('tip', ''))}</p>
      </article>"""


def render_gear_card(item: dict) -> str:
    return f"""      <a class="gear-card" href="{esc(item.get('url', '#'))}" target="_blank" rel="noopener noreferrer nofollow">
        <span class="gear-tag">{esc(item.get('tag', ''))}</span>
        <div class="gear-name">{esc(item.get('name', ''))}</div>
        <p class="gear-reason">{esc(item.get('reason', ''))}</p>
        <div class="gear-footer">
          <span>{esc(item.get('priceRange', ''))}</span>
          <span>최저가 보기 →</span>
        </div>
      </a>"""


def build() -> None:
    deals_data = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8"))
    gear_data = json.loads((ROOT / "data" / "gear.json").read_text(encoding="utf-8"))

    updated_at = deals_data.get("updatedAt", datetime.now(timezone.utc).date().isoformat())
    headline = deals_data.get("headline", "오늘의 국내 위스키 특가 총정리")
    summary = deals_data.get("summary", "데일리샷, 코스트코, 트레이더스, 보틀벙커, 편의점 위스키 할인 정보를 매일 정리합니다.")
    deals = deals_data.get("deals", [])
    gear_items = gear_data.get("items", [])
    monetization = gear_data.get("monetization", {})

    adsense_id = (monetization.get("adsenseClientId") or "").strip()
    adsense_tag = (
        f'  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(adsense_id)}" crossorigin="anonymous"></script>\n'
        if adsense_id
        else ""
    )
    disclosure_html = (
        '      <p class="disclosure">※ 이 페이지의 일부 홈바 용품 링크는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.</p>'
        if monetization.get("coupangDisclosure")
        else ""
    )

    deals_html = "\n".join(render_deal_card(d) for d in deals)
    gear_html = "\n".join(render_gear_card(g) for g in gear_items)

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "위스키픽 KR — 오늘의 국내 위스키 특가·신상 보드",
            "url": SITE_URL,
            "description": summary,
            "inLanguage": "ko-KR",
            "dateModified": updated_at,
        },
        ensure_ascii=False,
    )

    index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>위스키픽 KR — 오늘의 위스키 특가·할인·신제품 총정리 ({esc(updated_at)})</title>
  <meta name="description" content="{esc(summary)}">
  <meta name="keywords" content="위스키 특가, 위스키 할인, 데일리샷, 코스트코 위스키, 트레이더스 위스키, 보틀벙커, GS25 위스키, 이마트24 보틀오더, 위스키 신제품">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(headline)} | 위스키픽 KR">
  <meta property="og:description" content="{esc(summary)}">
  <meta property="og:url" content="{SITE_URL}/">
  <link rel="canonical" href="{SITE_URL}/">
  <link rel="alternate" type="application/rss+xml" title="위스키픽 KR RSS" href="{SITE_URL}/feed.xml">
  <link rel="stylesheet" href="style.css">
{adsense_tag}  <script type="application/ld+json">{json_ld}</script>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a class="brand" href="./">
        <div class="brand-mark">🥃</div>
        <div>
          <div class="brand-title">위스키픽 KR</div>
          <div class="brand-sub">매일 오전 9시 업데이트 · 국내 위스키 특가 보드</div>
        </div>
      </a>
      <div class="updated-pill">업데이트: {esc(updated_at)}</div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <h1>{esc(headline)}</h1>
      <p>{esc(summary)}</p>
    </section>

    <section class="controls" aria-label="필터 및 검색">
      <div class="tabs" role="tablist">
        <button class="tab-btn active" data-category="all">전체 ({len(deals)})</button>
        <button class="tab-btn" data-category="mart">대형마트·창고형</button>
        <button class="tab-btn" data-category="app">픽업앱</button>
        <button class="tab-btn" data-category="cvs">편의점</button>
        <button class="tab-btn" data-category="release">신제품·한정판</button>
      </div>
      <div class="search-box">
        <input id="search-input" type="search" placeholder="위스키명, 매장, 카드 검색..." aria-label="특가 검색">
      </div>
    </section>

    <section class="deals-grid" aria-label="진행 중인 위스키 특가 목록">
{deals_html}
    </section>

    <div id="empty-state" class="empty-state">조건에 맞는 특가 정보가 없습니다. 다른 키워드로 검색해 보세요.</div>

    <section aria-label="위스키 홈바 필수템">
      <div class="section-header">
        <h2>🧊 위스키 홈바 필수템 추천</h2>
        <p>특가로 구한 위스키를 2배 더 맛있게 즐기는 가성비 도구</p>
      </div>
      <div class="gear-grid">
{gear_html}
      </div>
    </section>
  </main>

  <footer>
    <div class="container footer-inner">
      <p><strong>위스키픽 KR</strong> — 국내 주요 마트·픽업앱·편의점의 공개된 위스키 할인 행사 및 신제품 소식을 매일 정리합니다.</p>
      <p>매장별 재고 및 행사 가격은 지점·시점에 따라 변동되거나 조기 품절될 수 있으므로 방문·결제 전 해당 앱/매장에서 최종 가격을 확인하세요. 지나친 음주는 건강에 해롭습니다.</p>
{disclosure_html}
    </div>
  </footer>

  <script src="app.js"></script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{updated_at}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    rss_items = "\n".join(
        f"""    <item>
      <title>{esc('[' + d.get('channel', '') + '] ' + d.get('title', ''))}</title>
      <link>{SITE_URL}/#{esc(d.get('id', ''))}</link>
      <guid isPermaLink="false">{esc(d.get('id', ''))}-{updated_at}</guid>
      <description>{esc(' / '.join(d.get('highlights', [])))}</description>
    </item>"""
        for d in deals
    )
    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>위스키픽 KR — 오늘의 국내 위스키 특가</title>
    <link>{SITE_URL}/</link>
    <description>{esc(summary)}</description>
    <language>ko</language>
    <lastBuildDate>{updated_at}</lastBuildDate>
{rss_items}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed_xml, encoding="utf-8")
    print(f"Built index.html, sitemap.xml, feed.xml ({len(deals)} deals, updated {updated_at})")


if __name__ == "__main__":
    build()
