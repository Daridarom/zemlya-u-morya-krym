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
    args = p.parse_args()
    domain = args.domain.strip().lower()
    if domain.startswith(("http://", "https://")):
        parts = urlsplit(domain)
        if parts.path not in ("", "/") or parts.query or parts.fragment:
            p.error("Домен нужно указывать без пути и параметров")
        domain = parts.netloc
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+", domain):
        p.error("Некорректное имя домена")
    if not args.form_verified or not args.policy_reviewed:
        p.error("Остановлено: до рекламы обязательны --form-verified и --policy-reviewed")
    out = Path(args.output).resolve()
    if out == ROOT or ROOT in out.parents and out == ROOT / "assets":
        p.error("Нельзя затирать исходники")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", out / "assets")
    shutil.copy2(ROOT / "politika.html", out / "politika.html")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    # GitHub Pages остаётся закрытым от поисковиков: запрет снимается только в отдельной сборке.
    index, n = re.subn(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="index, follow">', index, count=1)
    if n != 1:
        p.error("Не найден тег robots: проверьте файл вручную")
    index = index.replace("https://daridarom.github.io/zemlya-u-morya-krym/", f"https://{domain}/")
    if "github.io" in index:
        p.error("В странице остались ссылки на github.io")
    index = index.replace("</head>", f'<link rel="canonical" href="https://{domain}/">\n</head>', 1)
    if "https://forms.yandex.ru/u/6adc777e852af3c4d5fc9a8f/" not in index:
        p.error("Не найдена согласованная Яндекс Форма")
    for path in re.findall(r'(?:src|href)="(assets/[^"]+)"', index):
        if not (ROOT / path).exists():
            p.error(f"Нет файла {path}")
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://" + domain + "/sitemap.xml\n", encoding="utf-8"
    )
    (out / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>https://{domain}/</loc></url></urlset>\n', encoding="utf-8"
    )
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Сборка подготовлена: {out}. Перед переключением рекламы проверьте HTTPS, форму и цели.")

if __name__ == "__main__":
    main()
