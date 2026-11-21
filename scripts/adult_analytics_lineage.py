"""Select a versioned analytics release for inherited QA gates."""
import adult_analytics_release as r3
import diagnostic_intent_release as diagnostic
import guide_donor_release as guide_donors
import sitemap_route_dates_release as sitemap_dates


def has_diagnostic_forms():
    return diagnostic.active() or sitemap_dates.active()


def has_guide_links():
    return guide_donors.active() or has_diagnostic_forms()


def current_release():
    """Callers must still admit the selected release using active() and verify()."""
    if sitemap_dates.active():
        return sitemap_dates
    if diagnostic.active():
        return diagnostic
    return guide_donors if guide_donors.active() else r3
