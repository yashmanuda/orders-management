import calendar
import datetime
import json
import sys

AM = "AM"
ENTITIES = "entities"
ORDER = "ORDER"
ORDER_DATE = "orderDate"
TOTAL_COST = "totalCost"
DISH = "dishString"
RES_INFO = "resInfo"
RATING = "rating"
RATING_TEXT = "rating_text"
ESTABLISHMENT = "establishment"
NON_VEG = "Non-Veg"
VEG = "Veg"
DINNER = "Dinner"
LUNCH = "Lunch"
BREAKFAST = "Breakfast"
SNACKS = "Snacks"
NON_VEG_DISHES = {"chicken", "fish", "mutton", "egg"}
ORDER_IDS = set()


def find_day(date: str) -> str:
    day = datetime.datetime.strptime(date, '%B %d, %Y').weekday()
    return calendar.day_name[day]


def veg_or_non_veg(dish: str) -> str:
    for non_veg_dish in NON_VEG_DISHES:
        if non_veg_dish in dish.lower():
            return NON_VEG
    return VEG


def get_day_time(date: str) -> str:
    hour = float(date.split(" ")[4].split(":")[0])
    is_am = date.split(" ")[5] == AM
    if is_am:
        if hour > 5.0:
            return BREAKFAST
        return DINNER
    if hour > 6.0:
        return DINNER
    if hour > 3.0:
        return SNACKS

    return LUNCH


def parse_line(line):
    parsed_lines = []
    for order_id, details in line[ENTITIES][ORDER].items():
        if order_id in ORDER_IDS:
            continue
        ORDER_IDS.add(order_id)
        dish = str(details[DISH]).strip()
        date = str(details[ORDER_DATE]).strip()
        year = date.split(" ")[2].strip()
        month = date.split(" ")[0].strip()
        cost = str(float(str(details[TOTAL_COST][1:]).replace(",", "")))
        rating = get_rating(details)
        establishment = get_establishment(details)
        day_time = get_day_time(date)
        day = find_day(str(date.split("at")[0]).strip())
        veg_non_veg = veg_or_non_veg(dish)
        parsed_lines.append(
            [order_id, dish, date, day, month, year, cost, rating, establishment, day_time, veg_non_veg])
    return parsed_lines


def get_rating(details) -> str:
    try:
        return str(float(details[RES_INFO][RATING][RATING_TEXT]))
    except Exception as e:
        print(e)
        return "0.0"


def get_establishment(details) -> str:
    establishment = details[RES_INFO][ESTABLISHMENT]
    if not establishment:
        establishment = "NA"
    else:
        establishment = establishment[0]
    return establishment


def generate_zomato_details(input_file_path: str, output_file_path: str):
    input_file = open(input_file_path)
    output_file = open(output_file_path, "w+")
    output_file.write(
        "Order ID" + "\t" + "Dish" + "\t" + "Date" + "\t" + "Day" + "\t" + "Month" + "\t" + "Year" + "\t" +
        "Price" + "\t" + "Rating" + "\t" + "Restaurant" + "\t" + "Meal" + "\t" + "Meal Type" + "\n")
    for line in input_file:
        try:
            parsed_line = parse_line(json.loads(line))
            write_to_file(output_file, parsed_line)
        except Exception as e:
            print(e)
            print(line)
    input_file.close()
    output_file.close()


def write_to_file(output_file, parsed_lines):
    for parsed_line in parsed_lines:
        output_file.write("\t".join(parsed_line) + "\n")


if __name__ == "__main__":
    file_path = sys.argv[1]
    output_path = sys.argv[2]
    generate_zomato_details(file_path, output_path)
