"""Select a versioned analytics release for inherited QA gates."""
import adult_analytics_release as r3
import certificate_donor_release as certificate_donors
import diagnostic_intent_release as diagnostic
import guide_donor_release as guide_donors
import sitemap_route_dates_release as sitemap_dates
import telegram_card_release as telegram_card
import universe_en_home_release as universe_home
import restored_guides_release as restored_guides
import ru_guide_cards_release as ru_guide_cards


def has_restored_guides():
    return restored_guides.active() or ru_guide_cards.active()


def has_universe_home():
    return universe_home.active() or has_restored_guides()


def has_telegram_card():
    return telegram_card.active() or has_universe_home()


def has_certificate_links():
    return certificate_donors.active() or has_telegram_card()


def has_route_dates():
    return sitemap_dates.active() or has_certificate_links()


def has_diagnostic_forms():
    return diagnostic.active() or has_route_dates()


def has_guide_links():
    return guide_donors.active() or has_diagnostic_forms()


def current_release():
    """Callers must still admit the selected release using active() and verify()."""
    if ru_guide_cards.active():
        return ru_guide_cards
    if restored_guides.active():
        return restored_guides
    if universe_home.active():
        return universe_home
    if telegram_card.active():
        return telegram_card
    if certificate_donors.active():
        return certificate_donors
    if sitemap_dates.active():
        return sitemap_dates
    if diagnostic.active():
        return diagnostic
    return guide_donors if guide_donors.active() else r3
