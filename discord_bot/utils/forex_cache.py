from datetime import datetime, timedelta

class ForexEventCache:
    def __init__(self, cache_ttl=3600):  # 1 hour TTL by default
        self._cache = {}
        self._cache_ttl = cache_ttl
        self._last_scrape = None
        self._monthly_events = {
            'previous_month': {},
            'current_month': {},
            'next_month': {}
        }

    def get(self, key):
        """Get cached data if it exists and is not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return data
            else:
                del self._cache[key]
        return None

    def set(self, key, data):
        """Set data in cache with current timestamp"""
        self._cache[key] = (data, datetime.now())

    def get_last_scrape_time(self):
        """Get the last scrape time"""
        return self._last_scrape

    def set_last_scrape_time(self, time):
        """Set the last scrape time"""
        self._last_scrape = time

    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self._monthly_events = {
            'previous_month': {},
            'current_month': {},
            'next_month': {}
        }
        self._last_scrape = None

    def store_month(self, month_key, events):
        """Store events for a specific month"""
        self._monthly_events[month_key] = events

    def get_month(self, month_key):
        """Get events for a specific month"""
        return self._monthly_events.get(month_key, {})

    def get_events_for_date(self, date_str):
        """Get events for a specific date by checking all months"""
        for month_events in self._monthly_events.values():
            if date_str in month_events:
                return month_events[date_str]
        return []

    def get_events_in_range(self, start_date, end_date, currency=None, importance=None):
        """Get events between two dates with optional filters"""
        events = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_events = self.get_events_for_date(date_str)
            
            # Apply filters
            if currency:
                day_events = [e for e in day_events if e['currency'] == currency]
            if importance:
                day_events = [e for e in day_events if e['importance'] in importance]
            
            if day_events:  # Only add dates that have events
                events[date_str] = day_events
            
            current_date += timedelta(days=1)
        
        return events