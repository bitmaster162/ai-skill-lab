"""Select a versioned analytics release for inherited QA gates."""
import adult_analytics_release as r3
import certificate_donor_release as certificate_donors
import diagnostic_intent_release as diagnostic
import guide_donor_release as guide_donors
import sitemap_route_dates_release as sitemap_dates
import telegram_card_release as telegram_card


def has_certificate_links():
    return certificate_donors.active() or telegram_card.active()


def has_route_dates():
    return sitemap_dates.active() or has_certificate_links()


def has_diagnostic_forms():
    return diagnostic.active() or has_route_dates()


def has_guide_links():
    return guide_donors.active() or has_diagnostic_forms()


def current_release():
    """Callers must still admit the selected release using active() and verify()."""
    if telegram_card.active():
        return telegram_card
    if certificate_donors.active():
        return certificate_donors
    if sitemap_dates.active():
        return sitemap_dates
    if diagnostic.active():
        return diagnostic
    return guide_donors if guide_donors.active() else r3
