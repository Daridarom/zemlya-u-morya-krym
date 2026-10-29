#!/usr/bin/env python3
"""Собирает отдельный выпуск для российского хостинга, не меняя GitHub Pages."""
from __future__ import annotations
import argparse
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    p = argparse.ArgumentParser(description="Build standalone landing release")
    p.add_argument("--domain", required=True, help="Уже принадлежащий компании домен, например example.ru")
    p.add_argument("--form-verified", action="store_true", help="Проверена реальная доставка тестовой заявки")
    p.add_argument("--policy-reviewed", action="store_true", help="Юридически согласована политика и оператор")
    p.add_argument("--output", default="dist", help="Папка итоговой сборки")
    p.add_argument("--preview", action="store_true", help="Предпросмотр на домене: страница остаётся закрытой от поисковиков")
    p.add_argument("--metrika", help="Номер счётчика Яндекс Метрики для этого домена")
    p.add_argument("--alias", action="append", default=[], help="Дополнительный домен, который перенаправляется на основной (можно кириллицей)")
    args = p.parse_args()
    domain = args.domain.strip().lower()
    if domain.startswith(("http://", "https://")):
        parts = urlsplit(domain)
        if parts.path not in ("", "/") or parts.query or parts.fragment:
            p.error("Домен нужно указывать без пути и параметров")
        domain = parts.netloc
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+", domain):
        p.error("Некорректное имя домена")
    if not args.preview and (not args.form_verified or not args.policy_reviewed):
        p.error("Остановлено: до рекламы обязательны --form-verified и --policy-reviewed")
    out = Path(args.output).resolve()
    if out == ROOT or ROOT in out.parents and out == ROOT / "assets":
        p.error("Нельзя затирать исходники")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    metrika = ""
    if args.metrika:
        if not args.metrika.isdigit():
            p.error("Номер счётчика Метрики — только цифры")
        n_ = args.metrika
        # Счётчик не запускается сам: window.loadYM вызывается после согласия на cookies
        metrika = (
            f'<script>window.YM_ID={n_};window.loadYM=function(){{if(window.ymLoaded)return;window.ymLoaded=true;\n'
            '(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();'
            'for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}'
            'k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})'
            '(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");\n'
            f'ym({n_},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});}};</script>'
        )
    for page in ("politika.html", "spasibo.html", "soglasie.html"):
        html = (ROOT / page).read_text(encoding="utf-8").replace("<!--METRIKA-->", metrika)
        (out / page).write_text(html, encoding="utf-8")
    shutil.copytree(ROOT / "assets" / "fonts", out / "assets" / "fonts")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    # GitHub Pages остаётся закрытым от поисковиков: запрет снимается только в отдельной сборке.
    robots = "noindex, nofollow" if args.preview else "index, follow"
    index, n = re.subn(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', index, count=1)
    if n != 1:
        p.error("Не найден тег robots: проверьте файл вручную")
    index = index.replace("https://daridarom.github.io/zemlya-u-morya-krym/", f"https://{domain}/")
    if "github.io" in index:
        p.error("В странице остались ссылки на github.io")
    index = index.replace("</head>", f'<link rel="canonical" href="https://{domain}/">\n</head>', 1)
    if "https://forms.yandex.ru/u/6adc777e852af3c4d5fc9a8f/" not in index:
        p.error("Не найдена согласованная Яндекс Форма")
    # В выпуск попадают только файлы, на которые ссылается страница.
    for path in sorted(set(re.findall(r'(?:src|href)="(assets/[^"]+)"', index))):
        if not (ROOT / path).exists():
            p.error(f"Нет файла {path}")
        (out / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, out / path)
    if args.metrika and "<!--METRIKA-->" not in index:
        p.error("В странице нет места для счётчика Метрики")
    index = index.replace("<!--METRIKA-->", metrika)
    (out / "index.html").write_text(index, encoding="utf-8")
    if args.preview:
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    else:
        (out / "robots.txt").write_text(
            "User-agent: *\nAllow: /\nSitemap: https://" + domain + "/sitemap.xml\n", encoding="utf-8"
        )
        (out / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>https://{domain}/</loc></url></urlset>\n', encoding="utf-8"
        )
    # Все прочие адреса (www, зеркала) ведут на основной домен.
    hosts = [domain] + [a.strip().lower().encode("idna").decode() for a in args.alias]
    (out / ".htaccess").write_text(
        "AddDefaultCharset UTF-8\n"
        "RewriteEngine On\n"
        f"RewriteCond %{{HTTP_HOST}} !^{re.escape(domain)}$ [NC]\n"
        f"RewriteRule ^(.*)$ %{{REQUEST_SCHEME}}://{domain}/$1 [R=301,L]\n"
        "<IfModule mod_expires.c>\nExpiresActive On\nExpiresByType image/webp \"access plus 30 days\"\n</IfModule>\n"
        f"# Зеркала: {', '.join(hosts[1:]) or 'нет'}\n",
        encoding="utf-8",
    )
    print(f"Сборка подготовлена: {out}. Перед переключением рекламы проверьте HTTPS, форму и цели.")

if __name__ == "__main__":
    main()
