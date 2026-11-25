#!/usr/bin/env python3
"""Haal publiek beschikbare supermarktacties op voor Patjes Koopjeskrant.
Gebruikt alleen de vier ondersteunde winkels. Bij fouten geen schijnbaar lege week publiceren.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone, date
from pathlib import Path

BASE = 'https://www.prijsprofeet.nl/api/v1/products/promotional/all'
RETAILERS = {'albert_heijn':'Albert Heijn','hoogvliet':'Hoogvliet','jumbo':'Jumbo','aldi':'Aldi'}
DEST = Path(__file__).parent / 'data' / 'aanbiedingen.json'
TODAY = date.today().isoformat()

def first(p, *keys):
    for k in keys:
        val=p.get(k)
        if val is not None and val != '': return val
    return None

def money(v):
    try:
        n=float(str(v).replace(',','.'))
        return round(n,2) if 0 <= n < 100000 else None
    except (TypeError,ValueError): return None

def normalise(row, retailer):
    if not isinstance(row, dict): return None
    status=first(row,'promotion_status','status')
    if status and str(status).lower() not in ('active','current'): return None
    start=first(row,'valid_from','start_date')
    end=first(row,'valid_until','end_date')
    if start and str(start)[:10] > TODAY: return None
    if end and str(end)[:10] < TODAY: return None
    name=first(row,'name','product_name','title')
    if not name: return None
    price=money(first(row,'price','promotional_price','sale_price'))
    old=money(first(row,'original_price','regular_price','price_before','was_price'))
    discount=first(row,'discount_percentage','savings_percentage')
    try: discount=float(str(discount).replace('%','').replace(',','.')) if discount is not None else None
    except ValueError: discount=None
    if discount is None and price is not None and old and old > price: discount=(old-price)/old*100
    if discount is None or discount < 25 or discount > 100 or price is None: return None
    # Geen misleidende van-prijs afleiden: alleen doorgeven wanneer expliciet beschikbaar.
    return dict(id=str(first(row,'id','product_id','ean') or f'{retailer}:{name}'),name=str(name), retailer=retailer,
                price=price,old_price=old,discount=round(discount,1),valid_from=str(start or '')[:10],
                valid_until=str(end or '')[:10],estimated_end=bool(row.get('valid_until_estimated')),
                image=first(row,'image_url','image','product_image_url'),url=first(row,'product_url','url','source_url'),
                condition=first(row,'promotion_description','promotion_type','offer_description'),
                unit=first(row,'quantity','unit','unit_label'),loyalty=bool(row.get('loyalty_price')),
                retrieved_at=first(row,'extracted_at','updated_at'))

def fetch(retailer):
    products=[]; page=1
    while True:
        qs=urllib.parse.urlencode({'retailer':retailer,'page':page,'page_size':100})
        req=urllib.request.Request(f'{BASE}?{qs}',headers={'User-Agent':'PatjesKoopjeskrant/0.1 (+https://github.com/vrolijkepatrick/Patjes-Koopjeskrant)','Accept':'application/json','X-API-Key':os.environ['PRIJSPROFEET_API_KEY']})
        with urllib.request.urlopen(req,timeout=35) as resp: data=json.load(resp)
        rows=data if isinstance(data,list) else next((data[k] for k in ('products','items','results','data','promotions') if isinstance(data.get(k),list)),None)
        if rows is None: raise ValueError(f'Onbekend API formaat voor {retailer}: {list(data)[:10]}')
        for row in rows:
            item=normalise(row, RETAILERS[retailer])
            if item: products.append(item)
        if len(rows)<100: break
        page+=1
        if page>100: raise RuntimeError('Veiligheidslimiet op paginering bereikt')
    return products

def main():
    all_items=[]; errors=[]
    for key, name in RETAILERS.items():
        try:
            items=fetch(key); print(f'{name}: {len(items)} aanbiedingen >=25%');all_items.extend(items)
        except Exception as exc:
            errors.append(f'{name}: {exc}')
    # Atomair: nooit volledige oude data wissen door een tijdelijke API-fout.
    if errors:
        raise RuntimeError('Ophalen mislukt, bestaand bestand behouden: '+ '; '.join(errors))
    # Ontdubbel op winkel en id
    unique={f"{x['retailer']}|{x['id']}":x for x in all_items}
    result={'updated_at':datetime.now(timezone.utc).isoformat(), 'minimum_discount':25,
            'covered_shops':list(RETAILERS.values()),'pending_shops':['Kruidvat','Action','Trekpleister'],
            'source':'PrijsProfeet','offers':sorted(unique.values(),key=lambda x:(-x['discount'],x['name']))}
    DEST.parent.mkdir(exist_ok=True)
    tmp=DEST.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(DEST)
    print('Geschreven:',DEST,len(unique))

if __name__=='__main__': main()
