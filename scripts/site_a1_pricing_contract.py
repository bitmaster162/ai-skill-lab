#!/usr/bin/env python3
"""SITE-A1 pricing data contract, read-only source of pricing snapshot and JSON-LD."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUBLIC="https://aiskillab.work"
def facts():
    return json.loads((ROOT/"data/commercial_facts.json").read_text("utf-8"))
def money(price):
    assert isinstance(price,str) and price.startswith("$")
    return price.replace("$","").replace(",","")
def display_name(name,lang):
    ru={"workflow_audit":"Аудит рабочего процесса",
        "implementation_pilot":"Внедрение пилота",
        "operating_support":"Операционная поддержка",
        "operating_partner":"Операционный партнёр",
        "office_hours":"Часы консультаций"}
    return ru.get(name) if lang=="ru" else None
def catalog(lang):
    f=facts();en=lang=="en";p="/en/pricing" if en else "/pricing"
    rows=[]
    def add(name,price,desc=None):
        obj={"@type":"Offer","name":name,"price":money(price) if price.startswith("$") else price,
             "priceCurrency":"USD","url":PUBLIC+p}
        if desc:obj["description"]=desc
        rows.append(obj)
    add("Free introductory call" if en else "Бесплатный звонок-знакомство","0",
        "15 minutes" if en else "15 минут")
    add(f["diagnostic"]["name_en" if en else "name_ru"],f["diagnostic"]["price"])
    for group in ("adult","kids","teens"):
        for plan in f["tracks"][group]:add(plan["name"],plan["price"])
    add(f["family"]["name"],f["family"]["price"])
    business=f["business"]
    add(business["workflow_audit"]["name_en"] if en else display_name("workflow_audit",lang),
        business["workflow_audit"]["price"])
    add(business["team_training"]["name_en"] if en else business["team_training"]["name_ru"],
        business["team_training"]["total_from"],
        f"From {business['team_training']['price_from_per_session']} per session; minimum {business['team_training']['min_sessions']} sessions; up to {business['team_training']['max_people']} participants" if en else
        f"От {business['team_training']['price_from_per_session']} за занятие; минимум {business['team_training']['min_sessions']} занятия; до {business['team_training']['max_people']} человек")
    add(business["implementation_pilot"]["name_en"] if en else display_name("implementation_pilot",lang),
        business["implementation_pilot"]["price_from"],
        f"Starting at; scope cap {business['implementation_pilot']['scope_cap_hours']} hours" if en else
        f"От указанной суммы; предел объёма работ {business['implementation_pilot']['scope_cap_hours']} часов")
    recurring=f["recurring"]
    for key in ("operating_support","operating_partner","office_hours"):
        row=recurring[key]
        name=row["name_en"] if en else display_name(key,lang)
        add(name,row["price_monthly"],"per month" if en else "в месяц")
    return {"@context":"https://schema.org","@type":"OfferCatalog",
            "@id":PUBLIC+p+"#offers",
            "name":"AI Skill Lab pricing" if en else "Цены AI Skill Lab",
            "itemListElement":rows}
def snapshot():
    f=facts();a=[]
    a.append("## Pricing snapshot (USD)")
    a.append("RU: https://aiskillab.work/pricing | EN: https://aiskillab.work/en/pricing")
    a.append("- Introductory call: free, 15 minutes")
    a.append("- Diagnostic: "+f["diagnostic"]["price"]+", 60 minutes, 14-day package credit")
    for label,group in (("Adults","adult"),("Kids 8-13","kids"),("Teens 14-18","teens")):
        a.append("- "+label+": "+", ".join(plan["name"]+" "+plan["price"] for plan in f["tracks"][group]))
    a.append("- Family Concierge: "+f["family"]["price"])
    b=f["business"]
    a.append("- Workflow audit: "+b["workflow_audit"]["price"])
    a.append("- Team training: from "+b["team_training"]["price_from_per_session"]+"/session; "+str(b["team_training"]["min_sessions"])+"-session minimum from "+b["team_training"]["total_from"]+"; up to "+str(b["team_training"]["max_people"])+" people")
    a.append("- Implementation pilot: from "+b["implementation_pilot"]["price_from"]+"; scope cap "+str(b["implementation_pilot"]["scope_cap_hours"])+" hours")
    c=f["recurring"]
    a.append("- Operating support: "+c["operating_support"]["price_monthly"]+"/month, "+str(c["operating_support"]["hours"])+" hours")
    a.append("- Operating partner: "+c["operating_partner"]["price_monthly"]+"/month, "+str(c["operating_partner"]["hours"])+" hours")
    a.append("- Office hours: "+c["office_hours"]["price_monthly"]+"/month, "+str(c["office_hours"]["sessions"])+" sessions")
    a.append("- Pair: "+str(f["pair"]["multiplier"])+"x the individual package; each participant "+str(f["pair"]["participant_discount_percent"])+"% less")
    return "\n".join(a)+"\n"
if __name__=="__main__":
    print(snapshot(),end="")
