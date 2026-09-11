from clean_eats import run_summary_flow


def run_made_active_flow(df, product_order):
    return run_summary_flow(df, product_order, 'Made Active')
