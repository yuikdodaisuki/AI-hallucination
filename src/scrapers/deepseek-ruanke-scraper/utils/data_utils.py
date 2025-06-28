import csv
import json
from pathlib import Path  # 添加这行导入
from models.venue import Venue


def is_duplicate_venue(venue_name: str, seen_names: set) -> bool:
    return venue_name in seen_names


def is_complete_venue(venue: dict, required_keys: list) -> bool:
    return all(key in venue for key in required_keys)


def save_venues_to_csv(venues: list, filename: str):
    if not venues:
        print("No venues to save.")
        return

    # Use field names from the Venue model
    fieldnames = Venue.model_fields.keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(venues)
    print(f"Saved {len(venues)} venues to '{filename}'.")

def save_venues_to_json(venues: list, filename: str):
    """保存场馆数据到JSON文件"""
    if not venues:
        print("No venues to save.")
        return

    # 确保文件扩展名为.json
    json_filename = Path(filename).with_suffix('.json')
    
    with open(json_filename, mode="w", encoding="utf-8") as file:
        json.dump(venues, file, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(venues)} venues to '{json_filename}'.")

def save_venues_to_both_formats(venues: list, base_filename: str):
    """同时保存为CSV和JSON格式"""
    # 保存CSV
    csv_filename = Path(base_filename).with_suffix('.csv')
    save_venues_to_csv(venues, str(csv_filename))
    
    # 保存JSON
    json_filename = Path(base_filename).with_suffix('.json')
    save_venues_to_json(venues, str(json_filename))
