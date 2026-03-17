from __future__ import annotations

from __future__ import annotations
from functools import lru_cache
from pathlib import Path

import jinja2
from babel.core import negotiate_locale
from babel.dates import format_date, format_datetime
from babel.numbers import format_currency, format_decimal
from babel.support import NullTranslations, Translations
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware


locale_domain = "messages"
default_locale = "en"
supported_locales = ["en", "fr", "haw"]


LocaleID = Enum(  # type: ignore[misc]
    "LocaleID",
    {locale : locale for locale in supported_locales},
    type=str
)


class LocaleMiddleware(BaseHTTPMiddleware):
    base_dir = Path(__file__).resolve().parent
    template_dir = base_dir / "templates"
    translation_dir = base_dir / "translations"

    def __init__(
        self,
        app,
        supported_locales: list[LocaleID] = supported_locales,
        default_locale: LocaleID = default_locale,
        domain: str = locale_domain,
        template_dir: Optional[str | Path] = None,
        translation_dir: Optional[str | Path] = None
    ):
        super().__init__(app)
        if template_dir is not None:
            self.template_dir = template_dir
        if translation_dir is not None:
            self.translation_dir = translation_dir

    @staticmethod
    def normalize_locale(value: str | None) -> str | None:
        if not value:
            return None
        value = value.strip().replace("_", "-").lower()
        if not value:
            return None
        return value.split("-")[0]


    @classmethod
    def parse_accept_language(cls, header: str | None) -> list[str]:
        if not header:
            return []

        result: list[str] = []
        for part in header.split(","):
            lang = part.split(";")[0].strip()
            lang = cls.normalize_locale(lang)
            if lang:
                result.append(lang)
        return result


    def choose_locale(self, request: Request) -> str:
        lang = self.normalize_locale(request.query_params.get("lang"))
        if lang in self.supported_locales:
            return lang

        lang = self.normalize_locale(request.cookies.get("lang"))
        if lang in self.supported_locales:
            return lang

        accepted = self.parse_accept_language(request.headers.get("accept-language"))
        negotiated = negotiate_locale(accepted, self.supported_locales)
        if negotiated:
            return self.normalize_locale(negotiated) or self.default_locale

        return self.default_locale


    async def dispatch(self, request: Request, call_next):
        request.state.locale = self.choose_locale(request)
        return await call_next(request)


    @lru_cache(maxsize=32)
    def get_translations(self, locale: str) -> Translations:
        try:
            return Translations.load(
                dirname=str(self.translation_dir),
                locales=[locale],
                domain=self.domain,
            )
        except Exception:
            return NullTranslations()

     def template_context(self, request: Request) -> dict:
        locale = getattr(request.state, "locale", self.default_locale)
        t = self.get_translations(locale)

        context = {
            "locale": locale,
            "_": t.gettext,
            "gettext": t.gettext,
            "ngettext": t.ngettext,
        }

        pgettext = getattr(t, "pgettext", None)
        npgettext = getattr(t, "npgettext", None)

        if pgettext is not None:
            context["pgettext"] = pgettext
        if npgettext is not None:
            context["npgettext"] = npgettext

        return context

    def create_templates(self) -> Jinja2Templates:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            extensions=["jinja2.ext.i18n"],
        )

        env.policies["ext.i18n.trimmed"] = True
        env.install_null_translations(newstyle=True)

        return Jinja2Templates(
            env=env,
            context_processors=[self.template_context],
        )

