import lzma
import json
import urllib.request
import ssl
from datetime import datetime

def format_date(d_str):
    try:
        return datetime.strptime(d_str, "%Y%m%d").strftime("%Y-%m-%d")
    except Exception:
        return d_str

def main():
    url = "https://www.netmeister.org/tldstats/all-tlds.json.xz"
    print("Downloading and decompressing TLD data...")
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, context=context) as r:
            compressed_data = r.read()
        print(f"Downloaded {len(compressed_data)} bytes.")
        
        json_data = json.loads(lzma.decompress(compressed_data).decode('utf-8'))
        print("Data loaded successfully.")
        
        tlds = json_data['tlds']
        
        # Process each TLD to get its latest entry
        processed_tlds = []
        for tld, history in tlds.items():
            if not history:
                continue
            # Find the latest date for this specific TLD
            latest_date = max(history.keys())
            try:
                count = int(history[latest_date])
            except ValueError:
                count = 0
            processed_tlds.append({
                'tld': tld,
                'count': count,
                'date': latest_date
            })
            
        # Sort by count descending, then TLD name ascending
        processed_tlds.sort(key=lambda x: (-x['count'], x['tld']))
        
        total_history = json_data.get('total', {})
        overall_latest_date = json_data.get('date', '')
        if not overall_latest_date and total_history:
            overall_latest_date = max(total_history.keys())
        if not overall_latest_date:
            overall_latest_date = '20260705'
            
        sum_calculated = sum(t['count'] for t in processed_tlds)
        
        # Write to README.md
        readme_filename = "README.md"
        print(f"Writing to {readme_filename}...")
        with open(readme_filename, "w", encoding="utf-8") as f:
            f.write("# TLD Stats\n\n")
            f.write("A project containing domain registration statistics across all Top-Level Domains (TLDs) derived from the [netmeister.org](https://netmeister.org) TLD dataset.\n")
            f.write("Data sourced from [netmeister.org TLD statistics](https://www.netmeister.org/tldstats/).\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"- **Data Date:** {format_date(overall_latest_date)}\n")
            f.write(f"- **Total Registered Domains (Sum of TLDs):** {sum_calculated:,}\n")
            f.write(f"- **Total TLDs Tracked:** {len(processed_tlds):,}\n\n")
            
            f.write("\n## TLDs by Domain Count\n\n")
            f.write("| Rank | TLD | Domain Count | Latest Date | % of Total |\n")
            f.write("|---:|:---|---:|:---|---:|\n")
            
            for rank, item in enumerate(processed_tlds, 1):
                tld_name = item['tld']
                count_val = item['count']
                date_val = format_date(item['date'])
                pct = (count_val / sum_calculated * 100) if sum_calculated > 0 else 0
                
                count_str = f"{count_val:,}"
                pct_str = f"{pct:.4f}%" if pct >= 0.0001 else "<0.0001%"
                if count_val == 0:
                    pct_str = "0.0000%"
                    
                f.write(f"| {rank} | .{tld_name} | {count_str} | {date_val} | {pct_str} |\n")
            
            f.write("\n---\n\n*Built with ❤️ for the community. Maintained by [Khan Sunny](https://github.com/i). Automatically updated daily via GitHub Actions.*\n")

        print("Completed generation of README.md successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
