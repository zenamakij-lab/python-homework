seconds = int(input())

DAY = 24 * 60 * 60
HOUR = 60 * 60
MINUTE = 60

days, seconds = divmod(seconds, DAY)
hours, seconds = divmod(seconds, HOUR)
minutes, seconds = divmod(seconds, MINUTE)


if days % 10 == 1 and days % 100 != 11:
    day_word = "day"
elif 2 <= days % 10 <= 4 and not (12 <= days % 100 <= 14):
    day_word = "days"
else:
    day_word = "dayss"

print(f"{days} {day_word}, {str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")
