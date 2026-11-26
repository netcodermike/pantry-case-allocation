def int_field(data, key, maximum=1_000_000):
    value = data[key]
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{key} must be a whole number from 0 through {maximum}")
    return value


def analyze(data):
    stock = int_field(data, "stock_cases")
    reserve = int_field(data, "reserve_cases", stock)
    raw = data["sites"]
    if not isinstance(raw, list) or not 1 <= len(raw) <= 1000:
        raise ValueError("enter 1 through 1000 partner sites")
    sites = {}
    for site in raw:
        name = site["name"]
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise ValueError("site names must be nonempty labels of at most 80 characters")
        name = name.strip()
        key = name.casefold()
        if key in sites:
            raise ValueError("site names must be unique")
        requested = int_field(site, "requested_cases")
        capacity = int_field(site, "capacity_cases")
        sites[key] = (name, requested, capacity)

    ordered = [site for _, site in sorted(sites.items())]
    caps = [min(requested, capacity) for _, requested, capacity in ordered]
    budget = min(stock - reserve, sum(caps))

    # Find the largest uniform share that fits after capping every site.
    low, high = 0, max(caps) + 1
    while high - low > 1:
        middle = (low + high) // 2
        if sum(min(cap, middle) for cap in caps) <= budget:
            low = middle
        else:
            high = middle
    shares = [min(cap, low) for cap in caps]
    remaining = budget - sum(shares)

    allocation = []
    for (name, requested, capacity), share, cap in zip(ordered, shares, caps):
        if remaining and share < cap:
            share += 1
            remaining -= 1
        allocation.append({"site": name, "requested_cases": requested, "capacity_cases": capacity,
                           "allocated_cases": share, "unfilled_cases": requested - share})
    return {"stock_cases": stock, "reserved_cases": reserve, "distributed_cases": budget,
            "unassigned_cases_after_reserve": stock - reserve - budget, "allocation": allocation}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
