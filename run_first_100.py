#!/usr/bin/env python3
import time
import ast
import pandas as pd
from scripts import screenshot_links as s

LOG_INTERVAL = 10

if __name__ == '__main__':
    print('STARTING first 100 rows run')
    start = time.time()
    df = pd.read_excel('db/Interior_Inspiration_Database.xlsx')
    count = 0
    total = min(100, len(df))
    for idx, row in df.iterrows():
        if count >= 100:
            break
        raw = row.get('links', '')
        try:
            parsed = ast.literal_eval(raw)
            url = parsed[0] if parsed else None
        except Exception:
            url = raw
        if not url or str(url).strip() == '':
            continue
        count += 1
        print(f'[{count:03d}/{total:03d}] Capturing: {url}')
        try:
            shots = s.determine_shots_for_url(url, default=1)
            out = s.capture_screenshots(url, s.hash_url(url), shots=shots)
            print('   Saved:', out)
        except Exception as e:
            print('   Failed:', repr(e))
        if count % LOG_INTERVAL == 0:
            print(f'Processed {count} rows so far...')
        # polite small sleep
        time.sleep(0.2)
    print('DONE - processed', count, 'rows in', time.time() - start, 'seconds')
