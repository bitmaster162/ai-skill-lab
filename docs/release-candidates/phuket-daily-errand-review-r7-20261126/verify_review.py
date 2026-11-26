"""Replay exact R6 browser suite and add R7 errand status review assertions."""
import hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
source=P.parent/"L12_DAILY_VARIANCE_R6_20261126/verify_variance.py"
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=="4c7c31e9c8e227126db827b266d48bb486105b39445100071d2237a94e2917e2"
s=raw.decode()
def replace(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b,1)
replace('8813b0158b2e69d33383295b67fb87b92026ee79cb061be66b6f3329d0678fcc','aafd6aa35bb479d4c58ebfe87992dd9dc8471d645d0925fe6cc9414135876f9f')
replace('"VARIANCE_DRAFT.json"','"REVIEW_DRAFT.json"')
replace('OWNER_CATEGORY_VARIANCE_R6_BROWSER_QA','OWNER_ERRAND_REVIEW_R7_BROWSER_QA')
replace('print("R6 QA"','print("R7 QA"')
replace('Isolated static Chromium; not full inherited suite, Next router/build, independent accessibility or release acceptance.','Pinned R6 browser assertions replayed plus R7 grouping. Not full R5 suite, Next router/build, independent accessibility or release acceptance.')
replace('        checks["no_storage"]=', '''        review=g("errand-review")
        group=lambda k:review.locator('[data-review-state="'+k+'"]')
        count=lambda k:g("review-count-"+k).inner_text()
        names=lambda k:g("review-list-"+k).inner_text()
        none=review.get_attribute("data-none")
        checks["review_initial"]=review.is_visible() and count("0")=="6" and all(count(k)=="0" and names(k)==none for k in ("1","2","3"))
        checks["review_all_initial_labels"]=all(label(k) in names("0") for k in keys)
        for k,st in zip(keys,("1","2","3","0","1","2")):g(k+"-state").select_option(st)
        checks["review_group_counts"]=[count(st) for st in ("1","2","3","0")]==["2","2","1","1"]
        checks["review_exact_membership"]=all(names(st)=="; ".join(label(k) for k,s in zip(keys,("1","2","3","0","1","2")) if s==st) for st in ("1","2","3","0"))
        checks["review_summary"]=all(group(st).locator("[data-review-label]").inner_text()+" ("+count(st)+"): "+names(st) in note() for st in ("1","2","3","0"))
        checks["done_not_paid"]=g(keys[2]+"-actual").input_value()=="" and g("actual-known").inner_text()=="—"
        fill(keys[2]+"-actual","1.01")
        checks["payment_independent"]=count("3")=="1" and names("3")==label(keys[2]) and g("actual-known").inner_text()==money(101)
        g(keys[2]+"-state").select_option("2")
        checks["move_without_duplication"]=count("3")=="0" and names("3")==none and count("2")=="3" and g(keys[2]+"-actual").input_value()=="1.01"
        checks["sum_counts"]=sum(int(count(st)) for st in ("1","2","3","0"))==6
        checks["review_geometry"]=pg.evaluate("document.documentElement.scrollWidth <= innerWidth")
        g("reset").click()
        checks["review_reset"]=count("0")=="6" and all(count(st)=="0" and names(st)==none for st in ("1","2","3")) and g("reset").is_disabled()
        checks["no_storage"]=''')
replace('        checks["nojs_hidden"]=', '''        checks["review_nojs_hidden"]=not g("errand-review").is_visible()
        g(keys[0]+"-state").select_option("2")
        checks["review_nojs_native"]=g(keys[0]+"-state").input_value()=="2" and not g("errand-review").is_visible()
        checks["nojs_hidden"]=''')
compile(s,"adapted_r6.py","exec")
exec(compile(s,"adapted_r6.py","exec"),{"__name__":"__main__","__file__":str(P/"adapted_r6.py")})
