"""Select a versioned analytics release for inherited QA gates."""
import adult_analytics_release as r3
import diagnostic_intent_release as diagnostic
import guide_donor_release as guide_donors


def current_release():
    """Callers must still admit the selected release using active() and verify()."""
    if diagnostic.active():
        return diagnostic
    return guide_donors if guide_donors.active() else r3
