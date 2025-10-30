
import re
import csv
from datetime import datetime

# Regex to parse a typical log line format: Timestamp [LEVEL] Message
LOG_LINE_REGEX = re.compile(r'(\b\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b)\s+(.*)')

# Keywords indicating suspicious activity
SUSPICIOUS_KEYWORDS = {
    'deauthenticated': 'Potential Deauth Attack',
    'disassociated': 'Unexpected Disconnection',
    'failed authentication': 'Failed Connection Attempt',
    'probe request': 'Network Discovery Attempt',
    'rogue ap': 'Possible Rogue Access Point'
}

def analyze_log_file(log_file_path, output_csv_path):
    """
    Parses a log file for suspicious events and writes them to a CSV.

    Args:
        log_file_path (str): Path to the log file to be analyzed.
        output_csv_path (str): Path to save the forensic CSV report.
    """
    forensic_events = []
    
    print(f"Analyzing log file: '{log_file_path}'...")

    try:
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            for line_num, line in enumerate(log_file, 1):
                line_lower = line.lower()
                
                # Check for each suspicious keyword
                for keyword, description in SUSPICIOUS_KEYWORDS.items():
                    if keyword in line_lower:
                        match = LOG_LINE_REGEX.search(line)
                        if match:
                            timestamp_str = match.group(1)
                            message = match.group(2).strip()
                            # Convert log timestamp to a more standard format
                            timestamp = datetime.strptime(timestamp_str, '%b %d %H:%M:%S').replace(year=datetime.now().year)
                            
                            forensic_events.append({
                                'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                'Line': line_num,
                                'Description': description,
                                'Log Entry': message
                            })
                        break # Move to the next line after finding one keyword
                        
    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'")
        return

    if not forensic_events:
        print("No suspicious events found in the log file.")
        return

    # Write findings to the forensic CSV log
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Timestamp', 'Line', 'Description', 'Log Entry']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(forensic_events)
        print(f"Forensic analysis complete. Report saved to '{output_csv_path}'")
    except IOError:
        print(f"Error: Could not write to CSV file at '{output_csv_path}'")


def create_sample_log(file_path):
    """Creates a sample wifi.log file for demonstration purposes."""
    log_data = """
Oct 14 10:01:15 hostapd: wlan0: STA ac:87:a3:11:22:33 IEEE 802.11: authenticated
Oct 14 10:01:20 hostapd: wlan0: STA ac:87:a3:11:22:33 IEEE 802.11: associated (aid 1)
Oct 14 10:05:00 dnsmasq-dhcp[123]: DHCPREQUEST(wlan0) 192.168.1.10 ac:87:a3:11:22:33
Oct 14 10:05:00 dnsmasq-dhcp[123]: DHCPACK(wlan0) 192.168.1.10 ac:87:a3:11:22:33 My-Laptop
Oct 14 10:15:30 hostapd: wlan0: STA bc:99:c4:44:55:66 IEEE 802.11: deauthenticated due to inactivity.
Oct 14 10:18:10 wpa_supplicant: wlan0: CTRL-EVENT-SSID-CHANGED id=0 ssid="CorporateWifi"
Oct 14 10:20:05 hostapd: wlan0: STA de:ad:be:ef:77:88 IEEE 802.11: probe request for unknown network
Oct 14 10:22:45 hostapd: wlan0: STA 12:34:56:78:90:ab IEEE 802.11: disassociated
Oct 14 10:25:01 kernel: [ 123.456] wlan0: authentication with 00:11:22:33:44:55 timed out.
Oct 14 10:25:15 hostapd: wlan0: STA 54:45:65:76:87:98 had failed authentication.
Oct 14 10:30:00IDS: Alert! Possible rogue AP detected with BSSID 02:00:00:00:00:01 on channel 6.
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(log_data.strip())
    print(f"Created sample log file at '{file_path}'")


def main():
    """
    Main function to run the Wi-Fi log monitor.
    """
    log_file = "./wifi.log"
    forensic_report_file = "./forensic_log_analysis.csv"
    
    # Create a sample log file for the script to run
    create_sample_log(log_file)
    
    # Analyze the created log file
    analyze_log_file(log_file, forensic_report_file)


if __name__ == "__main__":
    main()
