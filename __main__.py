from bitdeli import Profiles, set_theme
from collections import Counter
from itertools import chain, groupby
from datetime import datetime

NUM_WEEKS = 4

set_theme('june')

def is_active(profile):
    return True

def daily_active(profiles):
    def day(hour):
        return datetime.utcfromtimestamp(hour * 3600)
    days = Counter()
    for profile in profiles:
        if is_active(profile):
            events = chain.from_iterable(profile['events'].itervalues())
            days.update(frozenset(day(hour) for hour, freq in events))
    return days.iteritems()

def week_to_week(daily_stats):
    def weekly_counts():
        for week, stats in groupby(daily_stats, lambda day: day[0].isocalendar()[1]):
            yield week, sum(count for day, count in stats)

    def weekly_growth(weekly_stats):
        if len(weekly_stats) > 2:
            it = iter(weekly_stats[-(NUM_WEEKS + 2):-1])
            week, prev = it.next()
            for week, count in it:
                yield week, float(count - prev) / prev
                prev = count

    growth = list(weekly_growth(list(weekly_counts())))
    for week, ratio in growth:
         yield {'type': 'text',
                'label': 'week %d' % week,
                'size': (2, 1),
                'data': {'text': '%d%%' % (100 * ratio)}}
    avg = sum(ratio for week, ratio in growth) / len(growth)
    yield {'type': 'text',
           'label': 'average week-to-week growth over the past %d weeks' % len(growth),
           'size': (6, 1),
           'color': 2,
           'data': {'head': '%d%%' % (100 * avg)}}

def growth(daily):
    stats = list(sorted(daily))
    dau = {'type': 'line',
           'label': 'Daily Active Users',
           'data': [(day.isoformat(), count) for day, count in stats],
           'size': (12, 3)}
    return chain([dau], week_to_week(stats))

Profiles().map(daily_active).map(growth).show()
