"""Exact production-report output names and explicit Shopify/Zapiet aliases."""
import re
import unicodedata
from decimal import Decimal, InvalidOperation
import pandas as pd

PRODUCT_ORDER = ['Spaghetti Bolognese', 'Beef Chow Mein', "Shepherd's Pie", 'Beef Burrito Bowl', 'Beef Meatballs', 'Lebanese Beef Stew', 'Mongolian Beef', 'Chicken with Sweet Potato and Beans', 'Naked Chicken Parma', 'Chicken Pesto Pasta', 'Chicken and Broccoli Pasta', 'Butter Chicken', 'Thai Green Chicken Curry', 'Moroccan Chicken', 'Steak with Mushroom Sauce', 'Creamy Chicken & Mushroom Gnocchi', 'Roasted Lemon Chicken & Potatoes', 'Beef Lasagna', 'Lamb Souvlaki', 'Baked Family Lasagna', 'Sunday Roast Lamb', 'Smashed Burger', 'Creamy Fettuccine']
MEAL_WEIGHTS_G = {'Spaghetti Bolognese': 380, 'Beef Chow Mein': 360, "Shepherd's Pie": 360, 'Beef Burrito Bowl': 400, 'Beef Meatballs': 370, 'Lebanese Beef Stew': 350, 'Mongolian Beef': 360, 'Chicken with Sweet Potato and Beans': 320, 'Naked Chicken Parma': 350, 'Chicken Pesto Pasta': 330, 'Chicken and Broccoli Pasta': 350, 'Butter Chicken': 380, 'Thai Green Chicken Curry': 370, 'Moroccan Chicken': 320, 'Steak with Mushroom Sauce': 380, 'Creamy Chicken & Mushroom Gnocchi': 450, 'Roasted Lemon Chicken & Potatoes': 340, 'Beef Lasagna': 350, 'Lamb Souvlaki': 300, 'Baked Family Lasagna': 1500, 'Sunday Roast Lamb': 380, 'Smashed Burger': 380, 'Creamy Fettuccine': 400}

# Made Active's approved active menu from the 13 September 2026 screenshot.
# Add meals here when they launch; Clean Eats retains its full production menu.
MADE_ACTIVE_MEALS = frozenset({
    'Mongolian Beef', 'Beef Chow Mein', 'Beef Meatballs',
    'Roasted Lemon Chicken & Potatoes', 'Chicken Pesto Pasta',
    'Steak with Mushroom Sauce', 'Beef Lasagna', 'Lamb Souvlaki',
    'Thai Green Chicken Curry', 'Naked Chicken Parma', 'Butter Chicken',
    'Spaghetti Bolognese', 'Beef Burrito Bowl',
})
ACTIVE_MEALS_BY_CLIENT = {'Clean Eats': frozenset(PRODUCT_ORDER), 'Made Active': MADE_ACTIVE_MEALS}
BUNDLE_NAMES_BY_CLIENT = {
    'Clean Eats': {'FEED ME BEEF', 'Make Your Own Mega Pack'},
    'Made Active': {'Made Active Membership (14 Meals)', 'Made Active Membership (7 Meals)',
                    'Choose Your 7 Pack', '20 Pack', 'SAMPLE PACK', '30 PACK', '10 PACK'},
}
BUNDLE_REASON = 'Bundle/membership title excluded'

# Aliases resolve to canonical names before the client's active menu is checked.
# Aliases below come from the prior cleanup
# tool and the supplied barcode workbook. Unknown names are never fuzzy-matched.
ALIASES = {
    'Chicken Parma with Seasoned Potato': 'Naked Chicken Parma',
    'Beef Meatballs with Potato Mash': 'Beef Meatballs',
    'Moroccan Chicken with Chickpeas': 'Moroccan Chicken',
    'Mongolian Beef with Basmati Rice': 'Mongolian Beef',
    'Butter Chicken with Basmati Rice': 'Butter Chicken',
    'Steak with Mushroom Sauce & Mash': 'Steak with Mushroom Sauce',
    'Baked Lasagna': 'Baked Family Lasagna',
    'Sunday Lamb Roast': 'Sunday Roast Lamb',
    'Roast Lamb with Roasted Veggies': 'Sunday Roast Lamb',
    'Smashed Burger with Wedges': 'Smashed Burger',
    'Creamy Fettuccini': 'Creamy Fettuccine',
}
RETIRED_NAMES = {
    'Chicken with Vegetables', 'Chicken with Broccoli & Beans',
    'Bean Nachos with Rice', 'Chicken Fajita Bowl', 'Chicken Fajita',
    'Steak On Its Own', 'Porterhouse Steak',
    'Chicken On Its Own', 'Baked Chicken Breast',
    'Family Mac and 3 Cheese Pasta Bake', 'Mac and 3 Cheese Pasta Bake',
}


def normalized_name(value):
    if pd.isna(value):
        return ''
    value = unicodedata.normalize('NFKC', str(value)).strip().casefold()
    value = value.replace('’', "'").replace('‘', "'").replace('&', ' and ')
    return ' '.join(value.split())


NAME_LOOKUP = {normalized_name(name): name for name in PRODUCT_ORDER}
for alias, canonical in ALIASES.items():
    assert canonical in PRODUCT_ORDER
    key = normalized_name(alias)
    if key in NAME_LOOKUP and NAME_LOOKUP[key] != canonical:
        raise ValueError(f'Conflicting meal alias: {alias}')
    NAME_LOOKUP[key] = canonical
RETIRED_LOOKUP = {normalized_name(name) for name in RETIRED_NAMES}
BUNDLE_LOOKUP_BY_CLIENT = {client: {normalized_name(n) for n in names}
                           for client, names in BUNDLE_NAMES_BY_CLIENT.items()}


def product_order_for_client(client):
    if client not in ACTIVE_MEALS_BY_CLIENT:
        raise ValueError('Select Clean Eats or Made Active.')
    return [name for name in PRODUCT_ORDER if name in ACTIVE_MEALS_BY_CLIENT[client]]


def _classify_name(value):
    name = normalized_name(value)
    if name in RETIRED_LOOKUP:
        return None, 'Retired meal'
    if name in NAME_LOOKUP:
        return NAME_LOOKUP[name], 'Included'
    # Accept a label weight only when it matches the known meal size.
    # Do not silently combine a differently sized product into the same recipe.
    match = re.fullmatch(r'(.+?)\s*(?:[-–—]\s*)?(\d+(?:\.\d+)?)\s*(kg|kilograms?|g|grams?)', name)
    if match:
        base, number, unit = match.groups()
        base = base.rstrip(' -–—')
        if base in RETIRED_LOOKUP:
            return None, 'Retired meal'
        canonical = NAME_LOOKUP.get(base)
        if canonical:
            grams = Decimal(number) * (1000 if unit.startswith('k') else 1)
            if grams == MEAL_WEIGHTS_G[canonical]:
                return canonical, 'Included'
            return None, 'Weight does not match production meal'
    return None, 'Unmapped product'


def classify_product(value, client='Clean Eats'):
    product_order_for_client(client)  # Validate rather than defaulting unknown clients.
    if normalized_name(value) in BUNDLE_LOOKUP_BY_CLIENT[client]:
        return None, BUNDLE_REASON
    canonical, reason = _classify_name(value)
    if canonical is not None and canonical not in ACTIVE_MEALS_BY_CLIENT[client]:
        return None, 'Not currently active for ' + client
    return canonical, reason


def prepare_input(frame):
    frame = frame.copy()
    frame.columns = [str(c).lstrip('\ufeff').strip().casefold() for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError('The file contains duplicate column headings.')
    if not {'product name', 'quantity'}.issubset(frame.columns):
        raise ValueError("Upload a Zapiet production export containing 'Product name' and 'Quantity' columns.")
    return frame[['product name','quantity']].rename(columns={'product name':'Product name','quantity':'Quantity'})


def count(value, name):
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f'{name}: Quantity must be a non-negative whole number.') from None
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError(f'{name}: Quantity must be a non-negative whole number.')
    if number > 2**53 - 1:
        raise ValueError(f'{name}: Quantity is too large.')
    return int(number)


def clean_products(frame, client='Clean Eats'):
    product_order = product_order_for_client(client)
    frame = prepare_input(frame)
    totals = dict.fromkeys(product_order, 0)
    excluded = []
    for index, row in frame.iterrows():
        raw_name, raw_qty = row['Product name'], row['Quantity']
        if (pd.isna(raw_name) or not str(raw_name).strip()) and (pd.isna(raw_qty) or not str(raw_qty).strip()):
            continue
        name = str(raw_name).strip() if not pd.isna(raw_name) else '(missing product name)'
        qty = count(raw_qty, name)
        canonical, reason = classify_product(raw_name, client)
        if canonical is None:
            excluded.append({'Product name':name,'Quantity':qty,'Reason':reason})
        else:
            # Repeated lines are real meal units, including discounted bundle
            # contents. Sum every line; never deduplicate by name, SKU or order.
            totals[canonical] += qty
    # One row per active client meal, retaining the production report's order.
    summary = pd.DataFrame({'Product name':product_order,'Quantity':[totals[n] for n in product_order]})
    omitted = pd.DataFrame(excluded, columns=['Product name','Quantity','Reason'])
    if not omitted.empty:
        omitted = omitted.groupby(['Product name','Reason'],as_index=False)['Quantity'].sum()[['Product name','Quantity','Reason']]
    return summary, omitted
